# RONIN compiler architecture (English companion)

This is an English summary of [the complete Spanish compiler annex](compiler.md).

The proposed compiler architecture is organized as a frontend (parser, semantic validation and AST), middle-end (intermediate representation and optimizations), and backend (code generation for selected targets). The annex describes IR structures, K-min/coexistence checks, K–alpha degeneracy diagnostics, equation simplification, invariant detection, command fusion, vectorization, backend extension points, new domain types, command registration, compile-time macros and contributor workflow.

This document is architectural guidance. It does not claim that all listed backends or optimizations are implemented in the current Python repository.
