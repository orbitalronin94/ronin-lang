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
- `scripts/check_cli_error_parity.py` — shared CLI failure cases and clean stderr/stdout behavior.
- `scripts/check_csv_parity.py` — CSV parity for the currently supported export scope.

Run the scripts from the repository root after installing the Python package and Rust toolchain. The canonical CI workflow remains the source of truth for the exact jobs and supported environments.

## Script coverage inventory

This inventory records the concrete scope visible in each parity script. Counts refer to inputs/cases enumerated by the script, not to a percentage of MDES conformance.

| Script | Concrete coverage in the current script | Important boundary |
|---|---|---|
| `check_parser_parity.py` | 8 valid files, 3 valid inline sources and 20 invalid inline sources | Parser acceptance, declared system names and a shared line/column diagnostic sentinel; not semantic execution |
| `check_validation_parity.py` | 12 valid files, 4 invalid files and 5 multi-system selection cases | Acceptance/rejection and selected-system behavior; does not compare all diagnostic wording |
| `check_ir_parity.py` | 11 valid files and 4 invalid files | Structural JSON equality and rejection parity for the listed corpus |
| `check_runtime_parity.py` | 11 valid files, 4 invalid files and one explicit delta override | Solver fields and numeric tolerances for the enumerated models; not all MDES formulas |
| `check_diagnostic_parity.py` | 4 diagnostic/check-only fixtures | Report fields and range comparison; bootstrap confidence interval remains null |
| `check_simulation_contracts.py` | 12 valid files, 12 steps, fixed seed 73 | Seeded trajectory/invariant comparison for these fixtures; not a universal RNG contract |
| `check_cli_selection_parity.py` | Synthetic two-system valid and mixed-validity projects | Default `solve`, all-system `run`, and named selection; error paths are covered separately |
| `check_cli_error_parity.py` | 10 shared failures: missing file, unknown system, malformed source, semantic rejection, unsupported format, missing option value, unknown option, format option outside run, output option outside compile and simulation option outside simulate | Both runtimes must fail, keep stdout empty and provide stderr; exact wording and numeric exit codes are intentionally not equated |
| `check_csv_parity.py` | 11 files and one synthetic multi-system project | Header, row identity and numeric values; quoting/escaping edge cases are not yet covered by this cross-runtime script |

When a script's input list changes, update this table in the same change. Unit tests and workflow jobs may provide additional evidence; they should be linked separately rather than silently folded into these counts.

## Limits

All fixtures use synthetic values. They do not replace normative examples or missing real datasets in MDES v0.5. Expected behavior is tested by both implementations where the corresponding feature exists.

A traceability ID identifies the intended requirement area; it does not upgrade a matrix status from P/A/N to I. In particular, parser acceptance does not prove semantic validation, solver correctness, or full MDES conformance. The matrix remains authoritative for the status and evidence of each requirement.
