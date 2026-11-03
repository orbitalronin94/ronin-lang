#!/usr/bin/env python3
"""Compare Python/Rust CLI failure behavior without requiring identical wording."""

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID = """
system First = {
  parts: 2, resource: 10,
  agents: [
    { phi: 0.5, psi: 0.5, frequency: 0.5 },
    { phi: 0.5, psi: 0.5, frequency: 0.5 }
  ]
}
"""
INVALID = """
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
        ["cargo", "run", "--quiet", "--manifest-path",
         str(ROOT / "rust" / "Cargo.toml"), "--", command, str(path), *options],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )


def assert_failure(label, python_result, rust_result):
    for runtime, result in (("Python", python_result), ("Rust", rust_result)):
        if result.returncode == 0:
            raise AssertionError(f"{label}: {runtime} unexpectedly succeeded")
        if result.stdout.strip():
            raise AssertionError(f"{label}: {runtime} wrote output on stdout: {result.stdout!r}")
        if not result.stderr.strip():
            raise AssertionError(f"{label}: {runtime} did not explain the failure on stderr")


def main():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        missing = root / "missing.ronin"
        py = run_python("check", missing)
        rs = run_rust("check", missing)
        assert_failure("missing input file", py, rs)

        valid = root / "valid.ronin"
        valid.write_text(VALID, encoding="utf-8")
        py = run_python("solve", valid, "--system", "Absent")
        rs = run_rust("solve", valid, "--system", "Absent")
        assert_failure("unknown selected system", py, rs)

        malformed = root / "malformed.ronin"
        malformed.write_text("system Broken = { parts: }", encoding="utf-8")
        py = run_python("check", malformed)
        rs = run_rust("check", malformed)
        assert_failure("malformed source", py, rs)

        invalid = root / "invalid.ronin"
        invalid.write_text(INVALID, encoding="utf-8")
        py = run_python("check", invalid)
        rs = run_rust("check", invalid)
        assert_failure("semantic validation rejection", py, rs)

    print("CLI error-path parity OK: both runtimes fail cleanly on four shared cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
