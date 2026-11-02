#!/usr/bin/env python3
"""Compare Python and Rust numerical results on shared RONIN projects."""

import json
import math
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from ronin.errors import SemanticError
from ronin.parser import parse
from ronin.solver import solve

ROOT = Path(__file__).resolve().parents[1]
VALID = [
    ROOT / "examples" / "maquinas.ronin",
    ROOT / "examples" / "maquinas_ces.ronin",
    ROOT / "examples" / "pesca.ronin",
    ROOT / "examples" / "degeneracy_active.ronin",
    ROOT / "examples" / "degeneracy_inactive.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "pusfre.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "ces.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "hill.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "ces_hill.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "full_order1.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "metadata_nested.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "degeneracy_unknown.ronin",
]
INVALID = [
    ROOT / "tests" / "fixtures" / "conformance" / "invalid_frequency_sum.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "invalid_pusfre_lambda.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "invalid_alpha.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "full_order3_unsupported.ronin",
]
NUMERIC_FIELDS = ("lambda_used", "alpha_h_used", "omega_range", "k_min")


def rust_run(path: Path, delta=None) -> subprocess.CompletedProcess:
    args = [
        "cargo", "run", "--quiet", "--manifest-path",
        str(ROOT / "rust" / "Cargo.toml"), "--", "run", str(path),
    ]
    if delta is not None:
        args.extend(["--delta", str(delta)])
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def close(left, right, label, path):
    if left is None or right is None:
        if left is not right:
            raise AssertionError(f"{path}: {label}: Python={left!r}, Rust={right!r}")
        return
    if not math.isclose(float(left), float(right), rel_tol=1e-9, abs_tol=1e-9):
        raise AssertionError(f"{path}: {label}: Python={left!r}, Rust={right!r}")


def compare(path: Path, delta=None) -> None:
    systems = parse(path.read_text(encoding="utf-8"))
    expected = {name: asdict(solve(system, delta=delta)) for name, system in systems.items()}
    result = rust_run(path, delta)
    if result.returncode != 0:
        raise AssertionError(
            f"Rust rejected valid project {path.relative_to(ROOT)}:\n{result.stderr}"
        )
    actual = json.loads(result.stdout)
    if set(actual) != set(expected):
        raise AssertionError(
            f"{path}: system names differ: Python={list(expected)}, Rust={list(actual)}"
        )

    for name, python_result in expected.items():
        rust_result = actual[name]
        for field in ("allocation", "fitness"):
            if len(python_result[field]) != len(rust_result[field]):
                raise AssertionError(f"{path}: {name}.{field} length differs")
            for index, (left, right) in enumerate(zip(python_result[field], rust_result[field])):
                close(left, right, f"{name}.{field}[{index}]", path)
        for field in ("coexistence", "degeneracy", "model_used", "debt"):
            if python_result[field] != rust_result[field]:
                raise AssertionError(
                    f"{path}: {name}.{field}: Python={python_result[field]!r}, Rust={rust_result[field]!r}"
                )
        for field in NUMERIC_FIELDS:
            close(python_result[field], rust_result[field], f"{name}.{field}", path)
        expected_k = python_result["K_used"]
        actual_k = rust_result["K_used"]
        if math.isinf(expected_k):
            if actual_k != "inf":
                raise AssertionError(f"{path}: {name}.K_used: expected 'inf', got {actual_k!r}")
        else:
            close(expected_k, actual_k, f"{name}.K_used", path)
    print(f"solver parity OK: {path.relative_to(ROOT)}")


def main() -> int:
    for path in VALID:
        compare(path)
    # Explicit override must replace the project's coexistence_delta in both CLIs.
    compare(ROOT / "tests" / "fixtures" / "conformance" / "pusfre.ronin", delta=0.07)

    invalid_deltas = (0.0, -0.01, 0.1001, float("inf"), float("nan"))
    for invalid_delta in invalid_deltas:
        path = ROOT / "tests" / "fixtures" / "conformance" / "pusfre.ronin"
        system = next(iter(parse(path.read_text(encoding="utf-8")).values()))
        try:
            solve(system, delta=invalid_delta)
        except SemanticError as error:
            if "delta must be in (0,0.1]" not in str(error):
                raise AssertionError(f"unexpected Python delta error: {error}")
        else:
            raise AssertionError(f"Python accepted invalid delta {invalid_delta!r}")
        result = rust_run(path, invalid_delta)
        if result.returncode == 0 or "delta must be in (0,0.1]" not in result.stderr:
            raise AssertionError(
                f"Rust did not reject invalid delta {invalid_delta!r}: {result.stderr}"
            )

    for path in INVALID:
        systems = parse(path.read_text(encoding="utf-8"))
        try:
            for system in systems.values():
                solve(system)
        except SemanticError:
            pass
        else:
            print(f"Python unexpectedly accepted {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        result = rust_run(path)
        if result.returncode == 0:
            print(f"Rust unexpectedly accepted {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"runtime rejection parity OK: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
