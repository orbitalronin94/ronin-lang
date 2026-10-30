# RONIN 1.1 source coverage and conformance notes

This file maps repository behavior to the supplied **RONIN 1.1 — Edición
Familia** Markdown. It deliberately separates executable code from
architecture proposals and incomplete examples.

## Python reference runtime

| Source section | Repository status |
|---|---|
| R.3–R.4 data model and errors | Implemented in `ronin/model.py` and `ronin/errors.py` |
| R.5–R.6 lexer and parser | Implemented for `system` declarations, inline agents, strings, arrays, comments and numeric literals |
| R.7 validator | Implemented for declared ranges, frequency normalization invariant and model coherence |
| R.8–R.9 semantics and solver | PUSFRE, CES, Hill, CES-Hill, allocation, `k_min`, coexistence threshold and K-alpha range report implemented |
| R.10 simulator | Seeded drift/noise/simplex kernel implemented |
| R.11 diagnose | Omega range, degeneracy state, identifiability flags and recommendation implemented |
| R.12 CLI | `check`, `solve`, `simulate`, `diagnose` implemented |
| R.13 tests | pytest acceptance and regression tests implemented |
| R.14 examples | Runnable Maquinas, Pesca, CES and degeneracy examples included |

## Explicit implementation limits

1. **Debt estimator.** The supplied R.8 Python code defines `debt(system)`
   as `0.0`. No executable estimator is supplied in R.3–R.14. The runtime
   preserves that placeholder and emits a warning; it does not claim to audit
   debt.
2. **Bootstrap.** The source's diagnose implementation explicitly leaves the
   bootstrap fitting pending. The runtime returns `bootstrap_ci: null`.
3. **Temporal memory.** The source defines `memory_order` and `memory_weights`
   and lists `full` as a model, but does not define an executable temporal
   kernel. Order 1 can use the static CES-Hill path; orders above 1 are rejected
   during execution rather than approximated.
4. **NeuralScaling/FamaFrench data.** The supplied examples use `...` rather
   than all 46/720 records. They are not executable data fixtures and no
   observations are fabricated.
5. **Parser language coverage.** The Python parser implements the executable
   `system`-block subset in R.6. It is not a general interpreter for every
   high-level language construct illustrated elsewhere in the document
   (named top-level agents, `let`, loops, conditionals, audit DSL, etc.).

## Source inconsistencies that must be resolved upstream

### Degeneracy inactive fixture

The source's inactive test uses frequencies `0.001, 0.01, 0.989`. Its
actual range is:

`log10(0.989 / 0.001) = log10(989) ≈ 2.9952`

That is below the stated 3.0-order threshold, so the specified algorithm
correctly classifies it as active. The repository preserves this fact in a
regression test and uses `0.0009, 0.0090, 0.9901` for a true inactive fixture.

### NeuralScaling range contradiction

The source's NeuralScaling excerpt includes `phi: 19.2` and `psi: 25.3`,
while R.7 constrains both fields to [0,1]. The example also omits 44 of its
46 records. It cannot pass the declared validator as written.

### CES lambda-to-zero wording

R.8 directs the compatibility branch for `abs(lambda) < 1e-6` to the
PUSFRE product `phi * psi * omega^alpha`. Appendix A.1.1 describes the
mathematical CES limit as a weighted geometric mean. These coincide in the
Maquinas acceptance case (`alpha = 1`) but need not coincide for arbitrary
alpha. The Python runtime follows the explicit R.8 compatibility branch;
the source owner should decide whether that branch or the appendix is
normative for non-unit alpha.

### Coexistence and delta

The source gives the `k_min` formula and says to warn when available resource
is below `k_min`, but does not define a separate debt/coexistence estimator.
The runtime reports `coexistence = resource >= k_min` as the direct threshold
interpretation and exposes `k_min` so callers can inspect the comparison.

## Other implementation targets in the Markdown

- **Rust (Part VI / sections 6.1–6.14):** architecture and code sketches are
  supplied, but the parser is explicitly called a functional skeleton and
  memory/IR/backends are incomplete. No Rust crate is presented as conformant
  by this repository.
- **WASM and C (6.13–6.14):** snippets are extension sketches; the C generator
  contains ellipses and is not a complete compiler backend.
- **RONIN Office (Part VII):** the panels are described with mockups and
  status tables. The Diagnose panel is marked specified/pending. This Python
  repository does not claim to ship the Office UI.
- **JavaScript engine (7.9):** the supplied function contains an ellipsis in
  agent extraction and is illustrative, not a complete parser or conformant
  backend.
- **Future language features (Part VIII and earlier extension chapters):**
  continuous systems, orchestration, optimization, audit DSL and advanced
  constructs remain specification/future work.

## Conformance policy

CI passing means the Python implementation passes the tests and executable
examples in this repository. It does not certify Rust, WASM, C, Office,
bootstrap, debt audit, temporal memory, or datasets that are absent from the
source artifact. No performance benchmark is claimed without a reproducible
benchmark artifact.
