# Plan de salida — RONIN Runtime v0.5

**Objetivo:** llegar a una versión publicable `RONIN Runtime v0.5.0`, con alcance explícito, evidencia reproducible y CI verde.  
**Base de trabajo:** `main` en `1513d317d9381b5696026b0c722bf21a07ff2f7d` (2026-11-03).  
**Especificación de referencia:** MDES v0.5.  
**Distinción de versiones:** este plan prepara el *runtime* v0.5.0; no renumera ni declara completa MDES v0.5.

## Regla de salida

RONIN Runtime v0.5.0 solo se declara cuando todos los checkpoints obligatorios están cerrados. Un commit, una PR fusionada o una CI verde aislada no equivalen a conformidad. El release debe anunciar un perfil implementado y probado, con exclusiones visibles. No se afirmará conformidad integral con MDES v0.5 mientras existan requisitos fuera de alcance, ambiguos o no implementados.

Los elementos que dependan de una decisión normativa del autor se preparan como ADR/propuesta y permanecen bloqueados hasta aprobación expresa. No se inventan fórmulas, datasets ni semántica para hacer avanzar el porcentaje.

## Checkpoints

| ID | Checkpoint | Salida verificable | Estado inicial |
|---|---|---|---|
| C0 | Baseline y gobierno del release | Rama de trabajo, SHA base, CI actual, PR/issues y alcance de v0.5 registrados | **Completado** |
| C1 | Cierre de evidencia v0.2 | Cada requisito del perfil candidato tiene estado correcto, evidencia concreta y referencias válidas; matriz y catálogo se validan en CI | En curso |
| C2 | Contrato compartido v0.3 | CLI, errores, selección, CSV, IR y comportamiento Python/Rust cubiertos por pruebas de integración/paridad; diferencias intencionadas documentadas | **Completado para el contrato documentado** |
| C3 | Decisiones normativas v0.4 | OPEN-001…OPEN-007 resueltos por fuente/ADR aprobado o excluidos explícitamente del perfil; ningún placeholder se presenta como resultado | Bloqueado por decisiones/fuentes |
| C4 | Lenguaje y perfil candidato v0.5 | Subconjunto léxico/sintáctico reproducible; perfil de runtime v0.5 delimitado, revisado y aprobado; parser-only separado de validación/ejecución | Propuesta de perfil Runtime v0.5 fusionada en PR #86; aprobación explícita pendiente |
| C5 | Núcleo matemático y diagnósticos | Funcionalidades seleccionadas de investigación con definición, fixtures y paridad; el resto se marca experimental/no incluido | **Completado para alcance v0.5:** PR #89 fusionada; 80 casos solver + 15 trayectorias simuladas; APIs FIM/SIR/D-óptimo/Sobol excluidas explícitamente |
| C6 | Robustez y distribución | Instalación limpia, ejemplos ejecutables, pruebas de límites/errores, política de dependencias y artefactos reproducibles para plataformas declaradas | **En validación:** quickstart/smoke CLI existente; wheel Python aislado y Rust release `--locked` añadidos en esta rama; falta CI integrada |
| C7 | Release candidate | Alcance congelado; matriz de compatibilidad, migración, documentación, suite completa y CI en verde en commit candidato | Pendiente |
| C8 | Declaración v0.5.0 | Tag/release, notas, artefactos, hashes y limitaciones publicados; ningún bloqueo crítico abierto | Pendiente |

## Criterios detallados

### C0 — Baseline y gobierno (completado)

- Se fijó como base el commit indicado arriba.
- La ejecución de CI de `main` #41681956356 terminó en `success`.
- Se registraron las issues #38, #39 y #40 y las PR #35, #79 y #82.
- Este plan se ejecuta en `planning/runtime-v0.5-release`; no modifica `main` directamente.

### C1 — Evidencia y trazabilidad

1. Revisar todas las filas I/P de `docs/conformance-matrix.md` contra código y pruebas actuales.
2. Toda fila implementada/parcial debe apuntar a test node, fixture, script o limitación reproducible; comprobar que las rutas y símbolos existen.
3. Cada fixture debe estar catalogado y enlazado a IDs reales; comprobar también el sentido inverso.
4. Calcular métricas desde la matriz; separar requisitos MDES, subconjunto del parser, validación y runtime.
5. Cerrar issue #38 solo cuando la revisión semántica, no solo el lint mecánico, esté completa.

**Gate C1:** cero referencias rotas; cero filas I/P sin evidencia concreta; ninguna prueba parser-only usada como evidencia de ejecución; revisión humana de las filas ambiguas.

### C2 — Contrato Python/Rust

1. Auditar los comandos realmente disponibles en ambos backends y sus códigos/salidas.
2. Asegurar que `solve`, `run`, `check`, `simulate`, `diagnose` y `compile` tienen pruebas de integración donde se anuncien.
3. Mantener los scripts de paridad para parser, validación, solver, simulación, diagnósticos, CLI, CSV e IR.
4. Documentar diferencias deliberadas (por ejemplo, selección por defecto de sistema y límites de IR v1).
5. Añadir casos de error y CSV al nivel CLI cross-runtime, no solo tests unitarios internos.

**Gate C2:** todos los comandos anunciados tienen comportamiento probado; no hay divergencias compartidas no explicadas; issue #39 cerrada o sus exclusiones trasladadas al perfil.

### C3 — Semántica normativa

Trabajar sobre issue #40 y los ADR correspondientes:

- OPEN-001: límite CES cuando lambda tiende a cero.
- OPEN-002: umbral de N.2 Test 6.
- OPEN-003…OPEN-006: decisiones de fuente, datasets, referencias y tipos indicadas en la issue.
- OPEN-007: deuda.

También revisar bootstrap, memoria temporal, geometría y fatiga de enrutamiento cuando se pretendan incluir.

**Gate C3:** cada punto queda (a) resuelto mediante fuente normativa recuperada o ADR aprobado y pruebas de referencia, o (b) excluido expresamente del perfil v0.5 con error/estado explícito. No se permite convertir un `null`, placeholder o ausencia de fuente en un cero/estimador inventado.

### C4 — Lenguaje y perfil de compatibilidad

1. Tomar `docs/language-subset.md` y la suite de parser como baseline existente.
2. Revisar que gramática, tokens, escapes, Unicode, whitespace y rechazos coincidan entre Python y Rust.
3. Delimitar qué construcciones de MDES están soportadas y cuáles no (imports, módulos, funciones, tipos, actores/concurrencia, macros).
4. Aprobar el perfil candidato mediante revisión explícita; la propuesta no se convierte sola en norma.
5. Separar conformidad del parser, validación semántica y ejecución.

**Gate C4:** perfil versionado y aprobado; corpus positivo/negativo compartido; documentación y matriz coherentes.

### C5 — Núcleo matemático e investigación

PR #35 es una rama amplia y divergida: no se fusionará como bloque monolítico. Dividir la integración en unidades revisables:

1. Estabilidad numérica del solver y pruebas de extremos.
2. Diagnóstico genérico con Jacobianos/Fisher Information Matrix.
3. Selección D-optimal y análisis Sobol de primer orden.
4. Diagnósticos SIR/Hill específicos, si se incluyen en el perfil.
5. Pruebas aleatorizadas deterministas y paridad Python/Rust.

Cada unidad debe tener contrato matemático, supuestos, límites, fixtures, pruebas unitarias y prueba de paridad. Bootstrap no soportado debe seguir rechazándose explícitamente. Lo que no alcance estos criterios se mantiene experimental o fuera de v0.5.

**Gate C5:** ninguna API se anuncia como estable sin contrato y cobertura; todas las funciones compartidas incluidas pasan paridad.

### C6 — Robustez, instalación y distribución

- Verificar instalación desde entornos limpios y versiones soportadas.
- Probar quickstart y ejemplos de principio a fin en CI.
- Añadir pruebas de entradas malformadas, límites numéricos, proyectos grandes y fallos de IO.
- Revisar dependencias/licencias y documentar plataformas soportadas.
- Generar artefactos reproducibles; no anunciar backend/plataforma sin prueba.
- Publicar benchmarks solo con metodología, hardware y datasets descritos.

**Gate C6:** un usuario nuevo puede instalar, validar, ejecutar, simular y exportar un proyecto de ejemplo siguiendo la documentación, sin pasos privados ni estado previo del repositorio.

### C7 — Release candidate

- Congelar gramática del perfil, CLI, JSON IR y APIs incluidas.
- Ejecutar la suite completa en todos los entornos declarados.
- Revisar cada fila del perfil en la matriz y cada exclusión.
- Publicar notas de migración desde v0.1 y changelog.
- Auditar ejemplos, documentación, licencias y artefactos.
- Clasificar todos los issues abiertos como bloqueantes, conocidos/no bloqueantes o fuera de alcance.

**Gate C7:** cero fallos CI; cero bloqueos críticos/altos; ninguna ambigüedad normativa afecta a una capacidad anunciada; aprobación del autor del perfil.

### C8 — Declaración v0.5.0

- Actualizar versión del paquete/crate y documentación.
- Crear tag verificable `v0.5.0` y GitHub Release.
- Adjuntar artefactos, checksums, instrucciones y notas.
- Publicar matriz de conformidad y limitaciones.
- Declarar explícitamente: “conforme al perfil RONIN Runtime v0.5”, no “conforme a toda MDES v0.5” salvo evidencia completa.

## Orden de ejecución y dependencias

`C0 → C1 → C2 → C3/C4 → C5 → C6 → C7 → C8`

C3 y C4 pueden avanzar en paralelo, pero el perfil candidato no se congela hasta que ambos gates estén resueltos. C5 puede desarrollar investigación en paralelo, pero solo se incluye en el release lo que cumpla sus pruebas y tenga supuestos documentados. C6 empieza con el quickstart existente y se completa tras congelar el perfil.

## Registro de trabajo
### 2026-11-03 — C1, recuento actualizado de trazabilidad estructural

- La CI de trazabilidad de PR #96 reporta: **117 IDs únicos**, **62 filas I/P**, **197 rutas de evidencia resueltas**, **22 fixtures** y 81 IDs del perfil mapeados. Salida exacta en el job [Conformance fixture catalog / traceability](https://github.com/orbitalronin94/ronin-lang/actions/runs/41695675868).
- La cifra anterior de 192 rutas estaba desactualizada y se corrige en el seguimiento. Este resultado es estructural: el propio checker aclara que valida referencias y declaraciones, no la suficiencia semántica de las 62 filas. La revisión humana de C1 sigue abierta.

### 2026-11-03 — C7, documentación preliminar de release

- PR [#97](https://github.com/orbitalronin94/ronin-lang/pull/97) prepara `CHANGELOG.md`, la guía [migration-v0.1-to-v0.5.md](migration-v0.1-to-v0.5.md), el índice documental y la actualización de estado del roadmap/README.
- El changelog está marcado explícitamente como Unreleased; la guía no promete compatibilidad antes de la aprobación del perfil y de un RC real.
- C7 permanece abierto: aún faltan aprobación del perfil, cierre de C1/C3, congelación de alcance, matriz final y CI del SHA candidato.

### 2026-11-03 — C1, revisión semántica de simulación y diagnóstico

- PR [#85](https://github.com/orbitalronin94/ronin-lang/pull/85) fusionada: corrigió la afirmación de RNG distinta, documentó la paridad seeded real de MT19937/gauss CPython y degradó NORM-005 a P porque la libertad de parámetros se infiere de valores y ADR-0002 sigue pendiente.
- La revisión sigue siendo parcial; C1 no se cierra hasta revisar el resto de las filas I/P.

### 2026-11-03 — C1, evidencia de deuda

- PR [#91](https://github.com/orbitalronin94/ronin-lang/pull/91) propone corregir NORM-004/PY-006: `debt()` devuelve `None`, Rust usa `None`, y el JSON contiene `debt: null`, no cero. PR pendiente de merge/revisión.

### 2026-11-03 — C5, paridad aleatoria integrada

- PR [#89](https://github.com/orbitalronin94/ronin-lang/pull/89) fusionada con 15/15 jobs correctos: 80 sistemas solver deterministas (16 por cada uno de cinco modelos) y 15 sistemas de simulación × 24 pasos. CI: https://github.com/orbitalronin94/ronin-lang/actions/runs/41693306589.
- Las APIs FIM/Jacobiano, SIR, D-óptimo y Sobol se mantienen fuera del contrato estable, según [research-integration-scope-v0.5.md](research-integration-scope-v0.5.md). C5 queda cerrado solo para el alcance explícito de Runtime v0.5, no como implementación de toda la línea de investigación.

### 2026-11-03 — C6, instalación aislada y binario release

- PR [#87](https://github.com/orbitalronin94/ronin-lang/pull/87) aporta build de sdist/wheel, instalación en venv limpio y smoke del CLI instalado; también build Rust `--release --locked` y smoke del binario. Su rama obtuvo 17/17 jobs: https://github.com/orbitalronin94/ronin-lang/actions/runs/41692876766.
- Se portaron esos dos jobs y `rust/Cargo.lock` a una rama limpia basada en el main que ya contiene PR #89. La CI integrada de esta rama debe pasar antes de cerrar C6.


### 2026-11-03 — C1, revisión semántica inicial

- Detectada y corregida una afirmación obsoleta: `docs/conformance-matrix.md` y `docs/roadmap-execution.md` decían que Python/Rust no compartían RNG, pero `rust/src/simulator.rs` replica MT19937, uniform de 53 bits y gauss cacheado de CPython; `scripts/check_simulation_contracts.py` compara 12 trayectorias con semilla fija a tolerancia 1e-12. Corregidas también `roadmap.md` y `source-coverage.md`.
- Revisado el diagnóstico normativo: `NORM-005` baja de I a P porque la inferencia de parámetros libres desde valores numéricos sigue provisional (ADR-0002). La propuesta de perfil limita el compromiso estable de identificabilidad hasta resolverlo.
- C1 sigue abierto: esta es una primera revisión semántica de las filas de simulación/diagnóstico, no la revisión completa de las 62 filas I/P.

### 2026-11-03 — C1, corrección de evidencia de deuda

- `NORM-004` describía incorrectamente un placeholder `0.0`; la implementación devuelve `None` en Python y `debt: null` en Rust. Se corrigen NORM-004 y la nota de PY-006. La deuda sigue excluida por falta de estimador normativo.

### 2026-11-03 — C5, stress numérico compartido

- Se incorporan dos pruebas deterministas procedentes de la línea de investigación, sin introducir nuevas fórmulas ni cambiar el runtime: `check_randomized_runtime_parity.py` genera 80 sistemas (16 por cada modelo PUSFRE/CES/Hill/CES-Hill/full), incluye frecuencias de 1e-300 y recursos/parametrizaciones extremos, y verifica rechazo degenerado; `check_randomized_simulation_parity.py` genera 15 sistemas (3 por modelo), 24 pasos y semillas fijas.
- Ambos scripts se añaden a los jobs de solver/simulación de CI y a las filas CORE-002/PY-006/RS-006/SIM-002/RS-007 de la matriz.
- Estos tests fortalecen el núcleo compartido, pero no integran las APIs experimentales FIM/D-optimal/Sobol/SIR de PR #35. La línea de investigación avanzada permanece fuera del perfil estable propuesto. La evaluación Hill en espacio logarítmico ya estaba en la línea base Python/Rust; no se vuelve a importar ni se cambia.

### 2026-11-03 — C4, perfil Runtime v0.5 propuesto

- Creado [`docs/runtime-v0.5-profile-proposal.md`](runtime-v0.5-profile-proposal.md), con alcance incluido, límites de contrato y exclusiones explícitas.
- Se propone mantener `diagnose`/identificabilidad como experimental hasta resolver ADR-0002; excluir CES lambda→0 hasta ADR-0001; mantener fuera deuda, bootstrap, datasets incompletos, tipos generales, concurrencia y backends no implementados.
- PR #35 (investigación) se propone como línea experimental separada; solo se integrará en v0.5 lo que se seleccione explícitamente y tenga contrato/paridad.
- **C4 no se cierra:** el perfil requiere aprobación del mantenedor. La propuesta evita afirmar conformidad integral con MDES v0.5.

### 2026-11-03 — C3, propuestas normativas preparadas

- Se trasladaron al plan de release dos propuestas que existían en la rama de investigación: [ADR-0001 — CES lambda→0](decisions/ADR-0001-ces-zero-limit.md) y [ADR-0002 — modos de parámetros](decisions/ADR-0002-parameter-modes.md).
- Ambas siguen **pendientes de aprobación**. ADR-0001 cambia N.2 Test 3; ADR-0002 cambia el significado de identificabilidad. No se modifica MDES ni el comportamiento del runtime en esta tanda.
- OPEN-003/004 siguen dependiendo de datasets fuente completos; OPEN-005 de recuperar/aclarar la referencia N.6; OPEN-006 de decisión de alcance del sistema de tipos; OPEN-007 de una definición normativa de deuda. Si no se recuperan fuentes, deberán quedar excluidos explícitamente del perfil v0.5.

### 2026-11-03 — C2, primera auditoría de CLI

- Auditoría de opciones: Rust aceptaba `--system` en `list`/`run` y `--delta` en comandos ajenos, aunque Python los rechaza. Se alineó el alcance de opciones y se añadieron tres casos a la paridad de errores (10 → 13).
- Contrato JSON: el CLI Python emitía `Infinity` no estándar para parámetros por defecto; se reutilizó la normalización JSON del IR para emitir `"inf"`/`"-inf"`/`"nan"`, con `allow_nan=False`. Añadidas aserciones Python y Rust.
- CI completo en commit `16b6945ccaaa3ffb8be0705c7728eccc5c8a0add`: **15/15 jobs correctos** (https://github.com/orbitalronin94/ronin-lang/actions/runs/41689832857).
- Issue [#39](https://github.com/orbitalronin94/ronin-lang/issues/39) cerrada con alcance y límites explícitos. C2 queda completado para el contrato compartido documentado; no implica paridad completa de MDES.

### 2026-11-03 — C1, primera ejecución

- Revisadas las PR #79 y #82: #79 comprueba declaraciones `def`/`fn` pero no tenía tests dedicados; #82 mejora la extracción `ruta::símbolo`, pero su búsqueda por subcadena acepta menciones en comentarios/cadenas y prefijos. Se consolidó extracción estructurada más verificación de declaración anclada y pruebas negativas/positivas.
- Añadido `tests/test_fixture_catalog_checker.py` y conectado a CI antes del chequeo de matriz.
- Primer intento CI detectó un escape incorrecto en la expresión regular; corregido antes de aceptar el resultado.
- CI final del commit `18175e451fb07d23676cff5a8f01fa31044c0722`: **15/15 jobs correctos**, incluido el job de trazabilidad. Evidencia: https://github.com/orbitalronin94/ronin-lang/actions/runs/41688569556.
- Corregida la documentación: el catálogo actual contiene ocho fixtures positivos, no siete.
- **C1 sigue en curso:** la verificación estructural pasa, pero falta la revisión semántica manual de todas las filas I/P y la aprobación del perfil.


Cada avance debe actualizar este archivo con:
- checkpoint e ítem;
- PR/commit/issue que aporta el cambio;
- comando o workflow ejecutado;
- resultado observado;
- evidencia enlazada;
- deuda restante y responsable de la decisión.

No se marcará un checkpoint como completado por inferencia. Si una herramienta o permiso impide ejecutar una prueba, se registra como pendiente, no como éxito.

## Primera tanda de ejecución

1. C0 registrado en este plan.
2. C1: auditar el solapamiento PR #79/#82 y consolidar una sola implementación de validación de símbolos.
3. C1: ejecutar y revisar la suite de trazabilidad en CI.
4. C2: convertir los huecos restantes de issue #39 en tests o exclusiones precisas.
5. C3/C4: preparar propuestas de decisión y pedir aprobación únicamente donde MDES no determine la respuesta.
