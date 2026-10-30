#!/usr/bin/env python3
"""Compare Python and Rust diagnostic reports on shared RONIN projects."""

import json
import math
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from ronin.diagnose import diagnose
from ronin.errors import SemanticError
from ronin.parser import parse

ROOT = Path(__file__).resolve().parents[1]
VALID = [
    ROOT / "examples" / "degeneracy_active.ronin",
    ROOT / "examples" / "degeneracy_inactive.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "degeneracy_active.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "degeneracy_inactive.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "degeneracy_unknown.ronin",
]


def rust_diagnose(path: Path, name: str, bootstrap: int = 0):
    return subprocess.run(
        [
            "cargo", "run", "--quiet", "--manifest-path",
            str(ROOT / "rust" / "Cargo.toml"), "--",
            "diagnose", str(path), "--system", name, "--bootstrap", str(bootstrap),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def compare(path: Path, bootstrap: int = 0):
    systems = parse(path.read_text(encoding="utf-8"))
    for name, system in systems.items():
        expected = asdict(diagnose(system, bootstrap=bootstrap))
        result = rust_diagnose(path, name, bootstrap)
        if result.returncode != 0:
            raise AssertionError(
                f"Rust rejected diagnostic fixture {path.relative_to(ROOT)}:\n{result.stderr}"
            )
        actual = json.loads(result.stdout)
        for field in (
            "degeneracy",
            "lambda_identifiable",
            "K_identifiable",
            "alpha_h_identifiable",
            "recommendation",
            "bootstrap_ci",
        ):
            if actual.get(field) != expected[field]:
                raise AssertionError(
                    f"{path}: {name}.{field}: Python={expected[field]!r}, Rust={actual.get(field)!r}"
                )
        if not math.isclose(
            actual["omega_range_orders"],
            expected["omega_range_orders"],
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            raise AssertionError(
                f"{path}: {name}.omega_range_orders differs: "
                f"Python={expected['omega_range_orders']}, Rust={actual['omega_range_orders']}"
            )
        print(f"diagnostic parity OK: {path.relative_to(ROOT)} / {name} / bootstrap={bootstrap}")


def main() -> int:
    for path in VALID:
        compare(path)
    # Bootstrap is accepted by both interfaces, but its CI remains explicitly null.
    compare(ROOT / "tests" / "fixtures" / "conformance" / "degeneracy_active.ronin", bootstrap=20)

    invalid = ROOT / "tests" / "fixtures" / "conformance" / "invalid_frequency_sum.ronin"
    system = next(iter(parse(invalid.read_text(encoding="utf-8")).values()))
    try:
        diagnose(system)
    except SemanticError:
        pass
    else:
        print("Python unexpectedly diagnosed invalid system", file=sys.stderr)
        return 1
    rust = rust_diagnose(invalid, system.name)
    if rust.returncode == 0:
        print("Rust unexpectedly diagnosed invalid system", file=sys.stderr)
        return 1

    negative_bootstrap = rust_diagnose(
        ROOT / "tests" / "fixtures" / "conformance" / "degeneracy_active.ronin",
        "DegeneracyActive",
        bootstrap=-1,
    )
    if negative_bootstrap.returncode == 0:
        print("Rust unexpectedly accepted negative bootstrap count", file=sys.stderr)
        return 1
    print("diagnostic rejection parity OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
