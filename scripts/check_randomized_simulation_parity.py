#!/usr/bin/env python3
"""Stress seeded Python/Rust simulation parity on generated systems."""

import json
import math
import random
import subprocess
import tempfile
from pathlib import Path

from check_randomized_runtime_parity import MODELS, SEED, make_system
from ronin.parser import parse
from ronin.simulator import simulate

ROOT = Path(__file__).resolve().parents[1]
CASES_PER_MODEL = 3
STEPS = 24


def rust_simulate(path, name, seed):
    args = [
        "cargo", "run", "--quiet", "--manifest-path",
        str(ROOT / "rust" / "Cargo.toml"), "--", "simulate", str(path),
        "--system", name, "--steps", str(STEPS), "--seed", str(seed),
    ]
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def assert_close(left, right, label):
    if not math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-12):
        raise AssertionError(f"{label}: Python={left!r}, Rust={right!r}")


def main():
    rng = random.Random(SEED + 9000)
    source_parts = []
    names = []
    index = 0
    for model in MODELS:
        for _ in range(CASES_PER_MODEL):
            index += 1
            names.append(f"Random{index:03d}")
            source_parts.append(make_system(rng, index, model))

    temporary = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".ronin", prefix=".random-sim-",
        dir=ROOT, delete=False,
    )
    path = Path(temporary.name)
    try:
        with temporary:
            temporary.write("\n".join(source_parts))
        systems = parse(path.read_text(encoding="utf-8"))
        for index, name in enumerate(names):
            seed = SEED + index
            system = systems[name]
            py = simulate(system, steps=STEPS, seed=seed)
            result = rust_simulate(path, name, seed)
            if result.returncode:
                raise AssertionError(f"{name}: Rust rejected generated simulation: {result.stderr}")
            rs = json.loads(result.stdout)

            if rs["steps"] != py.steps or rs["seed"] != py.seed:
                raise AssertionError(f"{name}: steps or seed differ")
            if rs["extinction_events"] != py.extinction_events:
                raise AssertionError(f"{name}: extinction events differ")
            assert_close(rs["survivability"], py.survivability, f"{name}.survivability")
            if len(rs["history"]) != STEPS + 1 or len(py.history) != STEPS + 1:
                raise AssertionError(f"{name}: history length differs")

            for step, (py_state, rs_state) in enumerate(zip(py.history, rs["history"])):
                if len(py_state) != len(rs_state):
                    raise AssertionError(f"{name}: state dimension differs at step {step}")
                for agent, (left, right) in enumerate(zip(py_state, rs_state)):
                    assert_close(left, right, f"{name}.history[{step}][{agent}]")
                if any(not math.isfinite(value) or value < 0.0 for value in rs_state):
                    raise AssertionError(f"{name}: Rust left the probability simplex")
                if not math.isclose(math.fsum(rs_state), 1.0, rel_tol=0.0, abs_tol=1e-9):
                    raise AssertionError(f"{name}: Rust state does not sum to one")

            for left, right in zip(py.final_state, rs["final_state"]):
                assert_close(left, right, f"{name}.final_state")
            print(f"random simulation parity OK: {name} ({system.params.model})")
    finally:
        path.unlink(missing_ok=True)

    print(
        f"Randomized simulation parity OK: {len(names)} systems, "
        f"{STEPS} steps each, deterministic seeds starting at {SEED}"
    )


if __name__ == "__main__":
    main()
