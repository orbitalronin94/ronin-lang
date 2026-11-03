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
| C2 | Contrato compartido v0.3 | CLI, errores, selección, CSV, IR y comportamiento Python/Rust cubiertos por pruebas de integración/paridad; diferencias intencionadas documentadas | En curso |
| C3 | Decisiones normativas v0.4 | OPEN-001…OPEN-007 resueltos por fuente/ADR aprobado o excluidos explícitamente del perfil; ningún placeholder se presenta como resultado | Bloqueado por decisiones/fuentes |
| C4 | Lenguaje y perfil candidato v0.5 | Subconjunto léxico/sintáctico reproducible; perfil de runtime v0.5 delimitado, revisado y aprobado; parser-only separado de validación/ejecución | Baseline parser completado; aprobación pendiente |
| C5 | Núcleo matemático y diagnósticos | Funcionalidades que se incluyan desde la línea de investigación integradas en PR pequeñas, con definición, fixtures y paridad; el resto se marca experimental/no incluido | En curso en PR #35 |
| C6 | Robustez y distribución | Instalación limpia, ejemplos ejecutables, pruebas de límites/errores, política de dependencias y artefactos reproducibles para plataformas declaradas | Pendiente |
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
