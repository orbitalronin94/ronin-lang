#!/usr/bin/env python3
"""Compare Python/Rust check acceptance, including all-system selection."""

import subprocess
import sys
import tempfile
from pathlib import Path

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
INVALID = [
    ROOT / "tests" / "fixtures" / "conformance" / "invalid_frequency_sum.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "invalid_pusfre_lambda.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "invalid_alpha.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "full_order3_unsupported.ronin",
]


def run_python(path, system=None):
    args = [sys.executable, "-m", "ronin.cli", "check", str(path)]
    if system is not None:
        args.extend(["--system", system])
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def run_rust(path, system=None):
    args = ["cargo", "run", "--quiet", "--manifest-path", str(ROOT / "rust" / "Cargo.toml"),
            "--", "check", str(path)]
    if system is not None:
        args.extend(["--system", system])
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def compare(path, expected, label, system=None):
    py = run_python(path, system)
    rs = run_rust(path, system)
    py_ok = py.returncode == 0
    rs_ok = rs.returncode == 0
    if py_ok != expected or rs_ok != expected or py_ok != rs_ok:
        raise AssertionError(
            f"{label}: expected={expected}, Python={py.returncode} ({py.stderr}), "
            f"Rust={rs.returncode} ({rs.stderr})"
        )
    print(f"check parity OK: {label}")


def main():
    for path in VALID:
        compare(path, True, str(path.relative_to(ROOT)))
    for path in INVALID:
        compare(path, False, str(path.relative_to(ROOT)))

    valid = """
    system First = {
      parts: 2, resource: 10,
      agents: [
        { phi: 0.5, psi: 0.5, frequency: 0.5 },
        { phi: 0.5, psi: 0.5, frequency: 0.5 }
      ]
    }
    """
    invalid = """
    system Broken = {
      parts: 2, resource: 10,
      agents: [
        { phi: 0.5, psi: 0.5, frequency: 0.4 },
        { phi: 0.5, psi: 0.5, frequency: 0.5 }
      ]
    }
    """
    with tempfile.TemporaryDirectory() as directory:
        valid_path = Path(directory) / "valid_multi.ronin"
        valid_path.write_text(valid + valid.replace("First", "Second"), encoding="utf-8")
        compare(valid_path, True, "multi-system / all valid")

        mixed_path = Path(directory) / "mixed_multi.ronin"
        mixed_path.write_text(valid + invalid, encoding="utf-8")
        compare(mixed_path, False, "multi-system / one invalid")
        compare(mixed_path, True, "multi-system / selected valid system", "First")
        compare(mixed_path, False, "multi-system / selected invalid system", "Broken")
        compare(mixed_path, False, "multi-system / unknown selection", "Missing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
