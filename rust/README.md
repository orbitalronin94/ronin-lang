# Runtime Rust parcial de RONIN 1.1

Este directorio inicia el workspace de Cargo y refleja los módulos principales descritos en la Parte VI del documento maestro.

## Estado

- AST y estructuras de salida: tipos base en `ast.rs`.
- IR: lowering AST → IR implementado.
- Solver: validación de parámetros, Hill, CES, asignación, `k_min` y estado de degeneración implementados.
- Simulator: deriva R.10, ruido gaussiano con RNG local reproducible y proyección al símplex implementados.
- Diagnose: rango Ω, estado, identificabilidad y recomendación implementados; bootstrap continúa sin ajuste estadístico.
- Pruebas Rust: caso Maquinas, proyección, reproducibilidad, diagnóstico y rechazo de memoria temporal.
- CI ejecuta `cargo test` y `cargo check`.

Esto ya no es solo un esqueleto, pero **no** es todavía el compilador Rust completo ni un runtime conforme: no hay lexer/parser, validador independiente, CLI ni bindings PyO3/WASM/C. La memoria temporal sigue rechazada. La implementación no depende de crates externos.


## Especificación completa

La Parte VI original (secciones 6.1–6.14, incluidos AST, lexer/parser, validador, IR, solver, simulador, diagnóstico, CLI, tests, PyO3, WASM y C) se conserva en [`docs/rust-backend-spec.md`](../docs/rust-backend-spec.md). El workspace actual sigue siendo un esqueleto: `todo!()` y las integraciones opcionales no se presentan como implementadas. La especificación describe el destino, no el estado ejecutable actual.
