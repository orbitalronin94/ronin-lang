# Esqueleto Rust de RONIN 1.1

Este directorio inicia el workspace de Cargo y refleja los módulos principales descritos en la Parte VI del documento maestro.

## Estado

- AST y estructuras de salida: tipos mínimos en `ast.rs`.
- IR: estructura y punto de entrada de lowering.
- Solver, simulador y diagnóstico: firmas públicas con `todo!()` para implementación futura.
- CI ejecuta `cargo check` para verificar que el esqueleto compila.

Esto **no** es todavía el compilador ni runtime Rust conforme. No se han añadido dependencias externas en esta fase.
