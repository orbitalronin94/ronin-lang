#!/usr/bin/env python3
"""Verify Python/Rust CLI system-selection semantics."""

import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VALID_FIRST = """
system First = {
  parts: 2, resource: 10,
  agents: [
    { phi: 0.5, psi: 0.5, frequency: 0.5 },
    { phi: 0.5, psi: 0.5, frequency: 0.5 }
  ]
}
"""
VALID_SECOND = """
system Second = {
  parts: 2, resource: 20,
  agents: [
    { phi: 0.6, psi: 0.5, frequency: 0.5 },
    { phi: 0.5, psi: 0.6, frequency: 0.5 }
  ]
}
"""
INVALID_SECOND = """
system Broken = {
  parts: 2, resource: 20,
  agents: [
    { phi: 0.6, psi: 0.5, frequency: 0.4 },
    { phi: 0.5, psi: 0.6, frequency: 0.5 }
  ]
}
"""


def run_python(command, path, *options):
    return subprocess.run(
        [sys.executable, "-m", "ronin.cli", command, str(path), *options],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )


def run_rust(command, path, *options):
    return subprocess.run(
        ["cargo", "run", "--quiet", "--manifest-path", str(ROOT / "rust" / "Cargo.toml"),
         "--", command, str(path), *options],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )


def compare_solutions(python_result, rust_result, system):
    py = json.loads(python_result.stdout)
    rs = json.loads(rust_result.stdout)
    if system not in rs or len(rs) != 1:
        raise AssertionError(f"Rust solve selected wrong system: {list(rs)}")
    rust = rs[system]
    for field in ("fitness", "allocation"):
        if len(py[field]) != len(rust[field]):
            raise AssertionError(f"{system}.{field} lengths differ")
        for left, right in zip(py[field], rust[field]):
            if not math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-9):
                raise AssertionError(f"{system}.{field} differs: {left} vs {right}")


def main():
    with tempfile.TemporaryDirectory() as directory:
        valid_path = Path(directory) / "valid_multi.ronin"
        valid_path.write_text(VALID_FIRST + VALID_SECOND, encoding="utf-8")

        py_solve = run_python("solve", valid_path)
        rs_solve = run_rust("solve", valid_path)
        if py_solve.returncode or rs_solve.returncode:
            raise AssertionError(f"default solve failed: {py_solve.stderr} {rs_solve.stderr}")
        compare_solutions(py_solve, rs_solve, "First")

        py_run = run_python("run", valid_path)
        rs_run = run_rust("run", valid_path)
        if py_run.returncode or rs_run.returncode:
            raise AssertionError(f"run failed: {py_run.stderr} {rs_run.stderr}")
        py_all = json.loads(py_run.stdout)
        rs_all = json.loads(rs_run.stdout)
        if set(py_all) != {"First", "Second"} or set(rs_all) != set(py_all):
            raise AssertionError(f"run system selection differs: Python={set(py_all)}, Rust={set(rs_all)}")
        for name in py_all:
            for field in ("fitness", "allocation"):
                for left, right in zip(py_all[name][field], rs_all[name][field]):
                    if not math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-9):
                        raise AssertionError(f"run {name}.{field} differs")

        py_selected = run_python("solve", valid_path, "--system", "Second")
        rs_selected = run_rust("solve", valid_path, "--system", "Second")
        if py_selected.returncode or rs_selected.returncode:
            raise AssertionError("named solve failed")
        compare_solutions(py_selected, rs_selected, "Second")

        mixed_path = Path(directory) / "mixed_multi.ronin"
        mixed_path.write_text(VALID_FIRST + INVALID_SECOND, encoding="utf-8")
        py_default = run_python("solve", mixed_path)
        rs_default = run_rust("solve", mixed_path)
        if py_default.returncode or rs_default.returncode:
            raise AssertionError("default solve should only evaluate the first declared system")

        py_all_check = run_python("check", mixed_path)
        rs_all_check = run_rust("check", mixed_path)
        if py_all_check.returncode == 0 or rs_all_check.returncode == 0:
            raise AssertionError("check should reject a project containing an invalid system")

        py_selected_check = run_python("check", mixed_path, "--system", "First")
        rs_selected_check = run_rust("check", mixed_path, "--system", "First")
        if py_selected_check.returncode or rs_selected_check.returncode:
            raise AssertionError("check --system First should validate the selected valid system")

    print("CLI selection parity OK: solve defaults first; run/check cover all systems.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
