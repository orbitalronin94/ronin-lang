# Auditoría semántica de evidencia — Runtime v0.5

**Fecha:** 2026-11-03  
**Objeto:** las 62 filas I/P de `docs/conformance-matrix.md`.  
**Resultado:** revisión de evidencia y límites completada por áreas; C1 queda pendiente de CI de esta actualización y de la aprobación separada del perfil Runtime v0.5.

## Método

Para cada fila I/P se contrastaron el comportamiento descrito, el archivo/símbolo citado, el test o script asociado y el límite expresado. Se revisó también que ninguna prueba parser-only se presentara como evidencia de ejecución semántica, que los casos experimentales no se anunciasen como estables y que los estados P/N/A no ocultasen ausencia de implementación o discrepancias normativas.

La revisión usa las pruebas y scripts del repositorio; no es una certificación externa ni demuestra conformidad integral con MDES.

## Cobertura revisada

| Área | Filas I/P | Evidencia contrastada | Resultado |
|---|---|---|---|
| Modelo y CLI | CORE-001/002/003/007/008, VAL-CLI-001, CLI-SELECT-001 | Parser, validator, solver, diagnóstico, selección multi-sistema y 13 rutas de error | Alineado con I/P y límites descritos |
| Sintaxis | LANG-001–005, PARSER-001 | 9 archivos válidos, 3 fuentes inline válidas, 29 inválidas; escapes, Unicode, metadata y rechazos | Alineado; LANG-005 permanece parcial, no es lenguaje de expresiones general |
| Tipos/validación | TYPE-001/003/004/005 | AST/modelos, tipos escalares/compuestos del subconjunto, 13 casos válidos, 10 inválidos y multi-sistema | Alineado; TYPE-003/004/005 permanecen parciales en alcance Rust/tipos generales |
| Concurrencia | CONC-004 | Historial reproducible y simplex en simulador | Parcial correctamente marcado: no existe stream consumible |
| Interoperabilidad | INTEROP-008/009 | IR: 12 válidos/4 rechazos; CSV: 11 proyectos + multi-sistema; tests unitarios de quoting | Alineado; CSV quoting no se presenta como paridad CLI |
| Build/CLI | BUILD-001/007/011/012/013/014 | IR validado, selección solve/run, REPL Python básico, diagnóstico y errores compartidos | Alineado; REPL no se anuncia como lenguaje general |
| Python | PY-001–012, SIM-002/003 | Package/entrypoint, modelos/errores, lexer/parser/validator, solver, simulación, diagnóstico, CLI, regresión y ejemplos | Alineado; PY-006/008/010/011/012 conservan límites explícitos |
| Rust | RS-001–010 | AST/parser, validación integrada, IR, solver, simulación, diagnóstico, CLI y tests runtime | Alineado; RS-003/006/007/008/010 permanecen parciales |
| Anexo normativo | NORM-001/002/003/005/006/008/011 | Tests PUSFRE, CES, k_min, degeneración, coherencia y paridad compartida | Alineado; discrepancias CES/coexistencia/umbral y conformidad global siguen P |
| Ejemplos | EX-001/002/003 I, EX-004 P, EX-005 P | Maquinas, Maquinas CES, Pesca resuelto en ambos runtimes, fixtures sintéticas de degeneración y parser de ejemplos | EX-003 incluye resolución; EX-004 permanece parcial porque el vector literal N.2 Test 6 mide 2.9952 órdenes frente al umbral 3.0; EX-005 es parser-only |

**Total:** 62 filas I/P revisadas. El estado se conserva salvo correcciones ya integradas: NORM-005/P por la heurística de libertad de parámetros, deuda `None/null` en NORM-004/PY-006 y EX-004/P porque los fixtures sintéticos no sustituyen el vector literal de N.2 Test 6. No se elevan estados P a I por añadir más casos de estrés.

## Registro por requisito

El registro se está completando por lotes. **Solo los IDs enumerados a continuación cuentan como revisados individualmente en esta sección**; el resumen por áreas no se contabiliza como auditoría fila a fila. Los estados son los publicados en la matriz y no se elevan por esta revisión.

| ID | Estado P/R | Implementación inspeccionada | Prueba/evidencia inspeccionada | Resultado de la revisión | Límite que se conserva |
|---|---|---|---|---|---|
| LANG-001 | I/I | `ronin/parser.py::Parser.program`; `rust/src/parser.rs::Parser::system` y `parse` | `tests/test_core.py::test_parser_and_pesca_validation`; `examples/maquinas.ronin`, `examples/pesca.ronin`; tests de parser Rust | Ambos parsers construyen declaraciones system; el script compartido incluye los ejemplos Maquinas y Pesca en sus ficheros válidos | La fila acredita declaraciones del subconjunto, no toda la gramática MDES |
| LANG-002 | I/P | `Parser.params` en Python; `Parser::params` en Rust | `tests/test_core.py::test_parser_supports_strings_signed_values_and_memory_arrays`; `tests/test_parser_strictness.py`; `scripts/check_parser_parity.py` | Python cubre parámetros extendidos y tipos; la suite compartida comprueba aceptación/rechazo de parámetros en ambos backends | La matriz conserva P en Rust: esta inspección no amplía cobertura a todos los campos/contratos |
| LANG-003 | I/I | `Parser.agent` y `Parser.number`; `Parser::agent` y `required_number` | `tests/test_core.py::test_parser_supports_strings_signed_values_and_memory_arrays`; `tests/test_parser_strictness.py::test_parser_rejects_booleans_where_numbers_are_required`; casos `boolean_agent_number` del script de paridad | Los tres campos requeridos se extraen como números y se rechazan booleanos en el caso testigo compartido | No se acredita inferencia de tipos ni restricciones semánticas generales del dominio |
| LANG-004 | I/I | `Agent.metadata` y la separación de `phi/psi/frequency`; AST `Agent.metadata` Rust y conversión de valores del parser | `tests/test_agent_metadata.py`; fixture `tests/fixtures/conformance/metadata_nested.ronin`; test Rust `parses_nested_object_metadata` | Metadata anidada se conserva sin sustituir los tres campos estructurales; existe prueba de que añadir metadata no altera el resultado del solver Python | Metadata es dato preservado; no es un sistema de tipos ni una API de extensiones |
| LANG-005 | P/P | `Parser.value` Python y `Parser::value` Rust | `tests/test_agent_metadata.py::test_agent_metadata_preserves_nested_objects_and_mixed_values`; `scripts/check_parser_parity.py::nested_object_and_arrays`; fixture `metadata_nested.ronin` | Arrays y objetos anidados se aceptan en valores/metadata y el caso compartido compara aceptación y nombres de sistemas | Sigue siendo P: arrays/objetos no equivalen a expresiones, llamadas ni estructuras ejecutables generales |
| PARSER-001 | I/I | Lexer/parser Python y lexer/`Parser::parse` Rust | `scripts/check_parser_parity.py`: 9 ficheros válidos, 3 fuentes inline válidas y 29 inválidas; ubicación compartida 2:9 | El script invoca ambas CLIs y compara aceptación/rechazo; para válidos compara también nombres declarados; incluye Unicode, escapes, duplicados, tipos estructurales y whitespace | La comparación no demuestra igualdad de AST completo ni de mensajes; parser-only no acredita semántica de ejecución |

| TYPE-001 | I/I | Valores escalares en `Parser.value` Python y `Parser::value` Rust; tipos `Value` Rust | `tests/test_parser_strictness.py`; `tests/test_agent_metadata.py`; `scripts/check_parser_parity.py` | Casos de número, booleano, cadena y null se preservan/rechazan en contextos estructurales; el script compartido compara ambos parsers | No existe sistema de tipos general; la fila solo cubre escalares en contextos admitidos |
| TYPE-003 | P/P | `Agent`, `Params`, `System` Python; AST `Agent/Params/System/Value` Rust | `tests/test_agent_metadata.py`; `rust/tests/runtime.rs::parser_preserves_nested_agent_metadata_and_optional_parameters` | Existen estructuras compuestas y metadata anidada en ambos runtimes | P permanece: son estructuras de datos internas, no tipos compuestos declarables por el usuario |
| TYPE-004 | I/P | `ronin/validator.py::validate` y `validate_coherence`; `rust/src/solver.rs::validate` | `scripts/check_validation_parity.py` (13 válidos, 10 inválidos y selección multi-sistema); `tests/test_core.py` | Python valida explícitamente antes de resolver; Rust valida durante el camino de solver/check y el script compara aceptación/rechazo | P en Rust se conserva: no se demuestra una fase de validación independiente ni cobertura de todos los contratos de tipos |
| TYPE-005 | I/P | Validación Python de partes, recurso, rangos de agente, suma de frecuencias y parámetros; validación equivalente integrada en Rust solver | `scripts/check_validation_parity.py`; fixtures `invalid_resource_negative.ronin`, `invalid_phi_out_of_range.ronin`, `invalid_gamma.ronin`, `frequency_sum_outside_tolerance.ronin` | Los casos testigo cubren invariantes y comparación de aceptación/rechazo de ambos CLI | P en Rust se conserva; no se acredita el catálogo completo de invariantes MDES ni equivalencia de arquitectura de validación |
| CONC-004 | P/P | `ronin/simulator.py::simulate` y `rust/src/simulator.rs::simulate` | `tests/test_core.py::test_simulation_is_seed_reproducible_and_normalized`; `scripts/check_runtime_parity.py` no cubre por sí solo el historial; la suite dedicada de simulación citada en roadmap es evidencia separada | Hay simulación con historial y pruebas de reproducibilidad/simplex en Python; el runtime Rust expone simulación y tests de semilla | P se conserva: producir historial no implementa una abstracción stream consumible ni backpressure |

**Alcance individual completado en esta actualización: 11 IDs (6 de sintaxis/parser y 5 de tipos/concurrencia).** Los otros IDs I/P siguen pendientes de registro individual; no se reutiliza el total de 62 como si todos hubieran recibido esta inspección.

## Conteos de evidencia confirmados

- Parser: 9 ficheros válidos + 3 fuentes inline válidas + 29 fuentes inline inválidas.
- Validación CLI: 13 fixtures válidos + 10 inválidos, más casos multi-sistema.
- Solver: 11 proyectos del corpus + 80 sistemas deterministas (16 por modelo) + 1 proyecto CES-Hill de 1.000 agentes + rechazo degenerado.
- Simulación: 12 proyectos del corpus + 15 sistemas generados, 24 pasos por sistema y semillas fijas.
- Diagnóstico: 4 fixtures compartidos; `bootstrap_ci` sigue siendo `null` en ambos runtimes.
- IR: 12 fixtures válidos + 4 rechazos.
- CSV: 11 proyectos + un proyecto multi-sistema; quoting CR/LF/comillas se cubre en tests unitarios, no se reclama paridad CLI para esos casos.
- CLI: 13 fallos compartidos; stdout vacío y stderr explicativo, sin exigir texto/códigos idénticos.

## Limitaciones que permanecen correctamente visibles

- `debt` es `None/null`, no cero ni un estimador.
- Bootstrap no está implementado.
- La libertad de K/alpha_h se infiere de valores; la identificabilidad individual sigue provisional hasta ADR-0002.
- CES lambda→0 y N.2 Test 3 requieren ADR-0001.
- N.2 Test 6 usa un vector de 2.9952 órdenes frente al umbral 3.0 (OPEN-002).
- El contrato completo de coexistencia/k_min y los datasets NeuralScaling/FamaFrench siguen incompletos.
- EX-004 usa fixtures sintéticas para verificar los estados; el vector literal de N.2 Test 6 permanece por debajo de 3.0 órdenes y no demuestra el resultado normativo esperado.
- Tipos generales, concurrencia, streams consumibles, imports, funciones, macros y backends no implementados siguen fuera del perfil.
- La prueba de 1.000 agentes es funcional; no constituye benchmark ni claim de rendimiento.

## Gate C1

C1 podrá cerrarse cuando el workflow de trazabilidad pase sobre el commit que contiene esta auditoría y la matriz/profile mantengan las referencias y estados coherentes. La aprobación del perfil es C4, y las decisiones normativas OPEN-* son C3; no se mezclan con el cierre de la auditoría de evidencia.

## Revisión de cierre C1 — 2026-11-10

C1 **permanece abierto**. En una segunda lectura del artefacto se confirma que el resumen por áreas y el párrafo genérico de «Registro por requisito» no exponen una ficha verificable para cada uno de los 62 IDs: no permiten comprobar de forma directa, fila a fila, qué símbolo/test se inspeccionó ni qué conclusión individual se obtuvo. La matriz contiene referencias concretas y el checker comprueba su existencia, pero eso no equivale por sí solo a una auditoría semántica individual.

Antes de cerrar C1, la auditoría debe incorporar un registro por ID con: (1) estado Python/Rust revisado, (2) símbolo o comportamiento de implementación inspeccionado, (3) prueba/fixture/script ejecutado o revisado, (4) resultado observado y (5) límite que impide ampliar la afirmación. Si una fila no recibió esa revisión, debe quedar pendiente y excluirse del total de filas revisadas. No se deben generar conclusiones automáticamente copiando las referencias de la matriz.

Esta revisión no modifica estados de conformidad ni decisiones normativas. C3 (OPEN-*) y C4 (aprobación explícita del perfil) siguen siendo puertas separadas. La CI de documentación tampoco sustituye la inspección semántica.
