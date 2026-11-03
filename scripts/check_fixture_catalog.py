#!/usr/bin/env python3
"""Verify fixture inventory and both directions of its matrix traceability."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "conformance"
CATALOG = FIXTURE_DIR / "README.md"
MATRIX = ROOT / "docs" / "conformance-matrix.md"
PROFILE = ROOT / "docs" / "v1-profile-proposal.md"
ID_PATTERN = re.compile(r"\b([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*)-(\d{3})(?:[–/-](\d{3}))?\b")
ROW_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3}$")
INLINE_CODE_PATTERN = re.compile(chr(96) + r"([^" + chr(96) + r"]+)" + chr(96))


def table_cells(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def requirement_ids(text):
    found = set()
    for prefix, start, end in ID_PATTERN.findall(text):
        first = int(start)
        last = int(end) if end else first
        if last < first or last - first > 100:
            raise ValueError(f"invalid requirement range: {prefix}-{start}-{end}")
        found.update(f"{prefix}-{number:03d}" for number in range(first, last + 1))
    return found


def evidence_references(text):
    """Return (path, optional symbol) pairs from inline-code evidence references."""
    for match in INLINE_CODE_PATTERN.findall(text):
        if "/" not in match:
            continue
        reference = match.strip().rstrip(".,;)")
        path, separator, symbol = reference.partition("::")
        if path:
            yield path, symbol.strip() if separator else None


def main():
    errors = []
    matrix_text = MATRIX.read_text(encoding="utf-8")
    matrix_row_ids = set()
    matrix_references = {}
    matrix_statuses = {}
    for line_number, line in enumerate(matrix_text.splitlines(), start=1):
        if not line.startswith("|"):
            continue
        cells = table_cells(line)
        if not cells or not ROW_ID_PATTERN.fullmatch(cells[0]):
            continue
        requirement_id = cells[0]
        if requirement_id in matrix_row_ids:
            errors.append(f"conformance-matrix.md:{line_number}: duplicate requirement row ID {requirement_id}")
        matrix_row_ids.add(requirement_id)
        reference = cells[1].strip() if len(cells) > 1 else ""
        if not reference or reference in {"—", "-", "TBD", "TODO"}:
            errors.append(f"conformance-matrix.md:{line_number}: {requirement_id} has no MDES reference")
        matrix_references[requirement_id] = reference
        if len(cells) == 6:
            matrix_statuses[requirement_id] = {cell.strip("* " + chr(96)) for cell in cells[3:5]}
        elif len(cells) >= 5:
            matrix_statuses[requirement_id] = {cells[3].strip("* " + chr(96))}

    profile_text = PROFILE.read_text(encoding="utf-8")
    profile_ids = {item for item in requirement_ids(profile_text) if not item.startswith("OPEN-")}
    for requirement_id in sorted(profile_ids - matrix_row_ids):
        errors.append(f"v1-profile-proposal.md: unknown matrix requirement ID {requirement_id}")
    for requirement_id in sorted(profile_ids & matrix_row_ids):
        if not matrix_references.get(requirement_id):
            errors.append(f"v1-profile-proposal.md: {requirement_id} has no matrix MDES reference")

    candidate_section = profile_text.split("## 2. Candidato de alcance incluido", 1)[1].split("## 3. Exclusiones", 1)[0]
    candidate_ids = set()
    candidate_rows = 0
    for line_number, line in enumerate(candidate_section.splitlines(), start=1):
        if not line.startswith("|"):
            continue
        cells = table_cells(line)
        if len(cells) < 4 or cells[0].lower() == "área" or all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        row_ids = {item for item in requirement_ids(cells[1]) if not item.startswith("OPEN-")}
        if not row_ids:
            errors.append(
                f"v1-profile-proposal.md:candidate table line {line_number}: row has no matrix requirement IDs"
            )
            continue
        duplicate_ids = candidate_ids.intersection(row_ids)
        for requirement_id in sorted(duplicate_ids):
            errors.append(
                f"v1-profile-proposal.md:candidate table line {line_number}: duplicate candidate ID {requirement_id}"
            )
        candidate_ids.update(row_ids)
        candidate_rows += 1
        for requirement_id in sorted(row_ids):
            statuses = matrix_statuses.get(requirement_id, set())
            if not statuses.intersection({"I", "P"}):
                errors.append(
                    f"v1-profile-proposal.md: candidate ID {requirement_id} is not I/P in the conformance matrix"
                )
    if candidate_rows == 0:
        errors.append("v1-profile-proposal.md: candidate scope table is empty or unreadable")

    catalog_text = CATALOG.read_text(encoding="utf-8")
    catalogued = set()

    for line_number, line in enumerate(catalog_text.splitlines(), start=1):
        if not line.startswith("|"):
            continue
        cells = table_cells(line)
        if not cells or not cells[0].startswith(chr(96)) or not cells[0].endswith(".ronin" + chr(96)):
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
        for requirement_id in sorted(ids - matrix_row_ids):
            errors.append(f"README.md:{line_number}: {filename} references unknown matrix ID {requirement_id}")

    actual = {path.name for path in FIXTURE_DIR.glob("*.ronin")}
    for filename in sorted(actual - catalogued):
        errors.append(f"uncatalogued fixture: {filename}")
    for filename in sorted(catalogued - actual):
        errors.append(f"catalog entry without fixture: {filename}")

    # Reverse direction: I/P rows need evidence notes and any cited file paths
    # must resolve. This validates references, not semantic test sufficiency.
    audited_rows = 0
    checked_paths = 0
    for line_number, line in enumerate(matrix_text.splitlines(), start=1):
        if not line.startswith("|"):
            continue
        cells = table_cells(line)
        if len(cells) < 4 or not ROW_ID_PATTERN.fullmatch(cells[0]):
            continue
        statuses = {cell.strip("* " + chr(96)) for cell in cells[1:-1]}
        if not statuses.intersection({"I", "P"}):
            continue
        audited_rows += 1
        evidence = cells[-1].strip()
        if not evidence or evidence in {"—", "-", "TBD", "TODO"}:
            errors.append(f"conformance-matrix.md:{line_number}: {cells[0]} is I/P without evidence or an explicit limitation")
            continue
        row_references = list(evidence_references(evidence))
        row_paths = [path for path, _ in row_references]
        if not any(path.startswith(("tests/", "rust/tests/", "scripts/")) for path in row_paths):
            errors.append(
                f"conformance-matrix.md:{line_number}: {cells[0]} has no explicit test, fixture, or parity-script reference"
            )
        for path, symbol in row_references:
            checked_paths += 1
            source_path = ROOT / path
            if not source_path.is_file():
                errors.append(
                    f"conformance-matrix.md:{line_number}: {cells[0]} cites missing evidence path {path}"
                )
                continue
            if symbol:
                try:
                    source_text = source_path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    errors.append(
                        f"conformance-matrix.md:{line_number}: {cells[0]} symbol target is not UTF-8 text: {path}::{symbol}"
                    )
                    continue
                if symbol not in source_text:
                    errors.append(
                        f"conformance-matrix.md:{line_number}: {cells[0]} cites missing symbol {path}::{symbol}"
                    )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        f"Traceability OK: {len(matrix_row_ids)} unique matrix requirements; "
        f"{len(profile_ids)} profile proposal IDs map to matrix rows; "
        f"{len(candidate_ids)} candidate IDs across {candidate_rows} scope rows are I/P; {len(actual)} fixtures; "
        f"{audited_rows} I/P rows; {checked_paths} cited evidence paths resolve."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
