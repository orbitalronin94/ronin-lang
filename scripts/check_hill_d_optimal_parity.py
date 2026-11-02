#!/usr/bin/env python3
"""Cross-runtime parity for D-optimal Hill observation selection."""

import json
import math
import subprocess
from pathlib import Path

from ronin.identifiability import d_optimal_hill_design

ROOT = Path(__file__).resolve().parents[1]
BASE_OMEGA = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
CASES = [
    (BASE_OMEGA, 1.0, 1.5, 0.05, 3),
    ([value * 1e200 for value in BASE_OMEGA], 1e200, 1.5, 0.05, 3),
    ([1.0, 1.0, 1.0], 1.0, 1.5, 0.05, 2),
]


def close(left, right, label):
    if left is None or right is None:
        if left is not right:
            raise AssertionError(f"{label}: Python={left!r}, Rust={right!r}")
        return
    if not math.isclose(left, right, rel_tol=1e-10, abs_tol=1e-10):
        raise AssertionError(f"{label}: Python={left!r}, Rust={right!r}")


def main():
    for index, (omega, k, alpha_h, sigma, n_samples) in enumerate(CASES):
        py = d_optimal_hill_design(omega, n_samples, k, alpha_h, sigma)
        args = [
            "cargo", "run", "--quiet", "--manifest-path", str(ROOT / "rust" / "Cargo.toml"),
            "--bin", "hill_d_optimal_probe", "--",
            str(n_samples), format(k, ".17g"), format(alpha_h, ".17g"),
            format(sigma, ".17g"), "1e-12",
            ",".join(format(value, ".17g") for value in omega),
        ]
        result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode:
            raise AssertionError(f"Hill D-optimal case {index}: Rust failed: {result.stderr}")
        rs = json.loads(result.stdout)
        if list(py.selected_indices) != rs["selected_indices"]:
            raise AssertionError(f"Hill D-optimal case {index}: selected indices differ")
        if len(py.selected_omega) != len(rs["selected_omega"]):
            raise AssertionError(f"Hill D-optimal case {index}: selected Omega count differs")
        for position, (left, right) in enumerate(zip(py.selected_omega, rs["selected_omega"])):
            close(left, right, f"case {index}.selected_omega[{position}]")
        close(py.design.log_determinant, rs["log_determinant"], f"case {index}.logdet")
        condition = py.design.local_information.fim_condition_number
        close(condition if math.isfinite(condition) else None, rs["condition"], f"case {index}.condition")
        if py.design.local_information.local_rank != rs["local_rank"]:
            raise AssertionError(f"Hill D-optimal case {index}: local rank differs")
        if len(py.warnings) != rs["warnings"]:
            raise AssertionError(f"Hill D-optimal case {index}: warnings differ")
        print(f"Hill D-optimal Python/Rust parity OK: case {index + 1}")

    print("Hill D-optimal design parity OK: broad, rescaled and rank-deficient designs.")


if __name__ == "__main__":
    main()
