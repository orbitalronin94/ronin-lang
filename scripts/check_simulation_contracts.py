#!/usr/bin/env python3
"""Compare seeded Python/Rust simulation trajectories and shared invariants."""

import json
import math
import subprocess
import sys
from pathlib import Path

from ronin.parser import parse

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
    ROOT / "tests" / "fixtures" / "conformance" / "valid_zero_fitness_check_only.ronin",
]
STEPS = 12
SEED = 73


def run_python(path):
    return subprocess.run(
        [sys.executable, "-m", "ronin.cli", "simulate", str(path),
         "--steps", str(STEPS), "--seed", str(SEED)],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )


def run_rust(path):
    return subprocess.run(
        ["cargo", "run", "--quiet", "--manifest-path", str(ROOT / "rust" / "Cargo.toml"),
         "--", "simulate", str(path), "--steps", str(STEPS), "--seed", str(SEED)],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )


def validate(result, expected_initial, path, backend):
    if result.returncode != 0:
        raise AssertionError(
            f"{backend} rejected {path.relative_to(ROOT)}:\n{result.stderr}"
        )
    payload = json.loads(result.stdout)
    required = {
        "history", "final_state", "steps", "seed",
        "extinction_events", "survivability",
    }
    if not required.issubset(payload):
        raise AssertionError(f"{backend} missing simulation fields for {path}")
    if payload["steps"] != STEPS or payload["seed"] != SEED:
        raise AssertionError(f"{backend} did not preserve steps/seed for {path}")
    history = payload["history"]
    dimension = len(expected_initial)
    if len(history) != STEPS + 1:
        raise AssertionError(f"{backend} history length mismatch for {path}")
    for step, state in enumerate(history):
        if len(state) != dimension:
            raise AssertionError(f"{backend} state dimension mismatch at step {step}: {path}")
        if any(not math.isfinite(value) or value < 0.0 for value in state):
            raise AssertionError(f"{backend} emitted invalid simplex coordinate: {path}")
        if not math.isclose(sum(state), 1.0, rel_tol=0.0, abs_tol=1e-9):
            raise AssertionError(f"{backend} state left simplex at step {step}: {path}")
    for left, right in zip(history[0], expected_initial):
        if not math.isclose(left, right, rel_tol=0.0, abs_tol=1e-12):
            raise AssertionError(f"{backend} initial state differs from project frequencies: {path}")
    for left, right in zip(payload["final_state"], history[-1]):
        if not math.isclose(left, right, rel_tol=0.0, abs_tol=1e-12):
            raise AssertionError(f"{backend} final_state differs from final history: {path}")
    events = payload["extinction_events"]
    if len(events) != len(set(events)) or any(not 0 <= i < dimension for i in events):
        raise AssertionError(f"{backend} emitted invalid extinction indices: {path}")
    expected_survivability = sum(value > 1e-12 for value in payload["final_state"]) / dimension
    if not math.isclose(payload["survivability"], expected_survivability, abs_tol=1e-12):
        raise AssertionError(f"{backend} survivability mismatch: {path}")
    return payload


def main():
    for path in VALID:
        systems = parse(path.read_text(encoding="utf-8"))
        system = next(iter(systems.values()))
        initial = [agent.frequency for agent in system.agents]
        py = validate(run_python(path), initial, path, "Python")
        rs = validate(run_rust(path), initial, path, "Rust")
        if len(py["history"]) != len(rs["history"]):
            raise AssertionError(f"simulation contract length differs: {path}")
        for step, (py_state, rs_state) in enumerate(zip(py["history"], rs["history"])):
            for index, (left, right) in enumerate(zip(py_state, rs_state)):
                if not math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-12):
                    raise AssertionError(
                        f"seeded trajectory mismatch at {path.name}, step {step}, "
                        f"agent {index}: Python={left!r}, Rust={right!r}"
                    )
        print(f"simulation invariants OK: {path.relative_to(ROOT)}")
    print("Seeded Python/Rust trajectories match within 1e-12.")


if __name__ == "__main__":
    raise SystemExit(main())
