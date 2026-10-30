#!/usr/bin/env python3
"""Compare Python and Rust CSV run exports on shared projects."""

import csv
import io
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = [
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
]
HEADER = ["system", "agent_index", "model", "fitness", "allocation"]


def run_python(path):
    return subprocess.run(
        [sys.executable, "-m", "ronin.cli", "run", str(path), "--format", "csv"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )


def run_rust(path):
    return subprocess.run(
        ["cargo", "run", "--quiet", "--manifest-path", str(ROOT / "rust" / "Cargo.toml"),
         "--", "run", str(path), "--format", "csv"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )


def rows(result, backend, path):
    if result.returncode != 0:
        raise AssertionError(f"{backend} failed for {path.name}: {result.stderr}")
    reader = csv.DictReader(io.StringIO(result.stdout))
    if reader.fieldnames != HEADER:
        raise AssertionError(f"{backend} CSV header mismatch for {path.name}: {reader.fieldnames}")
    return list(reader)


def compare(path, label):
    python_rows = rows(run_python(path), "Python", path)
    rust_rows = rows(run_rust(path), "Rust", path)
    if len(python_rows) != len(rust_rows):
        raise AssertionError(f"{label}: CSV row counts differ")
    for index, (left, right) in enumerate(zip(python_rows, rust_rows)):
        for field in ("system", "agent_index", "model"):
            if left[field] != right[field]:
                raise AssertionError(
                    f"{label} row {index} {field}: {left[field]!r} != {right[field]!r}"
                )
        for field in ("fitness", "allocation"):
            if not math.isclose(float(left[field]), float(right[field]),
                                rel_tol=1e-9, abs_tol=1e-9):
                raise AssertionError(
                    f"{label} row {index} {field}: "
                    f"{left[field]!r} != {right[field]!r}"
                )
    print(f"CSV parity OK: {label}")


def main():
    for path in FIXTURES:
        compare(path, str(path.relative_to(ROOT)))

    multi_system_source = """
    system First = {
      parts: 2, resource: 100,
      agents: [
        { phi: 0.5, psi: 0.5, frequency: 0.5 },
        { phi: 0.5, psi: 0.5, frequency: 0.5 }
      ]
    }
    system Second = {
      parts: 2, resource: 100,
      agents: [
        { phi: 0.6, psi: 0.5, frequency: 0.5 },
        { phi: 0.5, psi: 0.6, frequency: 0.5 }
      ]
    }
    """
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "multi_system.ronin"
        path.write_text(multi_system_source, encoding="utf-8")
        compare(path, "multi-system project")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
