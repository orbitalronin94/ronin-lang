# Shared conformance fixtures

These synthetic RONIN files are a shared input corpus for the Python and Rust implementations. They are separate from examples transcribed from the MDES source.

## Positive fixtures

| File | Purpose |
|---|---|
| pusfre.ronin | Valid PUSFRE project |
| ces.ronin | Valid CES project |
| hill.ronin | Valid Hill project |
| ces_hill.ronin | Valid CES-Hill project |
| full_order1.ronin | Valid full model with first-order memory |

## Negative fixtures

| File | Expected rejection |
|---|---|
| invalid_frequency_sum.ronin | Agent frequencies do not sum to one |
| invalid_pusfre_lambda.ronin | PUSFRE with non-zero lambda |
| invalid_alpha.ronin | Alpha outside the supported range |
| full_order3_unsupported.ronin | Higher-order temporal memory is not implemented |

## Diagnostic fixtures

| File | Expected diagnosis |
|---|---|
| degeneracy_active.ronin | active — narrow positive-frequency range |
| degeneracy_inactive.ronin | inactive — at least three orders of magnitude |
| degeneracy_unknown.ronin | unknown — fewer than two positive frequencies |

All fixtures use synthetic values. They do not replace normative examples or missing real datasets in MDES v0.5. Expected behavior is tested by both implementations where the corresponding feature exists.
