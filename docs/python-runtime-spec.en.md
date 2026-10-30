# Python reference runtime specification — English companion

The full source transcription is available in Spanish at [python-runtime-spec.md](python-runtime-spec.md). Part V (R.1–R.16) documents the reference Python runtime: module structure, data model, errors, lexer, parser, semantic validator, mathematical semantics, solver, simulator, diagnostics, CLI, acceptance examples, architecture, and conformance requirements.

The repository implements the executable subset in `ronin/`. Some source contracts remain placeholders or incomplete: debt estimation is zero-valued, bootstrap intervals are not fitted, temporal memory beyond order 1 is rejected, and the parser is not a general-purpose interpreter for every high-level construct in the language. Consult [source coverage](source-coverage.md) before treating a specification claim as an implemented capability.
