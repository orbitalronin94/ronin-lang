#!/usr/bin/env python3
"""Compare the Python and Rust local Hill design diagnostics."""

import json
import math
import subprocess
from pathlib import Path

from ronin.identifiability import diagnose_hill_design

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ([10 ** (-2 + index * 0.1) for index in range(41)], 1.0, 1.5, 0.05),
    ([0.001, 0.002, 0.004, 0.008], 1.0, 1.5, 0.05),
    ([0.5], 1.0, 1.5, 0.05),
    ([0.01, 0.1, 1.0, 10.0], 1.0, 1.5, 0.05),
]


def run_rust(omega, k, alpha_h, sigma):
    args = [
        "cargo", "run", "--quiet", "--manifest-path",
        str(ROOT / "rust" / "Cargo.toml"), "--bin", "hill_design_probe", "--",
        str(k), str(alpha_h), str(sigma), "1e-12", "0.1",
        *[repr(value) for value in omega],
    ]
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode:
        raise AssertionError(f"Rust Hill design diagnostic failed: {result.stderr}")
    return json.loads(result.stdout)


def close(left, right, label, case_index):
    if right is None:
        right = math.inf
    if not math.isclose(left, right, rel_tol=1e-10, abs_tol=1e-12):
        raise AssertionError(
            f"case {case_index} {label}: Python={left!r}, Rust={right!r}"
        )


def main():
    for index, (omega, k, alpha_h, sigma) in enumerate(CASES, 1):
        py = diagnose_hill_design(omega, k, alpha_h, sigma)
        rs = run_rust(omega, k, alpha_h, sigma)
        if py.observations != rs["observations"] or py.local_rank != rs["local_rank"]:
            raise AssertionError(f"case {index}: observation count or local rank differs")
        for field in ("omega_range_orders", "saturation_fraction", "max_omega_over_k"):
            close(getattr(py, field), rs[field], field, index)
        close(py.fim_condition_number, rs["fim_condition_number"], "fim_condition_number", index)
        for position in range(2):
            close(py.singular_values[position], rs["singular_values"][position],
                  f"singular_values[{position}]", index)
            close(py.weak_direction[position], rs["weak_direction"][position],
                  f"weak_direction[{position}]", index)
        print(f"Hill design diagnostic parity OK: case {index}")
    print("Python/Rust local Hill design diagnostics match.")


if __name__ == "__main__":
    main()
