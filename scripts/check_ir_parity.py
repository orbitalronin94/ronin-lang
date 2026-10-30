#!/usr/bin/env python3
"""Compare Python and Rust JSON IR for the shared conformance corpus."""

import json
import subprocess
import sys
from pathlib import Path

from ronin.errors import SemanticError
from ronin.ir import compile_program
from ronin.parser import parse

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
]
INVALID = [
    ROOT / "tests" / "fixtures" / "conformance" / "invalid_frequency_sum.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "invalid_pusfre_lambda.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "invalid_alpha.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "full_order3_unsupported.ronin",
]


def rust_compile(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "cargo", "run", "--quiet", "--manifest-path",
            str(ROOT / "rust" / "Cargo.toml"), "--",
            "compile", str(path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    for path in VALID:
        python_ir = compile_program(parse(path.read_text(encoding="utf-8")))
        result = rust_compile(path)
        if result.returncode != 0:
            print(f"Rust rejected valid fixture {path.relative_to(ROOT)}:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return 1
        try:
            rust_ir = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            print(f"Rust emitted invalid JSON for {path.relative_to(ROOT)}: {error}", file=sys.stderr)
            print(result.stdout, file=sys.stderr)
            return 1
        if rust_ir != python_ir:
            print(f"IR mismatch: {path.relative_to(ROOT)}", file=sys.stderr)
            print("Python:", json.dumps(python_ir, ensure_ascii=False, sort_keys=True), file=sys.stderr)
            print("Rust:  ", json.dumps(rust_ir, ensure_ascii=False, sort_keys=True), file=sys.stderr)
            return 1
        print(f"IR parity OK: {path.relative_to(ROOT)}")

    for path in INVALID:
        try:
            compile_program(parse(path.read_text(encoding="utf-8")))
        except SemanticError:
            pass
        else:
            print(f"Python unexpectedly accepted {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        result = rust_compile(path)
        if result.returncode == 0:
            print(f"Rust unexpectedly accepted {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"rejection parity OK: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
