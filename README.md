# RONIN 1.1 — Python reference runtime

Initial executable implementation of the RONIN 1.1 runtime: lexer, parser,
semantic validation, PUSFRE/CES/Hill functions, allocation solver, simulation,
diagnostics, CLI, examples and pytest suite.

## Install

```bash
python -m pip install -e .
pytest
ronin check examples/maquinas.ronin
ronin solve examples/maquinas.ronin
ronin simulate examples/pesca.ronin --steps 100 --seed 42
ronin diagnose examples/pesca.ronin
```

## Maquinas acceptance case

The included fixture is designed to return fitness [0.48, 0.20] and allocation
[70.5882352941, 29.4117647059].

## Scope and limitations

This is an initial reference implementation, not a claim of full formal
conformance. The debt function currently returns a placeholder zero; the
source material's incomplete or ellipsis-based NeuralScaling and FamaFrench
examples are intentionally not represented as runnable fixtures. Review the
equations and model coherence rules against the complete normative text before
treating this implementation as authoritative.
