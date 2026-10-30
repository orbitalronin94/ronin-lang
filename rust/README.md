# Esqueleto Rust de RONIN 1.1

Este directorio inicia el workspace de Cargo y refleja los módulos principales descritos en la Parte VI del documento maestro.

## Estado

- AST y estructuras de salida: tipos mínimos en `ast.rs`.
- IR: estructura y punto de entrada de lowering.
- Solver, simulador y diagnóstico: firmas públicas con `todo!()` para implementación futura.
- CI ejecuta `cargo check` para verificar que el esqueleto compila.

Esto **no** es todavía el compilador ni runtime Rust conforme. No se han añadido dependencias externas en esta fase.


## Especificación completa

La Parte VI original (secciones 6.1–6.14, incluidos AST, lexer/parser, validador, IR, solver, simulador, diagnóstico, CLI, tests, PyO3, WASM y C) se conserva en [`docs/rust-backend-spec.md`](../docs/rust-backend-spec.md). El workspace actual sigue siendo un esqueleto: `todo!()` y las integraciones opcionales no se presentan como implementadas. La especificación describe el destino, no el estado ejecutable actual.
