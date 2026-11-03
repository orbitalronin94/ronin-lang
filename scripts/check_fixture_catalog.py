#!/usr/bin/env python3
"""Verify that every conformance fixture is catalogued and traces to matrix IDs."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "conformance"
CATALOG = FIXTURE_DIR / "README.md"
MATRIX = ROOT / "docs" / "conformance-matrix.md"
ID_PATTERN = re.compile(r"\b([A-Z][A-Z0-9]*(?:-[A-Z][A-Z0-9]*)*)-(\d{3})(?:[–/-](\d{3}))?\b")


def requirement_ids(text):
    found = set()
    for prefix, start, end in ID_PATTERN.findall(text):
        first = int(start)
        last = int(end) if end else first
        if last < first or last - first > 100:
            raise ValueError(f"invalid requirement range: {prefix}-{start}-{end}")
        found.update(f"{prefix}-{number:03d}" for number in range(first, last + 1))
    return found


def main():
    errors = []
    matrix_ids = requirement_ids(MATRIX.read_text(encoding="utf-8"))
    catalog_text = CATALOG.read_text(encoding="utf-8")
    catalogued = set()

    for line_number, line in enumerate(catalog_text.splitlines(), start=1):
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or not cells[0].startswith("`") or not cells[0].endswith(".ronin`"):
            continue
        filename = cells[0][1:-1]
        if filename in catalogued:
            errors.append(f"README.md:{line_number}: duplicate fixture entry {filename}")
        catalogued.add(filename)
        if not (FIXTURE_DIR / filename).is_file():
            errors.append(f"README.md:{line_number}: fixture does not exist: {filename}")
        if len(cells) < 3 or not cells[-1]:
            errors.append(f"README.md:{line_number}: missing traceability for {filename}")
            continue
        ids = requirement_ids(cells[-1])
        if not ids:
            errors.append(f"README.md:{line_number}: no requirement IDs for {filename}")
        for requirement_id in sorted(ids - matrix_ids):
            errors.append(
                f"README.md:{line_number}: {filename} references unknown matrix ID {requirement_id}"
            )

    actual = {path.name for path in FIXTURE_DIR.glob("*.ronin")}
    for filename in sorted(actual - catalogued):
        errors.append(f"uncatalogued fixture: {filename}")
    for filename in sorted(catalogued - actual):
        errors.append(f"catalog entry without fixture: {filename}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        f"Fixture catalog OK: {len(actual)} files; every entry exists and references known matrix IDs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
