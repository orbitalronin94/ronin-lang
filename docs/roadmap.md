# Roadmap de RONIN Runtime v0.1 a v1.0

**Base de diseño:** MDES v0.5  
**Estado actual:** v0.1 — implementación temprana y ejecutable  
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

## 3. Hitos de versión

### v0.1 — Foundation / baseline (estado actual)

**Objetivo:** disponer de una base funcional que permita escribir, validar y resolver proyectos RONIN.

Entregado:
- Runtime y CLI Python para el subconjunto implementado.
- Validación, solver PUSFRE/CES/Hill/CES-Hill, asignación, simulación y diagnóstico.
- Proyectos multi-sistema, ejecución completa y salida JSON/CSV.
- Compilación Python a JSON IR validado.
- Parser y CLI Rust iniciales; metadatos anidados y parámetros extendidos.
- Pruebas automatizadas y CI para los trabajos integrados.

No implica:
- Conformidad integral con MDES v0.5.
- Paridad completa Python/Rust.
- Implementación de todas las extensiones descritas en la especificación.

### v0.2 — Conformance map and test baseline

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
- CI publica resultados por área y lenguaje.
- Ningún ejemplo incompleto se presenta como aceptación ejecutable.
- La cobertura reportada se calcula desde la matriz, no por estimación subjetiva.

### v0.3 — Python/Rust parity and portable IR

**Objetivo:** hacer que Python y Rust compartan un contrato de datos y ejecución verificable.

Trabajo:
- Implementar `ronin-rust compile` con salida JSON IR equivalente al compilador Python.
- Definir fixtures de entrada y salidas IR canónicas.
- Ejecutar los mismos proyectos en ambos runtimes y comparar asignaciones, fitness y diagnósticos.
- Alinear errores, valores por defecto, precisión numérica y serialización de valores no finitos.
- Añadir pruebas de round-trip donde la semántica lo permita.

**Criterios de salida:**
- El conjunto de fixtures comunes genera IR equivalente.
- Los casos numéricos compartidos cumplen tolerancias documentadas.
- Diferencias intencionadas quedan identificadas y justificadas.
- El CLI Rust tiene pruebas de integración para todos sus comandos publicados.

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

### v0.5 — Language profile completeness

**Objetivo:** ampliar y cerrar el perfil de lenguaje que se comprometerá a soportar v1.0.

Trabajo:
- Completar la matriz léxica y sintáctica respecto a MDES.
- Incorporar construcciones de alto nivel solo cuando su semántica esté definida.
- Mejorar mensajes de error con ubicación, contexto y sugerencias útiles.
- Definir imports/módulos y resolución de nombres si forman parte del perfil aprobado.
- Recuperar los cuerpos originales ausentes de ejemplos 1–100 y los datasets omitidos; no reconstruirlos a mano.
- Etiquetar ejemplos como normativos, ilustrativos, parser-only o ejecutables.

**Criterios de salida:**
- El perfil de lenguaje v1.0 está delimitado explícitamente.
- Todos sus constructos tienen pruebas positivas y negativas.
- Los ejemplos normativos completos se ejecutan o tienen una razón documentada para no hacerlo.

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

**v1.0 no significa implementar cada idea futura de MDES.** Significa que el perfil estable anunciado está definido, probado, documentado y mantenido con compatibilidad deliberada.

## 4. Líneas de trabajo transversales

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

## 5. Gestión de requisitos y porcentaje de avance

El porcentaje de avance no se calculará por número de commits, archivos o líneas de código. Se medirá sobre requisitos identificados:

- **No iniciado:** sin implementación.
- **En desarrollo:** existe código, pero faltan pruebas o contrato estable.
- **Implementado:** comportamiento y pruebas disponibles para el alcance declarado.
- **Conforme:** pruebas trazables demuestran el requisito de MDES en el perfil soportado.
- **Bloqueado/ambiguo:** falta definición normativa, datos o decisión editorial.

Un requisito no puede contarse como conforme solo porque exista una función con un nombre parecido. La matriz de v0.2 será la fuente del porcentaje verificable.

## 6. Política de cambios

- Cada cambio funcional debe incluir pruebas y documentación.
- Los cambios normativos deben citar la sección de MDES afectada y registrar la decisión.
- Los cambios incompatibles deben incrementar la versión correspondiente y ofrecer notas de migración.
- Una versión de software no modifica automáticamente MDES.
- No se anunciará soporte para un backend, binding o extensión hasta que sus pruebas de conformidad estén disponibles.

## 7. Estado actual

En el momento de publicar este roadmap, el repositorio se declara **RONIN Runtime v0.1**, basado en **MDES v0.5**. El runtime Python ofrece más capacidades que la implementación Rust en algunas áreas; Rust ya dispone de parser y CLI iniciales, pero no tiene paridad completa ni compilación IR equivalente. Los límites detallados están en [source-coverage.md](source-coverage.md).
