# Shared conformance fixtures

These synthetic RONIN files are a shared input corpus for the Python and Rust implementations. They are separate from examples transcribed from the MDES source. Every fixture is synthetic and must not be presented as evidence from a real-world dataset.

## Positive fixtures

| File | Purpose | Traceability |
|---|---|---|
| `pusfre.ronin` | Valid PUSFRE project | CORE-001/002, LANG-001–004, TYPE-001, PARSER-001, RS-006, PY-006 |
| `ces.ronin` | Valid CES project | CORE-002, LANG-001–004, PARSER-001, RS-006, PY-006 |
| `hill.ronin` | Valid Hill project | CORE-002, LANG-001–004, PARSER-001, RS-006, PY-006 |
| `ces_hill.ronin` | Valid CES-Hill project | CORE-002, LANG-001–004, PARSER-001, RS-006, PY-006 |
| `full_order1.ronin` | Valid full model with first-order memory and normalized weights | LANG-002/005, TYPE-003/004, PARSER-001; only the explicitly supported first-order profile |
| `metadata_nested.ronin` | Nested metadata, escapes, Unicode-safe JSON values and a very small finite number | LANG-004/005, TYPE-001, PARSER-001, INTEROP-008, RS-005 |

## Negative fixtures

| File | Expected rejection | Traceability |
|---|---|---|
| `invalid_frequency_sum.ronin` | Agent frequencies do not sum to one | TYPE-004/005, CORE-008, VAL-CLI-001 |
| `invalid_pusfre_lambda.ronin` | PUSFRE with non-zero lambda | CORE-008, TYPE-004, VAL-CLI-001 |
| `invalid_alpha.ronin` | Alpha outside the supported range | TYPE-004/005, VAL-CLI-001 |
| `full_order3_unsupported.ronin` | Higher-order temporal memory is not implemented | LANG-005, PY-006, RS-006; negative capability boundary, not a positive conformance claim |

## Diagnostic fixtures

| File | Expected diagnosis | Traceability |
|---|---|---|
| `degeneracy_active.ronin` | active — narrow positive-frequency range | CORE-007, PY-008, RS-008, SIM-003 |
| `degeneracy_inactive.ronin` | inactive — at least three orders of magnitude | CORE-007, PY-008, RS-008, SIM-003 |
| `degeneracy_unknown.ronin` | unknown — fewer than two positive frequencies | CORE-007, PY-008, RS-008, SIM-003 |

## Check-only fixture

| File | Purpose | Traceability |
|---|---|---|
| `valid_zero_fitness_check_only.ronin` | Semantically valid project with zero total fitness; validation, diagnosis and simulation accept it, while `solve` reports undefined allocation | VAL-CLI-001, CLI-SELECT-001; distinguishes validation from numerical solve |

## How the corpus is exercised

The shared corpus is consumed by these cross-runtime scripts:

- `scripts/check_parser_parity.py` — parser acceptance/rejection and declaration names.
- `scripts/check_validation_parity.py` — semantic check acceptance, rejection and system selection.
- `scripts/check_ir_parity.py` — JSON IR structural equality and rejection parity.
- `scripts/check_runtime_parity.py` — solver outputs and numerical tolerances.
- `scripts/check_diagnostic_parity.py` — diagnostic report parity.
- `scripts/check_simulation_contracts.py` — seeded trajectories and simulation invariants.
- `scripts/check_cli_selection_parity.py` — default and explicit system selection.
- `scripts/check_csv_parity.py` — CSV parity for the currently supported export scope.

Run the scripts from the repository root after installing the Python package and Rust toolchain. The canonical CI workflow remains the source of truth for the exact jobs and supported environments.

## Limits

All fixtures use synthetic values. They do not replace normative examples or missing real datasets in MDES v0.5. Expected behavior is tested by both implementations where the corresponding feature exists.

A traceability ID identifies the intended requirement area; it does not upgrade a matrix status from P/A/N to I. In particular, parser acceptance does not prove semantic validation, solver correctness, or full MDES conformance. The matrix remains authoritative for the status and evidence of each requirement.
