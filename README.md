# RONIN 1.1 — Runtime de referencia en Python

**Documentación principal en castellano. English version follows below.**

RONIN 1.1 es un lenguaje y runtime de modelización descrito en *RONIN 1.1 — Edición Familia*. Este repositorio contiene una implementación de referencia en Python de la parte ejecutable: modelo de datos, lexer, parser, validación semántica, funciones de fitness, asignación de recursos, simulación, diagnóstico, CLI y pruebas.

## Instalación y primeros pasos

```bash
python -m pip install -e .
pytest -q
ronin check examples/maquinas.ronin
ronin solve examples/maquinas.ronin
ronin simulate examples/pesca.ronin --steps 100 --seed 42
ronin diagnose examples/pesca.ronin
python -m ronin solve examples/maquinas.ronin
```

## Caso de aceptación: Maquinas

El ejemplo normativo `examples/maquinas.ronin` debe producir:

- Fitness: `[0.48, 0.20]`
- Asignación: `[70.5882352941, 29.4117647059]`
- Modelo: `pusfre`

La asignación se normaliza respecto al recurso configurado. CI ejecuta las pruebas en Python 3.9–3.12 y comprueba este caso de aceptación.

## Documentación y manuales

**¿Es tu primera vez con RONIN? Empieza por el [Manual para principiantes — Tutorial para mortales](docs/tutorial.md).** Explica desde cero qué es un sistema, cómo declarar agentes y recursos, cómo resolver tu primer modelo y cómo interpretar los resultados. No necesitas empezar leyendo la especificación formal.

Rutas de lectura:

1. [Manual para principiantes (castellano)](docs/tutorial.md) · [Beginner tutorial (English companion)](docs/tutorial.en.md)
2. [Índice completo de documentación](docs/README.md)
3. [Especificación formal del lenguaje](docs/spec.md)
4. [Arquitectura y extensión del compilador](docs/compiler.md)
5. [Familia matemática CES-Saturada](docs/family.md)
6. [Runtime Python: especificación y comportamiento](docs/python-runtime-spec.md)
7. [Cobertura de la fuente, conformidad y límites conocidos](docs/source-coverage.md)

El castellano es el idioma principal; los archivos `.en.md` son resúmenes de acompañamiento en inglés.

## Qué está implementado

- Lexer con ubicación línea/columna, cadenas, literales numéricos, comentarios y el símbolo `∞`.
- Parser para declaraciones `system`, agentes en línea y bloques `params`.
- Validación de rangos, suma de frecuencias y coherencia entre modelos.
- Rutas de fitness PUSFRE, CES, Hill y CES-Hill.
- Media CES ponderada, incluido el límite geométrico cuando λ tiende a cero.
- Asignación de recursos, umbral `k_min` y simulación reproducible con semilla.
- Diagnóstico del rango Ω y degeneración K–α.
- CLI: `check`, `solve`, `simulate` y `diagnose`.

## Prototipos y límites conocidos: lo que todavía no está terminado

No presentamos como terminado lo que el documento fuente deja como propuesta o pendiente:

- `debt()` conserva el placeholder `0.0`: el documento no define un estimador ejecutable de deuda.
- Los intervalos de confianza bootstrap siguen pendientes; `bootstrap_ci` devuelve `null`.
- La memoria temporal de orden superior a 1 no tiene un kernel normativo implementado y se rechaza en ejecución.
- Los ejemplos NeuralScaling y FamaFrench del documento contienen puntos suspensivos, no los conjuntos completos. No inventamos observaciones.
- Rust contiene un runtime parcial con solver CES/Hill, asignación, IR, simulación R.10, diagnóstico y pruebas; siguen pendientes lexer/parser, CLI, bindings externos y memoria temporal.
- [RONIN Office](office/index.html) incluye prototipos locales de Chat determinista, Sheet CSV, barrido heurístico, Simulator R.10, Agent Studio y Diagnose; no es todavía la suite completa.
- WASM y C siguen siendo propuestas; no son backends completos.
- Los ejemplos 101–130 se han incorporado como declaraciones extraídas o plantillas parser-only. Los ejemplos 1–100 no aparecen en el Markdown entregado.

## Conformidad y discrepancias de la especificación

Consulta [la cobertura de la fuente y las notas de conformidad](docs/source-coverage.md). El Markdown original está archivado en [docs/source/RONIN_1.1_Edicion_Familia.md](docs/source/RONIN_1.1_Edicion_Familia.md), con su aviso de licencia separado en [docs/source/NOTICE.md](docs/source/NOTICE.md). Las Partes VI–VIII y el anexo normativo también están separados en [docs/README.md](docs/README.md).

## Contribuir a RONIN

Queremos una comunidad técnica que pueda leer, debatir, probar y documentar RONIN en castellano. Las incidencias, propuestas, ejemplos y documentación en español son bienvenidos. Para facilitar la colaboración internacional, añadimos traducción al inglés después del contenido principal en castellano. Si detectas una discrepancia matemática, aporta la fórmula, un ejemplo mínimo y el resultado esperado.

---

# RONIN 1.1 — Python reference runtime (English)

RONIN 1.1 is a modeling language and runtime described in *RONIN 1.1 — Edición Familia*. This repository provides a Python reference implementation of the executable subset: data model, lexer, parser, semantic validation, fitness functions, resource allocation, simulation, diagnostics, CLI and tests.

## Install and run

```bash
python -m pip install -e .
pytest -q
ronin check examples/maquinas.ronin
ronin solve examples/maquinas.ronin
ronin simulate examples/pesca.ronin --steps 100 --seed 42
ronin diagnose examples/pesca.ronin
```

## Acceptance case: Maquinas

The normative `examples/maquinas.ronin` fixture must produce fitness `[0.48, 0.20]` and allocation `[70.5882352941, 29.4117647059]`. CI tests Python 3.9–3.12.

## Implemented scope

The repository includes the lexer/parser subset, validation, PUSFRE/CES/Hill/CES-Hill fitness, the geometric CES limit near zero lambda, resource allocation, `k_min`, seeded simulation, K–alpha diagnostics and the four CLI commands.

## Known limitations

Debt estimation remains a `0.0` placeholder; bootstrap confidence intervals return null; higher-order temporal memory has no executable kernel; and NeuralScaling/FamaFrench source datasets are incomplete. Rust now has a partial solver, IR lowering, simulator and diagnostics, but no Rust parser, CLI or foreign bindings. Office has local prototypes for its main panels, not the complete collaborative suite. WASM, C and the full JavaScript engine remain unfinished. See the Spanish-first [documentation index](docs/README.md) and [source coverage and conformance notes](docs/source-coverage.md).
