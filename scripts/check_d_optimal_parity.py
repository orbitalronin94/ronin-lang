#!/usr/bin/env python3
"""Cross-runtime parity for greedy D-optimal observation selection."""

import json
import math
import subprocess
from pathlib import Path

from ronin.identifiability import d_optimal_design

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    {
        "jacobian": [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, -1.0]],
        "n_samples": 2,
        "weights": None,
        "parameter_scales": None,
        "ridge": 1e-12,
    },
    {
        "jacobian": [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, -1.0]],
        "n_samples": 2,
        "weights": [1.0, 3.0, 1.0, 1.0],
        "parameter_scales": [2.0, 1.0],
        "ridge": 1e-10,
    },
    {
        "jacobian": [[1.0, 2.0], [2.0, 4.0], [3.0, 6.0]],
        "n_samples": 2,
        "weights": [1.0, 1.0, 1.0],
        "parameter_scales": [1.0, 1.0],
        "ridge": 1e-12,
    },
]


def encode_vector(values):
    return ",".join(format(value, ".17g") for value in values)


def encode_matrix(matrix):
    return ";".join(encode_vector(row) for row in matrix)


def run_rust(case):
    weights = "-" if case["weights"] is None else encode_vector(case["weights"])
    scales = "-" if case["parameter_scales"] is None else encode_vector(case["parameter_scales"])
    args = [
        "cargo", "run", "--quiet", "--manifest-path", str(ROOT / "rust" / "Cargo.toml"),
        "--bin", "d_optimal_probe", "--", str(case["n_samples"]),
        format(case["ridge"], ".17g"), encode_matrix(case["jacobian"]), weights, scales,
    ]
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def close(left, right, label):
    if left is None or right is None:
        if left is not right:
            raise AssertionError(f"{label}: Python={left!r}, Rust={right!r}")
        return
    if not math.isclose(float(left), float(right), rel_tol=1e-11, abs_tol=1e-11):
        raise AssertionError(f"{label}: Python={left!r}, Rust={right!r}")


def main():
    for index, case in enumerate(CASES):
        py = d_optimal_design(
            case["jacobian"],
            case["n_samples"],
            weights=case["weights"],
            parameter_scales=case["parameter_scales"],
            ridge=case["ridge"],
        )
        result = run_rust(case)
        if result.returncode:
            raise AssertionError(f"D-optimal case {index}: Rust failed: {result.stderr}")
        rs = json.loads(result.stdout)
        if list(py.selected_indices) != rs["selected_indices"]:
            raise AssertionError(
                f"D-optimal case {index}: selected rows differ: "
                f"Python={py.selected_indices}, Rust={rs['selected_indices']}"
            )
        close(py.log_determinant, rs["log_determinant"], f"case {index}.logdet")
        close(py.jacobian_scale, rs["jacobian_scale"], f"case {index}.jacobian_scale")
        close(
            py.local_information.fim_condition_number
            if math.isfinite(py.local_information.fim_condition_number) else None,
            rs["fim_condition_number"],
            f"case {index}.condition",
        )
        if py.local_information.local_rank != rs["local_rank"]:
            raise AssertionError(f"D-optimal case {index}: local rank differs")
        for row_index, (py_row, rs_row) in enumerate(
            zip(py.normalized_information_matrix, rs["normalized_information_matrix"])
        ):
            for column_index, (left, right) in enumerate(zip(py_row, rs_row)):
                close(left, right, f"case {index}.fim[{row_index}][{column_index}]")
        print(f"D-optimal Python/Rust parity OK: case {index + 1}")

    print(f"D-optimal design parity OK: {len(CASES)} cases.")


if __name__ == "__main__":
    main()
