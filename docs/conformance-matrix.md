# Matriz de trazabilidad y conformidad — MDES v0.5

**Baseline de implementación:** RONIN Runtime v0.1  
**Fase del roadmap:** v0.2 — Conformance map and test baseline  
**Estado de esta matriz:** primera línea base revisada contra el código y los tests existentes

Esta matriz convierte las secciones de MDES v0.5 en requisitos rastreables. No modifica la especificación ni transforma ejemplos ilustrativos en requisitos ejecutables. Las referencias de sección apuntan a [spec.md](spec.md), [normative-annex.md](normative-annex.md), [python-runtime-spec.md](python-runtime-spec.md), [rust-backend-spec.md](rust-backend-spec.md) y [compiler.md](compiler.md).

## 1. Cómo leer los estados

| Código | Estado | Criterio |
|---|---|---|
| **I** | Implementado y probado | Hay comportamiento ejecutable y una prueba identificable para el alcance descrito |
| **P** | Parcial | Existe implementación, pero solo cubre parte del requisito o carece de cobertura suficiente |
| **D** | Diseño/documentación | Está descrito en MDES, pero no existe implementación ejecutable demostrada |
| **N** | No implementado | No se ha encontrado implementación en el repositorio |
| **A** | Ambiguo/bloqueado | La fuente es contradictoria, incompleta o no permite fijar un resultado verificable |

**Importante:** I no significa que todo el requisito de MDES esté implementado si la fila delimita un subconjunto. No se declara conformidad global de MDES v0.5. Las pruebas de parser no prueban validación semántica ni ejecución.

## 2. Principios y modelo de sistema

| ID | Referencia MDES | Requisito / comportamiento | Python | Rust | Evidencia actual / observaciones |
|---|---|---|---|---|---|
| CORE-001 | §1.1, §2.1 | Declarar sistemas con partes, recurso, agentes y parámetros | I | P | `ronin/parser.py`; `rust/src/parser.rs`; `tests/test_core.py`; tests de parser Rust |
| CORE-002 | §1.2, N.1 | Resolver un sistema y calcular fitness/asignación | I | P | `ronin/solver.py`, `ronin/semantics.py`; `rust/src/solver.rs`; test normativo Maquinas |
| CORE-003 | §1.3, §2.3 | Evaluar coexistencia y umbral `k_min` | P | P | `k_min` y campo coexistence existen; falta cerrar el contrato de coexistencia de la fuente |
| CORE-004 | §1.4, N.1.4 | Estimar deuda del sistema | P | N | Python `debt()` devuelve placeholder `0.0`; no es un estimador. Rust no expone un estimador ni un campo deuda normativo |
| CORE-005 | §1.5 | Calcular geometría del sistema | N | N | No se encontró función ejecutable con contrato de geometría |
| CORE-006 | §1.6 | Calcular fatiga de enrutamiento | N | N | No se encontró implementación ejecutable |
| CORE-007 | §1.7, N.1.5 | Diagnosticar rango Ω y degeneración K–α | I | P | `ronin/diagnose.py`, `rust/src/diagnose.rs`; pruebas de umbral y parámetros no identificables |
| CORE-008 | §2.3, §3.5 | Rechazar combinaciones incoherentes entre modelo y parámetros | I | P | `ronin/validator.py`; `tests/test_core.py::test_model_coherence_is_enforced`; Rust valida a través de solver |

## 3. Sintaxis y construcciones del lenguaje

| ID | Referencia MDES | Requisito / comportamiento | Python | Rust | Evidencia actual / observaciones |
|---|---|---|---|---|---|
| LANG-001 | §2.1 | Parsear declaraciones de sistema | I | I | Parser Python y Rust; fixtures Maquinas/Pesca |
| LANG-002 | §2.2 | Parsear parámetros principales y extendidos | I | P | Defaults, tipos y parámetros soportados; cobertura no idéntica |
| LANG-003 | §2.4 | Parsear campos numéricos del agente | I | I | `phi`, `psi`, `frequency`; tests de parser y solver |
| LANG-004 | §2.5 | Conservar metadatos extendidos del agente | I | I | Python metadata; Rust `Value` incluye arrays/objetos; tests `test_agent_metadata.py` y parser Rust |
| LANG-005 | §2.6 | Parsear arrays y estructuras anidadas en valores admitidos | P | P | Arrays y objetos admitidos en datos/metadata; no equivale a expresiones o estructuras generales del lenguaje |
| LANG-006 | §2.7 | Declarar y evaluar funciones puras RONIN | N | N | No existe parser/evaluador general de funciones |
| LANG-007 | §2.8 | Ejecutar funciones impuras | N | N | No existe runtime general de funciones impuras |
| LANG-008 | §2.9 | Parsear la sintaxis DSL `simulate ... with {...}` | N | N | Simulación disponible como API/CLI, no como sentencia general del lenguaje |
| LANG-009 | §2.10 | Ejecutar DSL de auditoría | N | N | No hay comando/DSL audit ejecutable |
| LANG-010 | §2.11, §6.14 | Parsear sentencia DSL de diagnóstico | N | N | Diagnóstico disponible por CLI Python/API; no se parsea la sentencia de alto nivel |
| LANG-011 | §2.12 | Ejecutar instrucciones `plot` | N | N | No existe motor de visualización RONIN |
| LANG-012 | §2.13 | Parsear y ejecutar condicionales | N | N | No existe intérprete general |
| LANG-013 | §2.14 | Parsear y ejecutar bucles | N | N | No existe intérprete general |
| LANG-014 | §2.15 | Declarar/importar módulos RONIN | N | N | No hay sistema de módulos |
| LANG-015 | §2.16–2.17 | Expandir macros y macros de diagnóstico | N | N | No hay sistema de macros |

## 4. Tipos y validación

| ID | Referencia MDES | Requisito / comportamiento | Python | Rust | Evidencia actual / observaciones |
|---|---|---|---|---|---|
| TYPE-001 | §3.1 | Reconocer escalares numéricos, booleanos, cadenas y null en los contextos soportados | I | I | Lexer/parser y enum Rust `Value`; no implica sistema de tipos general |
| TYPE-002 | §3.2 | Implementar el catálogo completo de más de 160 tipos de dominio | N | N | El runtime usa tipos Python/Rust ordinarios y validaciones explícitas, no el catálogo tipado de MDES |
| TYPE-003 | §3.3 | Implementar tipos compuestos RONIN como tipos del lenguaje | P | P | Estructuras System/Agent/Params en runtime; sin sistema de tipos de usuario |
| TYPE-004 | §3.4 | Comprobar rangos y tipos antes de ejecutar/compilar | I | P | Python validator y compilación validada; Rust valida parcialmente al resolver |
| TYPE-005 | §3.5 | Validar invariantes del sistema (frecuencias, phi/psi, partes, recurso) | I | P | `ronin/validator.py`; pruebas de frecuencia y casos inválidos |
| TYPE-006 | §3.6 | Inferencia de tipos de expresiones | N | N | No existe evaluador de expresiones |
| TYPE-007 | §3.7 | Tipos paramétricos genéricos | N | N | No implementados |
| TYPE-008 | §3.8 | Tipos recursivos | N | N | No implementados |
| TYPE-009 | §3.9 | Tipos dependientes experimentales | N | N | No implementados |

## 5. Concurrencia y paralelismo

| ID | Referencia MDES | Requisito / comportamiento | Python | Rust | Evidencia actual / observaciones |
|---|---|---|---|---|---|
| CONC-001 | §4.1–4.4 | Actores, mensajes, recepción y canales | N | N | No existe modelo de actores/canales en el runtime |
| CONC-002 | §4.5–4.6 | Paralelismo automático y bloque `par` | N | N | No implementado |
| CONC-003 | §4.7–4.8 | Futures, promises y await | N | N | No implementado |
| CONC-004 | §4.9 | Streams de simulación | P | P | La simulación produce historial, pero no existe abstracción de stream consumible |
| CONC-005 | §4.10 | Canales con backpressure | N | N | No implementado |
| CONC-006 | §4.11 | Diagnóstico paralelo | N | N | No existe ejecución paralela de sentencias RONIN |

## 6. Interoperabilidad y formatos

| ID | Referencia MDES | Requisito / comportamiento | Python | Rust | Evidencia actual / observaciones |
|---|---|---|---|---|---|
| INTEROP-001 | §5.1, §5.20 | Importar y ejecutar bibliotecas Python desde RONIN | N | N | No hay puente de interoperabilidad desde el lenguaje |
| INTEROP-002 | §5.2 | Importar crates Rust desde RONIN | N | N | No hay import bridge |
| INTEROP-003 | §5.3–5.7 | SQL, REST, GraphQL, WebSockets y gRPC | N | N | No implementados |
| INTEROP-004 | §5.8 | Leer/escribir formatos de archivo generales desde el lenguaje | N | N | La CLI lee archivos .ronin y escribe artefactos concretos; no existe API DSL general |
| INTEROP-005 | §5.9 | Importar CSV como datos de sistema | N | N | Existe exportación de resultados CSV, no importación CSV al modelo |
| INTEROP-006 | §5.10 | Importar JSON de datos como proyecto/sistema | N | N | La exportación JSON IR no equivale a importar JSON externo como System |
| INTEROP-007 | §5.11–5.19 | YAML, TOML, XML, Protobuf, MsgPack, BSON, Avro, Parquet y Arrow | N | N | No implementados |
| INTEROP-008 | §3.2, §5.10 | Exportar IR JSON versionado | I | P | Python `ronin compile`, `tests/test_compile_ir.py`; Rust baja AST→IR pero no tiene CLI compile/serializador equivalente |
| INTEROP-009 | §5.9 | Exportar resultados a CSV | I | N | Python `ronin run --format csv`; `tests/test_run_csv.py` |

## 7. Compilación, ejecución y herramientas

| ID | Referencia MDES | Requisito / comportamiento | Python | Rust | Evidencia actual / observaciones |
|---|---|---|---|---|---|
| BUILD-001 | Anexo compilador 1–3 | Construir IR normalizado tras validación | I | P | Python IR versionado; Rust lowering AST→IR interno |
| BUILD-002 | §6.1 | Generar ejecutable nativo | N | N | No hay codegen nativo |
| BUILD-003 | §6.2 | Generar WASM | N | N | No hay backend WASM |
| BUILD-004 | §6.3 | Generar C | N | N | No hay backend C |
| BUILD-005 | §6.4 | Generar código Python | N | N | No hay codegen Python |
| BUILD-006 | §6.5–6.8 | LLVM, JVM, .NET y JavaScript codegen | N | N | No implementados |
| BUILD-007 | §6.9 | Ejecutar/resolver proyecto desde CLI | I | P | Python `run` multi-sistema; Rust `run` alias de solve para sistemas parseados |
| BUILD-008 | §6.10 | Niveles de optimización `-O0`…`-O3` | N | N | No hay pipeline de optimización |
| BUILD-009 | §6.11 | Perfilado RONIN | N | N | No hay profiler propio |
| BUILD-010 | §6.12 | Depurador RONIN | N | N | No hay debugger |
| BUILD-011 | §6.13 | REPL general del lenguaje | P | N | Existe consola Python básica; no ejecuta el lenguaje completo |
| BUILD-012 | §6.14 | Comando CLI de diagnóstico | I | P | Python `diagnose`; Rust expone módulo pero no subcomando CLI |
| BUILD-013 | §1, §2, §6 | CLI Python para list/check/solve/simulate/diagnose/run/compile | I | — | `ronin/cli.py`; tests CLI multi-sistema, run, CSV e IR |
| BUILD-014 | §6, Parte VI | CLI Rust `ronin-core` list/check/solve/run | — | I | `rust/src/main.rs`; tests de integración de comandos |

## 8. Runtime de referencia Python — Parte V

| ID | Referencia | Requisito | Estado | Evidencia / límite |
|---|---|---|---|---|
| PY-001 | R.1–R.2 | Paquete, entrypoint y módulo ejecutable | I | `pyproject.toml`, `ronin/__main__.py` |
| PY-002 | R.3–R.4 | Modelos y jerarquía de errores | I | `ronin/model.py`, `ronin/errors.py` |
| PY-003 | R.5 | Lexer con ubicación de errores y tokens soportados | I | `ronin/lexer.py`; tests lexer/escapes/Unicode y números |
| PY-004 | R.6 | Parser del subconjunto system/agent/params | I | `ronin/parser.py`; strictness y examples parser tests |
| PY-005 | R.7 | Validación semántica y coherencia de modelo | I | `ronin/validator.py`; tests de invariantes y combinaciones inválidas |
| PY-006 | R.8–R.9 | Semántica CES-Saturada y solver | P | PUSFRE/CES/Hill/CES-Hill; `debt()` sigue placeholder y existen discrepancias normativas |
| PY-007 | R.10 | Simulador con semilla reproducible | I | `ronin/simulator.py`; tests de normalización, semilla y sigma=0 |
| PY-008 | R.11 | Diagnóstico K–α y bootstrap CI | P | Rango/degeneración implementados; bootstrap devuelve null |
| PY-009 | R.12 | CLI de referencia | I | `ronin/cli.py`; list/check/solve/simulate/diagnose/run/compile/repl |
| PY-010 | R.13 | Tests normativos y regresión | P | Suite pytest existente; faltan vectores completos para todos los requisitos MDES |
| PY-011 | R.14 | Ejemplos ejecutables y datasets completos | P | Maquinas, Pesca, CES y degeneración; ejemplos 101–130 tienen plantillas; cuerpos 1–100 ausentes |
| PY-012 | R.15–R.16 | Arquitectura y conformidad integral del runtime | P | Arquitectura modular presente; conformidad integral no demostrada |

## 9. Backend Rust — Parte VI

| ID | Referencia | Requisito | Estado | Evidencia / límite |
|---|---|---|---|---|
| RS-001 | 6.2 | AST y modelos de datos | I | `rust/src/ast.rs`; metadata y Value anidados |
| RS-002 | 6.3–6.4 | Lexer/parser de proyectos soportados | I | `rust/src/parser.rs`; tests de sintaxis, escapes, Unicode y objetos |
| RS-003 | 6.5 | Validación semántica | P | Validación integrada en solver; no cubre el validador completo de MDES |
| RS-004 | 6.6 | Lowering a IR | I | `rust/src/ir.rs`; tests de campos y metadata |
| RS-005 | 6.6 | Serializar IR con contrato JSON idéntico a Python | N | No existe comando Rust `compile` ni serializador de IR público |
| RS-006 | 6.7 | Solver PUSFRE/CES/Hill | P | `rust/src/solver.rs`; tests Hill/CES/Maquinas/validación y corpus compartido de cinco modelos; paridad completa no demostrada |
| RS-007 | 6.8 | Simulador Rust | P | `rust/src/simulator.rs`; tests de semilla reproducible, simplex y steps inválidos; necesita vectores cruzados de conformidad |
| RS-008 | 6.9 | Diagnóstico Rust | P | `rust/src/diagnose.rs`; tests de degeneración activa/inactiva/unknown y fixtures compartidos; bootstrap no implementado |
| RS-009 | 6.10 | CLI Rust list/check/solve/run | I | `rust/src/main.rs`; tests de comandos |
| RS-010 | 6.11 | Suite normativa Rust completa | P | Tests unitarios/parser/CLI presentes; no cubren todas las normas MDES |
| RS-011 | 6.12 | Bindings Python con PyO3 | N | No existe crate/binding PyO3 en el workspace actual |
| RS-012 | 6.13 | Backend WASM | N | No implementado |
| RS-013 | 6.14 | Backend C | N | No implementado |

## 10. Anexo normativo N.1–N.5

| ID | Referencia | Requisito | Estado | Evidencia / límite |
|---|---|---|---|---|
| NORM-001 | N.1 pasos 1–4 | Parsear, validar tipos/rangos/agentes y coherencia de modelo | P | Python implementa el subconjunto; Rust parcial |
| NORM-002 | N.1 pasos 5–7 | Calcular Hill/CES fitness y asignación | P | Modelos ejecutables, pero discrepancia de límite CES pendiente |
| NORM-003 | N.1 paso 8 | Calcular coexistencia y k_min | P | Fórmula k_min y comparación disponibles; contrato de coexistencia requiere cierre |
| NORM-004 | N.1 paso 9 | Calcular deuda | N | Placeholder 0.0 no satisface estimación normativa |
| NORM-005 | N.1 pasos 10–11 | Rango Ω, degeneración y advertencias | I | Pruebas de umbral y diagnóstico |
| NORM-006 | N.2 Tests 1–2 | Compatibilidad Maquinas y PUSFRE explícito | I | `tests/test_core.py::test_maquinas_normative_result`, `test_explicit_pusfre_matches_legacy_default` |
| NORM-007 | N.2 Test 3 | CES con lambda→0 recupera PUSFRE | A | La prueba implementada sigue media geométrica; el anexo pide equivalencia PUSFRE. Requiere decisión normativa, no un cambio silencioso |
| NORM-008 | N.2 Test 4 | Rechazar modelo/parámetros incoherentes | I | `test_explicit_pusfre_matches_legacy_default`, `test_model_coherence_is_enforced`; Rust `rejects_model_parameter_incoherence` |
| NORM-009 | N.2 Tests 5–6 | Detectar degeneración activa/inactiva | I | `test_degeneracy_active_for_narrow_omega_range`, `test_degeneracy_inactive_requires_three_full_orders`; Rust solver tests cubren el cálculo de fitness y errores |
| NORM-010 | N.2 Test 7 | Diagnóstico del dataset Neural Scaling real | A | Datos fuente incompletos y valores phi/psi fuera del rango normativo |
| NORM-011 | N.3 | Cumplimiento integral de tolerancias, simulación y requisitos | P | Hay pruebas parciales; no procede declarar conformidad global |

## 11. Fixtures compartidos de conformidad

El corpus sintético `tests/fixtures/conformance/` se ejecuta tanto en Python como en Rust: cinco perfiles positivos (PUSFRE, CES, Hill, CES-Hill y full/order 1), cuatro casos negativos y tres diagnósticos compartidos. Su catálogo está en `tests/fixtures/conformance/README.md`. No reemplaza los datasets normativos ausentes ni resuelve contradicciones de MDES.

## 12. Ejemplos y datos de aceptación

| ID | Referencia | Estado | Qué demuestra y qué no demuestra |
|---|---|---|---|
| EX-001 | R.14, §8.1 | I | Maquinas: resultado PUSFRE de aceptación, solver y asignación |
| EX-002 | R.14, §8.2 | I | Maquinas CES: ejecución de la variante CES |
| EX-003 | R.14, §8.1 | I | Pesca: parseo y validación del fixture |
| EX-004 | N.2 Tests 5–6 | I | Fixtures degeneración activa/inactiva con rango medido |
| EX-005 | Ejemplos 101–130 | P | `tests/test_examples.py` prueba parseo de todos los ficheros; no prueba ejecución semántica |
| EX-006 | Ejemplos 1–100 | A | Los cuerpos no están en el Markdown maestro disponible |
| EX-007 | §8.3, §8.9 | A | NeuralScaling/FamaFrench carecen de registros completos; no son datasets de aceptación |
| EX-008 | §8.4–8.8 | D | Casos descritos en MDES sin fixtures completos y verificados para el runtime |

## 13. Discrepancias y bloqueos que requieren decisión

| ID | Fuente | Problema | Tratamiento en la línea base |
|---|---|---|---|
| OPEN-001 | Apéndice CES A.1.1 vs N.2 Test 3 / R.8 | El límite geométrico CES no es, en general, idéntico a PUSFRE | Se conserva el comportamiento geométrico actual; bloqueado para conformidad normativa |
| OPEN-002 | N.2 Test 6 | Frecuencias 0.001, 0.01, 0.989 producen ~2.9952 órdenes, no 3.0 | El fixture de test usa datos que sí superan el umbral; la fuente queda señalada |
| OPEN-003 | §8.3 / R.14 | NeuralScaling contiene phi/psi > 1 y dataset incompleto | No se fuerza el fixture contra el validador |
| OPEN-004 | §8.9 / R.14 | FamaFrench no contiene los 720 registros prometidos | Dataset pendiente; no sintetizar observaciones |
| OPEN-005 | R.16 vs anexo | R.16 referencia N.6, pero el anexo disponible termina en N.5 | Se registra como discrepancia editorial |
| OPEN-006 | §2.2 / §3.2 | Catálogo extenso de tipos sin implementación de sistema de tipos | No declarar tipos de dominio completos |
| OPEN-007 | N.1.4 | Contrato de deuda remite a contenido "sin cambios" no reproducido aquí | Requiere fuente normativa íntegra antes de implementar |

## 14. Criterios para cerrar v0.2

Esta primera matriz es la línea base, no el cierre del hito. v0.2 podrá declararse completada cuando:

- [ ] Cada requisito del perfil v1.0 tenga un ID estable y una referencia exacta a MDES.
- [ ] Cada fila I/P tenga al menos una prueba o una explicación explícita de por qué no es automatizable.
- [ ] Los tests se separen en parser-only, validación, solver, simulación, CLI e interoperabilidad.
- [ ] Los casos normativos N.2 tengan resultado esperado, prueba ejecutable o bloqueo documentado.
- [ ] CI publique el resultado de las suites Python y Rust por separado.
- [ ] Los ejemplos incompletos se excluyan expresamente de la aceptación de ejecución.
- [ ] Las discrepancias OPEN-* tengan responsable/decisión o permanezcan fuera del perfil estable.
- [ ] Se defina el denominador del perfil de conformidad antes de publicar cualquier porcentaje.

**No se publica un porcentaje global todavía.** La matriz mezcla requisitos normativos, construcciones de lenguaje, propuestas de plataforma y ejemplos; primero hay que aprobar qué subconjunto constituye el perfil de v1.0. Contar todas las filas por igual daría una métrica engañosa.

## 15. Relación con el roadmap

- v0.2: esta matriz y la suite de conformidad trazable.
- v0.3: paridad Python/Rust y serialización IR equivalente.
- v0.4: decisiones normativas para deuda, bootstrap, memoria y discrepancias matemáticas.
- v0.5+: ampliación del perfil de lenguaje, interoperabilidad, herramientas y robustez.

