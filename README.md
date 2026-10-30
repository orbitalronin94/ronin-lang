# RONIN 1.1 — Python reference runtime

Python reference implementation of the executable runtime described in
**RONIN 1.1 — Edición Familia**. The implementation follows the source's
R.3–R.14 data model, parser, semantic validation, solver, simulator,
diagnostics, CLI, examples and acceptance tests.

## Install and run

```bash
python -m pip install -e .
pytest -q
ronin check examples/maquinas.ronin
ronin solve examples/maquinas.ronin
ronin simulate examples/pesca.ronin --steps 100 --seed 42
ronin diagnose examples/pesca.ronin
python -m ronin solve examples/maquinas.ronin
```

## Normative acceptance case

`examples/maquinas.ronin` must return:

- fitness: `[0.48, 0.20]`
- allocation: `[70.5882352941, 29.4117647059]`
- model: `pusfre`

The allocation is normalized to the configured resource. The CI matrix runs
the tests on Python 3.9–3.12 and executes the Maquinas CLI acceptance example.

## Implemented in this repository

- Lexer with line/column locations, strings, signed numeric literals and comments.
- Parser for `system`, inline agents and extended `params` blocks.
- Range, frequency-sum and model-coherence validation.
- PUSFRE, CES, Hill and CES-Hill fitness paths.
- Resource allocation and the documented `k_min` threshold.
- Seeded drift/noise/simplex simulation.
- K–alpha range diagnostic and JSON CLI commands.

## Explicitly incomplete or specified-only

The source document distinguishes normative implementation from proposals and
placeholders. This repository does not misrepresent those as completed:

- `debt()` returns the source runtime's placeholder `0.0`; no executable debt
  estimator is defined in the supplied runtime section.
- Bootstrap confidence intervals are specified in the UI but the source code
  explicitly leaves the estimator pending; `diagnose --bootstrap` therefore
  returns `bootstrap_ci: null`.
- `model: "full"` with temporal memory orders above 1 is parsed and validated
  but execution is rejected until a normative memory kernel exists.
- NeuralScaling and FamaFrench examples in the source contain ellipses rather
  than complete datasets. They are documented as templates, not executable
  fixtures. The NeuralScaling excerpt also uses `phi`/`psi` values above the
  validator's declared [0,1] range; that contradiction is recorded in
  `docs/source-coverage.md`.
- Rust, WASM, C and RONIN Office are architecture/proposal sections in the
  supplied document, not complete, testable implementations in this Python
  runtime repository.

## Source discrepancies tracked

See [docs/source-coverage.md](docs/source-coverage.md) for the exact source
conflicts preserved rather than silently guessed or rewritten.
