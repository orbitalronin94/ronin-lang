#!/usr/bin/env python3
"""Compare Python and Rust early-phase SIR identifiability diagnostics."""

import json
import math
import subprocess
from pathlib import Path

from ronin.identifiability import diagnose_sir_early_phase

ROOT = Path(__file__).resolve().parents[1]


def projector(directions):
    size = len(directions[0]) if directions else 0
    return [
        [
            sum(vector[row] * vector[col] for vector in directions)
            for col in range(size)
        ]
        for row in range(size)
    ]


def main():
    times = list(range(31))
    parameters = (0.4, 0.15, 0.1, 100.0, 0.1)
    py = diagnose_sir_early_phase(times, *parameters)
    args = [
        "cargo", "run", "--quiet", "--manifest-path",
        str(ROOT / "rust" / "Cargo.toml"), "--bin", "sir_design_probe", "--",
        *[str(value) for value in parameters],
        *[str(value) for value in times],
    ]
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode:
        raise AssertionError(f"Rust SIR diagnostic failed: {result.stderr}")
    rs = json.loads(result.stdout)

    assert py.local_information.local_rank == rs["local_rank"]
    assert py.structural_status == rs["structural_status"]
    python_projector = projector(py.local_information.weak_directions)
    rust_projector = projector(rs["weak_directions"])
    for row, values in enumerate(python_projector):
        for col, value in enumerate(values):
            if not math.isclose(value, rust_projector[row][col], rel_tol=1e-8, abs_tol=1e-10):
                raise AssertionError(
                    f"weak-direction subspace projector[{row},{col}]: "
                    f"Python={value}, Rust={rust_projector[row][col]}"
                )
    assert py.growth_rate == rs["growth_rate"]
    assert py.observed_amplitude == rs["observed_amplitude"]
    for index, value in enumerate(py.local_information.singular_values):
        rust_value = rs["singular_values"][index]
        if rust_value is None:
            rust_value = 0.0
        if not math.isclose(value, rust_value, rel_tol=1e-9, abs_tol=1e-11):
            raise AssertionError(
                f"singular_values[{index}]: Python={value}, Rust={rust_value}"
            )
    if not math.isclose(
        py.local_information.fim_condition_number,
        math.inf if rs["fim_condition_number"] is None else rs["fim_condition_number"],
        rel_tol=1e-9,
    ):
        raise AssertionError("SIR FIM condition number differs")
    print("Python/Rust early-phase SIR diagnostic parity OK.")


if __name__ == "__main__":
    main()
