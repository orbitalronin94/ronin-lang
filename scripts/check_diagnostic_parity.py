#!/usr/bin/env python3
"""Compare Python/Rust diagnostic reports on the shared conformance corpus."""

import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = [
    ROOT / "tests" / "fixtures" / "conformance" / "degeneracy_active.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "degeneracy_inactive.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "degeneracy_unknown.ronin",
    ROOT / "tests" / "fixtures" / "conformance" / "valid_zero_fitness_check_only.ronin",
]
BOOTSTRAP = 50


def run_python(path):
    return subprocess.run(
        [sys.executable, "-m", "ronin.cli", "diagnose", str(path),
         "--bootstrap", str(BOOTSTRAP)],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )


def run_rust(path):
    return subprocess.run(
        ["cargo", "run", "--quiet", "--manifest-path", str(ROOT / "rust" / "Cargo.toml"),
         "--", "diagnose", str(path), "--bootstrap", str(BOOTSTRAP)],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )


def main():
    for path in FIXTURES:
        py = run_python(path)
        rs = run_rust(path)
        if py.returncode != 0:
            raise AssertionError(f"Python rejected {path.name}: {py.stderr}")
        if rs.returncode != 0:
            raise AssertionError(f"Rust rejected {path.name}: {rs.stderr}")
        left = json.loads(py.stdout)
        right = json.loads(rs.stdout)
        for field in ("degeneracy", "lambda_identifiable", "K_identifiable",
                      "alpha_h_identifiable", "recommendation", "bootstrap_ci"):
            if left[field] != right[field]:
                raise AssertionError(
                    f"{path.name}.{field}: Python={left[field]!r}, Rust={right[field]!r}"
                )
        if not math.isclose(left["omega_range_orders"], right["omega_range_orders"],
                            rel_tol=1e-12, abs_tol=1e-12):
            raise AssertionError(
                f"{path.name}.omega_range_orders: "
                f"Python={left['omega_range_orders']}, Rust={right['omega_range_orders']}"
            )
        print(f"diagnostic parity OK: {path.relative_to(ROOT)}")
    print("Bootstrap CI remains null in both runtimes; no estimator is claimed.")


if __name__ == "__main__":
    raise SystemExit(main())
