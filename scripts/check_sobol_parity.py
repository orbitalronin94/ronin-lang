#!/usr/bin/env python3
"""Cross-runtime parity for the generic first-order Sobol estimator."""

import json
import math
import subprocess
from pathlib import Path

from ronin.identifiability import sobol_first_order

ROOT = Path(__file__).resolve().parents[1]
BASE_A = [0.2, 1.3, -0.4, 2.1, 0.9]
BASE_B = [1.2, -0.2, 0.7, 1.9, -1.0]
BASE_AB = [
    [0.5, 1.0, 0.3, 2.5, 0.4],
    [1.4, -0.1, 0.8, 1.2, -0.6],
]


def encode(values):
    return ",".join(format(value, ".17g") for value in values)


def run_rust(f_a, f_b, f_ab):
    matrix = ";".join(encode(row) for row in f_ab)
    args = [
        "cargo", "run", "--quiet", "--manifest-path", str(ROOT / "rust" / "Cargo.toml"),
        "--bin", "sobol_probe", "--", encode(f_a), encode(f_b), matrix,
    ]
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def close(left, right, label):
    if not math.isclose(left, right, rel_tol=1e-11, abs_tol=1e-11):
        raise AssertionError(f"{label}: Python={left!r}, Rust={right!r}")


def main():
    for factor in (1.0, 1e-200, 1e200):
        f_a = [factor * value for value in BASE_A]
        f_b = [factor * value for value in BASE_B]
        f_ab = [[factor * value for value in row] for row in BASE_AB]
        py = sobol_first_order(f_a, f_b, f_ab)
        result = run_rust(f_a, f_b, f_ab)
        if result.returncode:
            raise AssertionError(f"Sobol factor {factor}: Rust failed: {result.stderr}")
        rs = json.loads(result.stdout)
        if rs["sample_count"] != py.sample_count or rs["parameter_count"] != py.parameter_count:
            raise AssertionError(f"Sobol factor {factor}: dimensions differ")
        for index, (left, right) in enumerate(zip(py.first_order_indices, rs["first_order_indices"])):
            close(left, right, f"factor {factor}.S1[{index}]")
        close(py.output_scale, rs["output_scale"], f"factor {factor}.output_scale")
        close(
            py.output_variance_normalized,
            rs["output_variance_normalized"],
            f"factor {factor}.normalized_variance",
        )
        print(f"Sobol Python/Rust parity OK: output scale {factor:g}")

    print("First-order Sobol parity OK: ordinary and extreme output scales.")


if __name__ == "__main__":
    main()
