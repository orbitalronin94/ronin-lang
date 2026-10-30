# Rust backend specification — English companion

The full Spanish source transcription is [`rust-backend-spec.md`](rust-backend-spec.md). It covers the intended Rust project layout and the AST, lexer, parser, semantic validator, IR, solver, simulator, diagnostics, CLI, normative tests, PyO3, WASM, and C backends.

This file documents the target architecture, not a claim of completion. The repository now implements AST-to-IR lowering, validation, Hill/CES fitness, allocation, coexistence threshold, seeded R.10 simulation, and degeneracy diagnosis with regression tests. The Rust lexer/parser, CLI, PyO3/WASM/C bindings, and temporal-memory execution remain unfinished, so this is not yet a complete conforming runtime.
