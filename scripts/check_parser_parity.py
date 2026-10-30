#!/usr/bin/env python3
"""Compare parser acceptance and system declarations across Python and Rust."""

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID_FILES = [
    ROOT / "examples" / "maquinas.ronin",
    ROOT / "examples" / "maquinas_ces.ronin",
    ROOT / "examples" / "pesca.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "pusfre.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "ces.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "hill.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "ces_hill.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "metadata_nested.ronin",
]

VALID_SOURCES = {
    "comments_and_extended_params": r'''
        // comment at the start
        system Coastal = {
          parts: 2, resource: 10,
          agents: [
            { phi: 0.6, psi: 0.7, frequency: 0.5, role: worker, tools: ["net"] },
            { phi: 0.5, psi: 0.8, frequency: 0.5 }
          ],
          params: { model: "ces", lambda: -0.25, K: inf, memory_order: 2 }
        }
    ''',
    "escaped_unicode_string": r'''
        system Escapes = {
          parts: 1, resource: 1,
          agents: [
            { phi: 1, psi: 1, frequency: 1,
              note: "say \"hi\"; path C:\\ronin\nnext\t\u263A" }
          ]
        }
    ''',
    "nested_object_and_arrays": r'''
        system Nested = {
          parts: 1, resource: 1,
          agents: [
            { phi: 1, psi: 1, frequency: 1,
              profile: { niche: robotics, active: true,
                         tags: ["a", "b"], details: { region: "north" } } }
          ]
        }
    ''',
}

INVALID_SOURCES = {
    "duplicate_system_field": """
        system Bad = { parts: 2, parts: 3, resource: 1,
          agents: [{phi: 1, psi: 1, frequency: 1}] }
    """,
    "duplicate_agent_field": """
        system Bad = { parts: 1, resource: 1,
          agents: [{phi: 1, phi: 1, psi: 1, frequency: 1}] }
    """,
    "duplicate_params_field": """
        system Bad = { parts: 1, resource: 1,
          agents: [{phi: 1, psi: 1, frequency: 1}],
          params: {alpha: 1, alpha: 2} }
    """,
    "duplicate_nested_object_key": """
        system Bad = { parts: 1, resource: 1,
          agents: [{phi: 1, psi: 1, frequency: 1, meta: {x: 1, x: 2}}] }
    """,
    "unsupported_string_escape": r'''
        system Bad = { parts: 1, resource: 1,
          agents: [{phi: 1, psi: 1, frequency: 1, note: "bad\q"}] }
    ''',
    "missing_agent_field": """
        system Bad = { parts: 1, resource: 1,
          agents: [{phi: 1, psi: 1}] }
    """,
    "unterminated_array": """
        system Bad = { parts: 1, resource: 1,
          agents: [{phi: 1, psi: 1, frequency: 1}] 
    """,
}


def run_python(path):
    return subprocess.run(
        [sys.executable, "-m", "ronin.cli", "list", str(path)],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )


def run_rust(path):
    return subprocess.run(
        ["cargo", "run", "--quiet", "--manifest-path", str(ROOT / "rust" / "Cargo.toml"),
         "--", "list", str(path)],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )


def compare(path, expected, label, expected_names=None):
    py = run_python(path)
    rs = run_rust(path)
    if (py.returncode == 0) != expected or (rs.returncode == 0) != expected:
        raise AssertionError(
            f"{label}: expected accepted={expected}, Python={py.returncode} ({py.stderr}), "
            f"Rust={rs.returncode} ({rs.stderr})"
        )
    if expected and py.stdout.splitlines() != rs.stdout.splitlines():
        raise AssertionError(
            f"{label}: declaration names differ: Python={py.stdout!r}, Rust={rs.stdout!r}"
        )
    if expected and expected_names is not None and py.stdout.splitlines() != expected_names:
        raise AssertionError(f"{label}: expected names {expected_names}, got {py.stdout.splitlines()}")
    print(f"parser parity OK: {label}")


def main():
    for path in VALID_FILES:
        compare(path, True, str(path.relative_to(ROOT)))

    with tempfile.TemporaryDirectory() as directory:
        for label, source in VALID_SOURCES.items():
            path = Path(directory) / f"{label}.ronin"
            path.write_text(source, encoding="utf-8")
            expected_names = {
            "comments_and_extended_params": ["Coastal"],
            "escaped_unicode_string": ["Escapes"],
            "nested_object_and_arrays": ["Nested"],
        }[label]
        compare(path, True, label, expected_names)
        for label, source in INVALID_SOURCES.items():
            path = Path(directory) / f"{label}.ronin"
            path.write_text(source, encoding="utf-8")
            compare(path, False, label)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
