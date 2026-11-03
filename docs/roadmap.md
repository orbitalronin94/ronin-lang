# Roadmap de RONIN Runtime v0.1 a v1.0

**Base de diseño:** MDES v0.5  
**Estado actual:** v0.3 cerrado para el contrato compartido Python/Rust e IR v1; baseline técnico v0.5 del parser completado; v0.2 continúa en curso y el perfil v1.0 sigue pendiente de aprobación  
**Idioma canónico de proyecto:** castellano

## 1. Política de versiones

Este proyecto mantiene dos líneas de versión independientes:

- **MDES v0.5:** versión de la especificación de diseño completa que sirve como referencia normativa y arquitectónica.
- **RONIN Runtime v0.1:** versión del software implementado hasta ahora.

Que exista una especificación completa no significa que todas sus capacidades estén implementadas. Del mismo modo, incrementar la versión del runtime no cambia automáticamente la versión de MDES. Cualquier cambio normativo debe quedar documentado y revisado expresamente.

## 2. Principios del roadmap

1. **Conformidad antes que marketing:** una capacidad solo se declara implementada cuando tiene comportamiento definido, pruebas y documentación.
2. **Paridad verificable:** Python y Rust deben producir resultados equivalentes en los perfiles que ambos declaren soportar.
3. **Sin semántica inventada:** las lagunas de MDES —por ejemplo, deuda o bootstrap— requieren una decisión normativa antes de codificarse.
4. **Fixtures reproducibles:** los ejemplos y datasets de aceptación deben estar completos, versionados y trazables a su sección fuente.
5. **Compatibilidad deliberada:** los cambios de sintaxis, IR y API deben tener pruebas de compatibilidad y notas de migración.
6. **Hitos por criterios de salida:** no se promete una fecha ni se considera alcanzada una versión por el mero hecho de crear una etiqueta.
7. **Utilidad incremental sin rebajar el destino:** cada etapa debe producir capacidades que alguien pueda usar; el objetivo final sigue siendo completar la conformidad con MDES v0.5, no sustituirla por un subconjunto permanente.

## 3. Línea paralela: utilidad y adopción

La conformidad completa sigue siendo el destino técnico. No obstante, RONIN debe generar valor antes de terminar todos los capítulos de MDES. Por eso, junto al trabajo de especificación, se mantiene una línea de producto incremental:

1. **Caso real reproducible:** partir de proyectos existentes del repositorio —empezando por `examples/maquinas.ronin`— y documentar el problema, los datos de entrada, el modelo elegido, los comandos y la interpretación de la salida.
2. **Flujo de usuario completo:** instalación limpia → inspección del proyecto → validación → resolución/simulación → exportación → explicación de resultados. Cada paso debe poder repetirse desde la documentación.
3. **Ejemplos orientados a tareas:** añadir ejemplos solo cuando haya una pregunta concreta que responder y datos/expectativas verificables; no convertir fixtures sintéticos en evidencia de aplicabilidad real.
4. **Experiencia de uso:** priorizar mensajes de error accionables, defaults explícitos, documentación de inicio rápido y salidas fáciles de consumir desde Python, Rust, CSV y JSON.
5. **Distribución:** preparar paquetes y artefactos reproducibles cuando el flujo de instalación y las plataformas soportadas estén probados.
6. **Feedback:** recoger problemas de usuarios y convertirlos en issues, tests de regresión o mejoras de documentación, sin alterar silenciosamente la semántica normativa.

### Puerta de utilidad de cada entrega

Una capacidad se considera útil cuando existe al menos un ejemplo completo y ejecutable, una explicación del problema que aborda, entradas y resultados esperados, instrucciones de ejecución desde un entorno limpio y una descripción honesta de sus límites. La CI verde es necesaria para la calidad del cambio, pero no sustituye esa demostración de uso.

Esta línea no permite etiquetar como implementadas funciones ausentes ni relajar la precisión matemática. Las áreas no soportadas deben fallar claramente o declararse explícitamente; nunca deben producir resultados ficticios.

## 4. Hitos de versión

### Estado verificado a 2026-11-03

Se han integrado checkpoints separados para: tolerancias y validación de frecuencias; auditoría automática de trazabilidad del catálogo de fixtures; paridad de selección de sistemas en `simulate`/`diagnose`; rutas de error de CLI; ubicaciones de diagnóstico del parser; escapes Unicode surrogate inválidos; y validación de longitud/suma de `memory_weights`. La CI de la última PR de validación de memoria terminó con 15/15 jobs correctos ([ejecución](https://github.com/orbitalronin94/ronin-lang/actions/runs/41658388618)). Esto mejora la evidencia de v0.2; v0.3 está cerrado para el contrato compartido delimitado más abajo. No demuestra conformidad integral.


### v0.1 — Foundation / baseline (estado actual)

**Objetivo:** disponer de una base funcional que permita escribir, validar y resolver proyectos RONIN.

Entregado:
- Runtime y CLI Python para el subconjunto implementado.
- Validación, solver PUSFRE/CES/Hill/CES-Hill, asignación, simulación y diagnóstico.
- Proyectos multi-sistema, ejecución completa y salida JSON/CSV.
- Compilación Python a JSON IR validado.
- Parser Rust para el subconjunto compartido, metadatos anidados y parámetros extendidos; CLI `list`, `check`, `solve`, `run`, `compile`, `diagnose` y `simulate`, con exportación CSV en `run`.
- Pruebas automatizadas y CI para los trabajos integrados.

No implica:
- Conformidad integral con MDES v0.5.
- Paridad completa Python/Rust.
- Implementación de todas las extensiones descritas en la especificación.

### v0.2 — Conformance map and test baseline (en curso)

**Primera línea base creada.**

La [matriz de trazabilidad](conformance-matrix.md) ya asigna IDs a los requisitos de las secciones 0–15, Partes V–VI, el anexo normativo y los ejemplos; distingue el estado Python/Rust y registra evidencias y bloqueos. El corpus compartido y su catálogo contienen siete fixtures positivos, diez negativos, tres diagnósticos y uno check-only. Un job de CI comprueba que los `.ronin` estén catalogados, existan y enlacen IDs únicos de filas reales de la matriz; además, audita en sentido inverso que cada fila I/P tenga una nota de evidencia o limitación, cite al menos un test/fixture/script y use rutas y símbolos citados que resuelvan. La matriz incluye referencias concretas de implementación en las filas I/P y tests, fixtures o scripts identificables en las filas I; estas mejoras se integraron en [PR #67](https://github.com/orbitalronin94/ronin-lang/pull/67), [PR #69](https://github.com/orbitalronin94/ronin-lang/pull/69), [PR #71](https://github.com/orbitalronin94/ronin-lang/pull/71) y [PR #72](https://github.com/orbitalronin94/ronin-lang/pull/72). Es una línea base trazable, no el cierre del hito: la suficiencia semántica de la evidencia requiere revisión y la propuesta de perfil v1.0 aún no está aprobada.

**Objetivo:** convertir MDES v0.5 en una matriz de requisitos trazable y una suite de conformidad.

Trabajo:
- Identificar cada requisito normativo, sección fuente, estado, implementación y prueba.
- Clasificar requisitos como MUST/SHOULD/MAY solo cuando MDES lo permita; no reinterpretar silenciosamente su fuerza normativa.
- Completar y etiquetar fixtures mínimos para cada comportamiento ejecutable.
- Añadir pruebas negativas para errores léxicos, sintácticos y semánticos.
- Separar claramente pruebas parser-only de pruebas de ejecución.
- Documentar cada discrepancia o ambigüedad abierta con una decisión pendiente.

**Criterios de salida:**
- Cada requisito del perfil ejecutable tiene identificador y estado.
- CI publica resultados por área y lenguaje. La workflow separa Python (parser/metadata, runtime numérico/fixtures, CLI/IR/REPL) y Rust (parser, solver, diagnóstico, simulación, IR y CLI).
- Ningún ejemplo incompleto se presenta como aceptación ejecutable.
- La cobertura reportada se calcula desde la matriz, no por estimación subjetiva.

### v0.3 — Python/Rust parity and portable IR (cerrado para el contrato compartido documentado)

**Primera entrega integrada:** `ronin-core compile` emite JSON IR v1 con validación previa; `scripts/check_ir_parity.py` compara 12 proyectos válidos y cuatro rechazos. `scripts/check_runtime_parity.py` contrasta fitness, allocation, coexistence, k_min, degeneracy y override de delta en 11 proyectos. `scripts/check_diagnostic_parity.py` compara cuatro informes; `scripts/check_simulation_contracts.py` compara trayectorias con semilla fija en 12 proyectos con tolerancia 1e-12; y `scripts/check_csv_parity.py` compara exportaciones CSV en 11 proyectos y un proyecto multi-sistema; `scripts/check_validation_parity.py` contrasta aceptación/rechazo, selección de sistemas y proyectos válidos con fitness cero; `scripts/check_cli_selection_parity.py` fija la diferencia intencionada entre `solve` (primer sistema) y `run`/`check` (todos); `scripts/check_parser_parity.py` contrasta nueve ficheros válidos, tres fuentes válidas inline y 29 fuentes inválidas inline; incluye escapes, Unicode, metadatos anidados, rechazo de surrogate aislado y una comprobación de ubicación línea/columna. `scripts/check_cli_error_parity.py` verifica diez fallos compartidos; `scripts/check_cli_selection_parity.py` cubre selección por defecto y explícita en solve/simulate/diagnose y el alcance de run/check. Los casos de longitud/suma de memory_weights están incluidos en la paridad de validación. Todo queda integrado en jobs independientes de CI.

**Resultado:** contrato de datos y ejecución compartido verificado para el corpus/campos enumerados. Los errores se comparan por fallo limpio, no por igualdad textual/código; las semillas reproducen dentro de cada backend, sin promesa de RNG común; IR v1 es salida, no importación de vuelta a `.ronin`.

**Objetivo:** hacer que Python y Rust compartan un contrato de datos y ejecución verificable.

Trabajo futuro (fuera del cierre v0.3): importación del IR a un modelo ejecutable, RNG idéntico entre backends, ampliación de vectores normativos cuando se recuperen las fuentes completas y mayor cobertura de comandos/casos no incluidos en los scripts. Estos puntos no se consideran contratos actuales ni se simulan con expectativas inventadas.

### v0.4 — Normative semantics closure

**Objetivo:** resolver los huecos semánticos que impiden afirmar conformidad en áreas clave.

Trabajo:
- Resolver editorial y normativamente la discrepancia del límite CES cuando lambda tiende a cero.
- Definir, si se desea incluir en el perfil estable, el estimador de deuda y sus entradas/salidas.
- Definir el método bootstrap, semillas, intervalos, niveles de confianza y condiciones de error.
- Especificar el kernel de memoria temporal: orden, pesos, inicialización, actualización y estabilidad.
- Establecer comportamiento para casos degenerados, infinitos, NaN y límites numéricos.
- Añadir vectores de prueba normativos para cada decisión.

**Criterios de salida:**
- Cada semántica incluida en el perfil estable tiene definición inequívoca.
- No quedan placeholders silenciosos en las funciones declaradas estables.
- Implementaciones y pruebas coinciden con las decisiones normativas aprobadas.

> Este hito no autoriza a inventar fórmulas. Si una decisión no está resuelta en MDES, debe registrarse como propuesta hasta su aprobación.

### v0.5 — Technical language subset baseline

**Estado:** baseline técnico del parser compartido completado; la aprobación del perfil de compatibilidad v1.0 sigue pendiente.

RONIN documenta el subconjunto que implementan actualmente Python y Rust en [language-subset.md](language-subset.md). La paridad cubre nueve archivos válidos, tres fuentes válidas inline y 29 inválidas inline. Se alinearon whitespace admitido, valores literales, escapes, Unicode y rechazos de campos/valores fuera del subconjunto.

Este hito cierra el inventario y la regresión del parser existente; no declara completa la gramática MDES v0.5 ni aprueba qué capacidades futuras serán obligatorias en v1.0.

Trabajo posterior sujeto a aprobación/fuentes:
- Resolver imports/módulos y construcciones de alto nivel para el perfil v1.0.
- Recuperar los cuerpos originales ausentes de ejemplos 1–100 y datasets incompletos; no reconstruirlos a mano.
- Ampliar diagnósticos con contexto/sugerencias sin exigir igualdad textual innecesaria entre backends.

**Criterios del baseline técnico satisfechos:** subconjunto delimitado, inventario léxico/sintáctico y casos positivos/negativos en CI. La puerta normativa de v1.0 permanece abierta.
### v0.6 — Interoperability and stable interfaces

**Objetivo:** permitir integrar RONIN desde otros programas y entornos.

Trabajo:
- Estabilizar API Python y crate/API Rust.
- Diseñar bindings externos (por ejemplo, PyO3) con contratos de error y tipos explícitos.
- Evaluar WASM y C como backends separados, con pruebas de conformidad comunes.
- Versionar el JSON IR y definir compatibilidad hacia delante/atrás.
- Añadir documentación de integración y ejemplos mínimos por lenguaje.

**Criterios de salida:**
- APIs públicas documentadas y versionadas.
- Serialización e IR con política de compatibilidad.
- Cada binding/backend publicado supera el subconjunto de conformidad que anuncia.

### v0.7 — Authoring tools and RONIN Office MVP

**Objetivo:** ofrecer herramientas de trabajo utilizables alrededor del lenguaje.

Trabajo:
- Definir el alcance realista de Office MVP.
- Integrar editor, validación, ejecución y visualización de resultados.
- Mejorar importación/exportación CSV y trazabilidad de los proyectos.
- Mantener cálculos en el runtime común; evitar divergencias matemáticas en la interfaz.
- Incorporar accesibilidad, manejo de errores y pruebas de interfaz.

**Criterios de salida:**
- Flujo completo desde abrir un proyecto hasta ejecutar y revisar resultados.
- La interfaz no duplica ni altera la semántica del solver.
- Las funciones no implementadas se muestran como tales.

### v0.8 — Performance, reliability and security

**Objetivo:** preparar el runtime para cargas y proyectos reales.

Trabajo:
- Crear benchmarks reproducibles para parseo, validación, solver y simulación.
- Perfilar antes de optimizar; publicar hardware, datos y metodología.
- Probar proyectos grandes, entradas malformadas y límites de memoria.
- Revisar determinismo, concurrencia, semillas y estabilidad numérica.
- Añadir fuzzing de parser y pruebas de propiedades donde sea viable.
- Establecer política de dependencias, licencias y divulgación de vulnerabilidades.

**Criterios de salida:**
- Benchmarks repetibles y sin afirmaciones no demostradas.
- Pruebas de robustez automatizadas.
- No hay fallos críticos conocidos en el perfil de lanzamiento.

### v0.9 — Release candidate

**Objetivo:** congelar el alcance y validar la compatibilidad de la primera versión estable.

Trabajo:
- Congelar sintaxis, IR, CLI y APIs públicas candidatas.
- Ejecutar la suite completa de conformidad en Python y Rust.
- Publicar notas de migración y matriz de compatibilidad.
- Auditar documentación, ejemplos, licencias y artefactos de distribución.
- Corregir defectos sin añadir características incompatibles salvo necesidad crítica.

**Criterios de salida:**
- Todos los bloqueos de lanzamiento están cerrados.
- No quedan discrepancias normativas sin clasificar.
- Instalación y pruebas funcionan desde entornos limpios soportados.

### v1.0 — Stable release

**Objetivo:** publicar el primer perfil estable, reproducible y verificable de RONIN.

Requisitos de lanzamiento:
- Perfil de MDES soportado delimitado y versionado.
- Matriz de conformidad completa para ese perfil.
- Suite de pruebas de aceptación y regresión en verde.
- Python y Rust conformes en las capacidades declaradas compartidas.
- IR, CLI y APIs estables con política de compatibilidad.
- Documentación de usuario, referencia, arquitectura y migración.
- Limitaciones y extensiones no soportadas claramente publicadas.
- Artefactos reproducibles y procedimiento de release documentado.

**La conformidad completa con MDES v0.5 sigue siendo el objetivo final del proyecto.** v1.0 no debe declarar conformidad con requisitos excluidos o pendientes: el alcance anunciado debe estar delimitado, y cualquier requisito de MDES aún no implementado debe permanecer visible como deuda o trabajo posterior. Las entregas intermedias pueden ser útiles y estables para sus capacidades declaradas sin presentarse como conformidad integral.

## 5. Líneas de trabajo transversales

| Línea | Resultado esperado para v1.0 |
|---|---|
| Especificación | Requisitos trazables y ambigüedades resueltas o excluidas explícitamente |
| Parser | Gramática del perfil estable, errores precisos y pruebas negativas |
| Semántica | Fórmulas y límites normativos implementados sin placeholders |
| Solver | Resultados reproducibles y contrastados entre runtimes |
| IR | Esquema versionado y serialización interoperable |
| Rust | Implementación conforme al perfil compartido |
| Simulación | Kernel definido, determinista bajo semilla y validado |
| Diagnóstico | Indicadores con definiciones, límites y pruebas |
| Herramientas | CLI estable y Office MVP probado si se incluye en el alcance |
| Calidad | CI, fuzzing, benchmarks y política de releases |

## 6. Gestión de requisitos y porcentaje de avance

El porcentaje de avance no se calculará por número de commits, archivos o líneas de código. Se medirá sobre requisitos identificados:

- **No iniciado:** sin implementación.
- **En desarrollo:** existe código, pero faltan pruebas o contrato estable.
- **Implementado:** comportamiento y pruebas disponibles para el alcance declarado.
- **Conforme:** pruebas trazables demuestran el requisito de MDES en el perfil soportado.
- **Bloqueado/ambiguo:** falta definición normativa, datos o decisión editorial.

Un requisito no puede contarse como conforme solo porque exista una función con un nombre parecido. La matriz de v0.2 será la fuente del porcentaje verificable.

## 7. Política de cambios

- Cada cambio funcional debe incluir pruebas y documentación.
- Los cambios normativos deben citar la sección de MDES afectada y registrar la decisión.
- Los cambios incompatibles deben incrementar la versión correspondiente y ofrecer notas de migración.
- Una versión de software no modifica automáticamente MDES.
- No se anunciará soporte para un backend, binding o extensión hasta que sus pruebas de conformidad estén disponibles.

## 8. Estado actual

En el momento de publicar este roadmap, el repositorio se declara **RONIN Runtime v0.1**, basado en **MDES v0.5**. El runtime Python ofrece más capacidades que la implementación Rust en algunas áreas; Rust ya dispone de parser y CLI iniciales, pero no tiene paridad completa ni compilación IR equivalente. Los límites detallados están en [source-coverage.md](source-coverage.md).
