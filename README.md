# RONIN Runtime v0.1

**Implementación inicial del lenguaje RONIN basada en la especificación completa MDES v0.5.** La documentación canónica se mantiene primero en castellano.

RONIN Runtime **v0.1** es una versión temprana y funcional: incluye un runtime de referencia en Python, un núcleo/CLI en Rust en desarrollo, herramientas de validación y resolución, exportación de resultados y compilación Python a JSON IR. No representa todavía la implementación completa de MDES v0.5.

> **Versionado del proyecto:** v0.1 identifica el estado del software. **MDES v0.5** identifica la versión de la especificación de diseño. Son versiones independientes. El material fuente conserva sus rótulos editoriales originales cuando corresponde.

## Instalación y primeros pasos

```bash
python -m pip install -e .
pytest -q
ronin list examples/maquinas.ronin
ronin check examples/maquinas.ronin
ronin solve examples/maquinas.ronin
ronin run examples/maquinas.ronin
ronin run examples/maquinas.ronin --format csv
ronin compile examples/maquinas.ronin
```

Para Rust, desde el directorio `rust/`:

```bash
cargo test
cargo run -- check ../examples/maquinas.ronin
cargo run -- solve ../examples/maquinas.ronin
cargo run -- run ../examples/maquinas.ronin --format csv
cargo run -- diagnose ../tests/fixtures/conformance/degeneracy_active.ronin
cargo run -- simulate ../examples/maquinas.ronin --steps 100 --seed 42
cargo run -- compile ../examples/maquinas.ronin -o ../maquinas.ir.json
```

Desde la raíz del repositorio, comprobar paridad entre Python y Rust:

```bash
python scripts/check_ir_parity.py
python scripts/check_runtime_parity.py
python scripts/check_simulation_contracts.py
python scripts/check_diagnostic_parity.py
python scripts/check_csv_parity.py
python scripts/check_validation_parity.py
python scripts/check_cli_selection_parity.py
python scripts/check_csv_parity.py
```

## Qué incluye v0.1

### Runtime y CLI Python
- Lexer, parser y validación semántica del subconjunto ejecutable.
- Resolución de modelos PUSFRE, CES, Hill y CES-Hill.
- Asignación de recursos, umbral `k_min`, simulación reproducible y diagnóstico.
- CLI para `list`, `check`, `solve`, `simulate`, `diagnose`, `run` y `compile`.
- Ejecución multi-sistema y exportación JSON/CSV.
- Compilación validada a JSON IR normalizado.

### Núcleo y CLI Rust
- Lexer/parser para la sintaxis de proyectos actualmente soportada.
- CLI `ronin-core` (binario Cargo por defecto) con `list`, `check`, `solve`, `run` (JSON/CSV), `compile`, `diagnose` y `simulate`.
- Conservación de metadatos escalares, arrays y objetos anidados.
- Parámetros extendidos y lowering AST→IR con estructuras alineadas con Python.

### Caso de aceptación: Maquinas

El fixture `examples/maquinas.ronin` es la referencia de aceptación principal:
- Fitness: `[0.48, 0.20]`
- Asignación: `[70.5882352941, 29.4117647059]`
- Modelo: `pusfre`

## Especificación de referencia

La especificación completa de diseño se identifica en este proyecto como **MDES v0.5**. Consulta el [índice de documentación](docs/README.md), la [especificación formal](docs/spec.md), el [anexo normativo](docs/normative-annex.md), la [matriz de trazabilidad MDES v0.5](docs/conformance-matrix.md) y las [notas de cobertura](docs/source-coverage.md).

El documento maestro de origen conserva algunas etiquetas editoriales de su edición original. MDES v0.5 es la etiqueta de referencia adoptada para el ciclo de desarrollo; no se han reescrito silenciosamente las fórmulas ni se han rellenado lagunas del material fuente.

## Roadmap hacia v1.0

La hoja de ruta completa, con fases y criterios de salida verificables, está en **[docs/roadmap.md](docs/roadmap.md)**. La línea base de v0.2 está en la [matriz de trazabilidad y conformidad](docs/conformance-matrix.md); todavía no publicamos un porcentaje global porque falta aprobar el perfil de conformidad v1.0.

| Hito | Objetivo |
|---|---|
| v0.1 | Base ejecutable, Python + parser/CLI Rust iniciales |
| v0.2 | Conformidad y cobertura de la especificación |
| v0.3 | Paridad funcional Python/Rust y JSON IR |
| v0.4 | Cierre de semánticas pendientes con decisiones normativas |
| v0.5 | Cobertura del lenguaje y fixtures de referencia |
| v0.6 | Interoperabilidad y bindings estables |
| v0.7 | Herramientas de autoría y Office MVP |
| v0.8 | Rendimiento, robustez y seguridad |
| v0.9 | Release candidate y congelación de interfaces |
| v1.0 | Primera versión estable y conforme al perfil publicado |

Los hitos son objetivos de ingeniería, no afirmaciones de funcionalidades ya entregadas ni fechas comprometidas.

## Límites conocidos de v0.1

- `debt()` continúa siendo un placeholder `0.0`; no existe un estimador normativo ejecutable.
- Los intervalos bootstrap siguen pendientes y se devuelven como `null`.
- La memoria temporal de orden superior a 1 no tiene kernel ejecutable.
- Rust todavía no ofrece paridad completa con Python; la simulación usa un RNG diferente y no produce las mismas trayectorias bit a bit.
- WASM, C, bindings externos y la suite completa RONIN Office no están terminados.
- Algunos ejemplos y datasets de la fuente están incompletos. No se inventan los cuerpos ausentes de los ejemplos 1–100 ni los datos omitidos.

Consulta [source coverage](docs/source-coverage.md) para los límites y discrepancias concretos. Una CI verde certifica únicamente las pruebas que ejecuta; no certifica automáticamente toda MDES v0.5.

## Contribuir

Se agradecen incidencias, propuestas, ejemplos y documentación en castellano. Para cambios matemáticos o normativos, incluye la sección de MDES v0.5 afectada, la fórmula, un caso mínimo y el resultado esperado.

---

# RONIN Runtime v0.1 (English summary)

RONIN Runtime v0.1 is an early, usable implementation based on the complete MDES v0.5 design specification. The software version and specification version are independent.

The repository includes a Python reference runtime and CLI, plus an evolving Rust parser/core/CLI. Python supports validation, solving, simulation, diagnostics, multi-system runs, JSON/CSV output and validated JSON IR compilation. Rust supports the currently implemented project syntax, metadata preservation and list/check/solve/run commands.

This release is **not yet fully conformant** with MDES v0.5. Debt estimation, bootstrap confidence intervals, higher-order temporal memory, complete Rust parity, external bindings, WASM/C and the full Office suite remain unfinished. See the [roadmap](docs/roadmap.md), [documentation index](docs/README.md) and [coverage notes](docs/source-coverage.md).
