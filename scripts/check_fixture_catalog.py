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


def evidence_file_paths(text):
    """Return repository-relative paths explicitly formatted as inline code."""
    for match in INLINE_CODE_PATTERN.findall(text):
        if "/" not in match:
            continue
        path = match.split("::", 1)[0].strip().rstrip(".,;)")
        if path:
            yield path


def evidence_file_symbols(text):
    """Return (path, symbol) pairs for inline-code file/function references."""
    for match in INLINE_CODE_PATTERN.findall(text):
        if "/" not in match or "::" not in match:
            continue
        path, symbol = match.split("::", 1)
        symbol = symbol.split("::")[-1].strip().rstrip(".,;)")
        if path and symbol:
            yield path, symbol


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
    candidate_ids = {item for item in requirement_ids(candidate_section) if not item.startswith("OPEN-")}
    for requirement_id in sorted(candidate_ids):
        statuses = matrix_statuses.get(requirement_id, set())
        if not statuses.intersection({"I", "P"}):
            errors.append(
                f"v1-profile-proposal.md: candidate ID {requirement_id} is not I/P in the conformance matrix"
            )

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
        row_paths = list(evidence_file_paths(evidence))
        if not any(path.startswith(("tests/", "rust/tests/", "scripts/")) for path in row_paths):
            errors.append(
                f"conformance-matrix.md:{line_number}: {cells[0]} has no explicit test, fixture, or parity-script reference"
            )
        for path in row_paths:
            checked_paths += 1
            if not (ROOT / path).is_file():
                errors.append(
                    f"conformance-matrix.md:{line_number}: {cells[0]} cites missing evidence path {path}"
                )
        for path, symbol in evidence_file_symbols(evidence):
            source_path = ROOT / path
            if not source_path.is_file():
                continue
            source = source_path.read_text(encoding="utf-8")
            declaration = re.compile(r"\b(?:def|fn)\s+" + re.escape(symbol) + r"\b")
            if not declaration.search(source):
                errors.append(
                    f"conformance-matrix.md:{line_number}: {cells[0]} cites missing symbol {symbol} in {path}"
                )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        f"Traceability OK: {len(matrix_row_ids)} unique matrix requirements; "
        f"{len(profile_ids)} profile proposal IDs map to matrix rows; "
        f"{len(candidate_ids)} candidate IDs are I/P; {len(actual)} fixtures; "
        f"{audited_rows} I/P rows; {checked_paths} cited evidence paths resolve."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
