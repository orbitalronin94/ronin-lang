#!/usr/bin/env python3
"""Deterministic randomized Python/Rust solver parity over the shared profile."""

import json
import math
import random
import subprocess
import tempfile
from dataclasses import asdict
from pathlib import Path

from ronin.errors import SemanticError
from ronin.parser import parse
from ronin.solver import solve

ROOT = Path(__file__).resolve().parents[1]
SEED = 1310
CASES_PER_MODEL = 16
MODELS = ("pusfre", "ces", "hill", "ces_hill", "full")
NUMERIC_FIELDS = ("lambda_used", "alpha_h_used", "omega_range", "k_min")


def number(value):
    return format(value, ".17g")


def make_system(rng, index, model):
    count = rng.randint(2, 8)
    raw = [10.0 ** rng.uniform(-300.0, 0.0) for _ in range(count)]
    total = math.fsum(raw)
    frequencies = [value / total for value in raw]
    # Correct the largest component so the serialized vector sums to one
    # without erasing very small positive frequencies.
    largest = max(range(count), key=frequencies.__getitem__)
    frequencies[largest] = 1.0 - math.fsum(
        value for position, value in enumerate(frequencies) if position != largest
    )

    agents = []
    for phi, psi, frequency in zip(
        (rng.uniform(0.05, 1.0) for _ in range(count)),
        (rng.uniform(0.05, 1.0) for _ in range(count)),
        frequencies,
    ):
        agents.append(
            "    { phi: %s, psi: %s, frequency: %s }"
            % (number(phi), number(psi), number(frequency))
        )

    params = {
        "alpha": rng.uniform(0.5, 2.5),
        "gamma": rng.uniform(0.0, 1.0),
        "sigma": rng.uniform(0.0, 0.5),
        "coexistence_delta": rng.uniform(0.005, 0.1),
        "model": model,
        "lambda": 0.0 if model in ("pusfre", "hill") else rng.choice(
            (-0.9, -0.5, -0.1, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0)
        ),
        "alpha_h": rng.choice((1.0, 0.25, 0.5, 1.5, 2.0, 5.0, 10.0)),
    }
    if model in ("hill", "ces_hill", "full"):
        params["K"] = 10.0 ** rng.uniform(-300.0, 0.0)
    if model == "full":
        params["memory_order"] = 1

    param_lines = [
        "    %s: %s" % (key, value if isinstance(value, str) else number(value))
        for key, value in params.items()
    ]
    resource = 10.0 ** rng.uniform(-200.0, 200.0)
    return (
        "system Random%03d = {\n" % index
        + "  parts: %d,\n" % count
        + "  resource: %s,\n" % number(resource)
        + "  agents: [\n"
        + ",\n".join(agents)
        + "\n  ],\n"
        + "  params: {\n"
        + ",\n".join(param_lines)
        + "\n  }\n"
        + "}\n"
    )


def rust_run(path):
    args = [
        "cargo", "run", "--quiet", "--manifest-path",
        str(ROOT / "rust" / "Cargo.toml"), "--", "run", str(path),
    ]
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def close(left, right, label, case):
    if left is None or right is None:
        if left is not right:
            raise AssertionError(f"{case}: {label}: Python={left!r}, Rust={right!r}")
        return
    if not math.isclose(float(left), float(right), rel_tol=2e-9, abs_tol=1e-12):
        raise AssertionError(f"{case}: {label}: Python={left!r}, Rust={right!r}")


def compare_source(source, label):
    systems = parse(source)
    expected = {name: asdict(solve(system)) for name, system in systems.items()}
    temporary = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".ronin", prefix=".random-parity-",
        dir=ROOT, delete=False,
    )
    path = Path(temporary.name)
    try:
        with temporary:
            temporary.write(source)
        result = rust_run(path)
        if result.returncode:
            raise AssertionError(f"{label}: Rust rejected generated valid input:\n{result.stderr}")
        actual = json.loads(result.stdout)
        if set(actual) != set(expected):
            raise AssertionError(f"{label}: system names differ")
        for name, py in expected.items():
            rs = actual[name]
            if any(not math.isfinite(value) or value < 0.0 for value in py["fitness"]):
                raise AssertionError(f"{label}/{name}: Python produced invalid fitness")
            if any(not math.isfinite(value) or value < 0.0 for value in py["allocation"]):
                raise AssertionError(f"{label}/{name}: Python produced invalid allocation")
            resource = systems[name].resource
            if not math.isclose(math.fsum(py["allocation"]), resource, rel_tol=2e-9, abs_tol=0.0):
                raise AssertionError(f"{label}/{name}: allocation does not conserve resource")
            for field in ("fitness", "allocation"):
                if len(py[field]) != len(rs[field]):
                    raise AssertionError(f"{label}/{name}: {field} length differs")
                for position, (left, right) in enumerate(zip(py[field], rs[field])):
                    close(left, right, f"{name}.{field}[{position}]", label)
            for field in ("coexistence", "degeneracy", "model_used", "debt"):
                if py[field] != rs[field]:
                    raise AssertionError(
                        f"{label}/{name}.{field}: Python={py[field]!r}, Rust={rs[field]!r}"
                    )
            for field in NUMERIC_FIELDS:
                close(py[field], rs[field], f"{name}.{field}", label)
            expected_k = py["K_used"]
            actual_k = rs["K_used"]
            if math.isinf(expected_k):
                if actual_k != "inf":
                    raise AssertionError(f"{label}/{name}.K_used: expected inf, got {actual_k!r}")
            else:
                close(expected_k, actual_k, f"{name}.K_used", label)
    finally:
        path.unlink(missing_ok=True)


def compare_expected_rejection(source, label, expected_message):
    systems = parse(source)
    for system in systems.values():
        try:
            solve(system)
        except SemanticError as error:
            if expected_message not in str(error):
                raise AssertionError(f"{label}: unexpected Python rejection: {error}")
        else:
            raise AssertionError(f"{label}: Python unexpectedly accepted the degenerate system")

    temporary = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".ronin", prefix=".random-rejection-",
        dir=ROOT, delete=False,
    )
    path = Path(temporary.name)
    try:
        with temporary:
            temporary.write(source)
        result = rust_run(path)
        if result.returncode == 0 or expected_message not in result.stderr:
            raise AssertionError(
                f"{label}: Rust did not reject the same degenerate system: {result.stderr}"
            )
    finally:
        path.unlink(missing_ok=True)


def main():
    rng = random.Random(SEED)
    cases = []
    index = 0
    for model in MODELS:
        for _ in range(CASES_PER_MODEL):
            index += 1
            cases.append(make_system(rng, index, model))
    compare_source("\n".join(cases), f"seed={SEED}, cases={len(cases)}")

    # A valid but numerically degenerate Hill system must fail consistently
    # instead of dividing by a zero total fitness in either runtime.
    degenerate = """system HillUnderflow = {
  parts: 2,
  resource: 1,
  agents: [
    { phi: 1, psi: 1, frequency: 0.5 },
    { phi: 1, psi: 1, frequency: 0.5 }
  ],
  params: { model: "hill", K: 1e300, alpha_h: 10, alpha: 1 }
}
"""
    compare_expected_rejection(
        degenerate, "Hill underflow rejection", "allocation undefined: zero total fitness"
    )
    print(
        "Randomized Python/Rust solver parity OK: "
        f"{len(cases)} deterministic systems, seed={SEED}, models={','.join(MODELS)}, "
        "plus a matched degenerate-system rejection"
    )


if __name__ == "__main__":
    main()
