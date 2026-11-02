# Programa de implementación integral de RONIN

**Objetivo de proyecto:** completar la especificación de referencia MDES v0.5 y convertir en capacidades ejecutables las partes implementables de la edición 1.1, manteniendo separadas norma, propuesta, extensión futura y evidencia científica.

Este programa amplía el roadmap de versiones. No sustituye MDES, no aprueba ADR pendientes y no convierte ejemplos incompletos en requisitos demostrados.

## 1. Regla de autoridad

Hay tres capas que no deben mezclarse:

1. **MDES v0.5 y su anexo normativo:** fuente de conformidad del proyecto.
2. **Documento maestro RONIN 1.1:** diseño ampliado, arquitectura y código de referencia. Sus secciones que dicen «propuesto», «experimental», «sin cambios respecto a 1.0» o «futuro» conservan esa condición.
3. **Papers:** corpus de investigación para diagnósticos y validación. Sus resultados se integran solo con hipótesis, dominio, parametrización, ruido y límites explícitos; no se convierten automáticamente en semántica del lenguaje.

El perfil candidato v1.0 es un hito intermedio para estabilizar un subconjunto verificable, no la definición del límite final del proyecto. La finalización integral exige cerrar la matriz MDES, no solo el perfil intermedio.

## 2. Líneas de implementación

### A. Núcleo matemático y semántica del sistema

| Capacidad | Estado observado | Trabajo de cierre |
|---|---|---|
| Declaración y validación de sistemas/agentes | Implementado en el subconjunto Python/Rust | Mantener fixtures compartidos, errores equivalentes y límites numéricos |
| PUSFRE, CES, Hill y CES-Hill | Implementados en ambos runtimes | Resolver discrepancias normativas CES→0 y dominios de parámetros; ampliar pruebas de borde |
| Asignación y conservación del recurso | Implementadas | Pruebas deterministas, aleatorias, extremos y sistemas degenerados |
| k_min y coexistencia | Parciales | Fijar una definición única de coexistencia, unidades, umbral y casos límite |
| Deuda y auditoría | Bloqueadas | Recuperar el contrato íntegro de la versión anterior; definir estimador, observables, muestreo, incertidumbre y validación externa antes de codificar |
| Geometría del sistema | No implementada / contrato insuficiente | Definir objeto geométrico, métrica, normalización y propiedades invariantes |
| Fatiga de enrutamiento | No implementada / contrato insuficiente | Definir topología, carga, horizonte, unidades y dinámica de fatiga |
| Memoria temporal full | Orden 1 compartido; órdenes superiores rechazados | Especificar kernel, inicialización, pesos, tratamiento de historia y estabilidad antes de habilitar órdenes 2/3/5 |
| Familia CES-Saturada | Parcialmente implementada | Cerrar ADR-0001, pesos configurables si se aprueban, límites y vectores normativos |
| Metadatos de solver | Parciales | Definir o retirar convergence/steps y alinear JSON/IR Python/Rust |

**Regla:** no se implementarán deuda, geometría, fatiga ni memoria superior mediante fórmulas intuitivas. Si la fuente no contiene el contrato, primero se registra y resuelve la decisión normativa.

### B. Lenguaje, frontend y sistema de tipos

La implementación actual es principalmente un lenguaje declarativo de proyectos system; no es todavía el lenguaje general mostrado en los ejemplos conceptuales.

Secuencia de construcción:

1. **AST de programa:** separar Program, declaraciones System, Let, Fn y comandos; conservar posiciones de fuente.
2. **Expresiones:** literales, referencias, arrays/objetos, llamadas, operadores aritméticos, comparaciones y precedencia documentada.
3. **Ámbitos y funciones:** resolución de nombres, parámetros, retorno, funciones puras y errores de tipos.
4. **Control de flujo:** if/else y for, con reglas de evaluación y límites de ejecución.
5. **Módulos e imports:** resolución determinista, ciclos, rutas y aislamiento.
6. **Macros:** expansión sobre AST, límites de recursos y diagnósticos de expansión.
7. **Tipos de dominio:** catálogo, tipos compuestos, rangos, restricciones e inferencia. Los tipos dependientes permanecen experimentales hasta disponer de reglas formales.

Cada etapa necesita gramática, AST estable, pruebas de aceptación/rechazo, errores con ubicación y equivalencia entre Python y Rust. No se anunciará soporte de funciones, macros o tipos por aceptar únicamente su sintaxis.

### C. Motor de ejecución y operaciones de dominio

- **solve:** consolidar semántica normativa y contratos de salida.
- **simulate:** mantener el kernel de referencia y extenderlo solo con opciones definidas (DTMC, estocasticidad, presión de enrutamiento, historia y eventos).
- **audit:** implementar tras cerrar deuda y muestreo; distinguir estimación, intervalo, confianza y error.
- **diagnose:** integrar en CLI/IR los diagnósticos de sistema y los diagnósticos de diseño FIM/SVD de Papers, con alcances separados.
- **plot:** definir una salida de datos independiente del frontend gráfico y un contrato de visualización.
- **REPL:** ejecutar programas y comandos sobre el mismo AST/IR, no una gramática paralela.
- **Concurrencia:** actores, canales, futures/promises, streams y backpressure requieren modelo de memoria, cancelación, errores y determinismo.

### D. Investigación, identificabilidad y evidencia

Integraciones ya iniciadas:

- Hill: diseño pre-ajuste, FIM local y direcciones débiles.
- PBPK: selección D-óptima greedy sobre filas de sensibilidades, con score regularizado normalizado y diagnóstico de rango del subconjunto.
- PBPK: estimador genérico Sobol de primer orden sobre salidas A/B/A_B^i; no genera muestras ni calcula interacciones de segundo orden.
- PBPK: diagnóstico local/práctico condicionado por escalado y ruido.
- SIR con subreporte: combinaciones identificables solo bajo la aproximación de fase temprana.
- Protocolo de 50 dominios y Testing 1310: base para diseñar pruebas, no garantía automática de validez externa.
- Tratado y CASCABEL: principios de trazabilidad y QA, manteniendo fuera de la semántica normativa aquello que no esté demostrado.

Siguiente cierre:

1. FIM genérica estable frente a escalas y pesos extremos.
2. Sensibilidad a valores típicos, parametrización y tolerancias.
3. Integración CLI/IR con entradas observacionales explícitas.
4. Perfiles prácticos calibrados por dominio, sin umbrales universales inventados.
5. Diagnóstico post-ajuste, perfiles de verosimilitud y bootstrap solo cuando existan observaciones, modelo de error y estimador definidos.
6. Validación externa con datasets versionados y procedencia verificable.

### E. Interoperabilidad

Construir por contratos y conectores independientes:

- Python y Rust: API estable, bindings, ownership, errores y paridad.
- Bases de datos y servicios: SQL, REST, GraphQL, WebSockets y gRPC.
- Formatos de datos: CSV, JSON, YAML, TOML, XML, Protobuf, MsgPack, BSON, Avro, Parquet y Arrow.
- Ecosistema científico: pandas y flujos de datos reproducibles.

Cada conector debe tener round-trip tests, esquema versionado, tipos soportados, errores, límites de tamaño y pruebas de seguridad. La mera lectura de un formato no equivale a interoperabilidad completa.

### F. IR, compilador y backends

1. Congelar un IR versionado, con esquema, tipos, comandos y semántica de errores.
2. Representar dependencias explícitas y validar lowering AST→IR.
3. Añadir optimizaciones con pruebas de equivalencia semántica: constantes, invariantes, variables muertas, fusión y vectorización.
4. Crear un registro de backends con capacidades declaradas.
5. Implementar y probar por separado: nativo/Rust, WASM, C y Python.
6. Evaluar LLVM IR, JVM bytecode, .NET IL y JavaScript como backends adicionales, cada uno con su propia matriz de conformidad.

Un backend no se declara soportado por generar texto: debe compilar, ejecutar y superar los mismos vectores normativos que el runtime de referencia.

### G. Herramientas, Office y plataforma Linux

- Herramientas de desarrollo: formatter, linter, profiler, debugger, trazas y diagnósticos de fuente.
- RONIN Office: especificación de componentes, importación/exportación, paneles de diagnóstico y pruebas de integración reales.
- Linux: systemd, journald, señales POSIX, pipes, cron, sockets Unix, inotify y sandbox/seccomp.
- Seguridad: límites de recursos, rutas, imports, ejecución de macros, datos externos y aislamiento de procesos.

Estas capacidades requieren perfiles de plataforma, pruebas de integración y documentación de despliegue; no se consideran cubiertas por la CLI actual.

## 3. Orden de ejecución y puertas de salida

| Etapa | Resultado que debe quedar entregado | Puerta de salida |
|---|---|---|
| 0. Consolidación | Una línea principal de trabajo, matriz única y CI fiable | No mantener ramas divergentes con el mismo objetivo |
| 1. Contratos matemáticos | Decisiones sobre CES, coexistencia, deuda, geometría, fatiga y memoria | Fórmula, dominio, unidades, bordes y vectores aprobados |
| 2. Runtime numérico | Python/Rust completos para el perfil matemático definido | Fixtures compartidos, propiedades y paridad |
| 3. Lenguaje | AST, expresiones, funciones, control de flujo, módulos y tipos | Gramática y semántica con tests positivos/negativos |
| 4. Operaciones | solve/simulate/audit/diagnose/plot integrados | CLI, API, IR y resultados coherentes |
| 5. Interoperabilidad | Conectores y formatos soportados | Round-trip, esquemas y pruebas de seguridad |
| 6. Compilación | IR estable y backends ejecutables | Build + ejecución + conformidad por backend |
| 7. Herramientas y plataforma | REPL, Office, perfilado, depuración y Linux | Tests de integración por entorno |
| 8. Cierre integral | Todos los requisitos normativos implementados o con exclusión aprobada | Todas las filas normativas MDES verificadas; sin bloqueos ocultos |

Las etapas pueden avanzar en paralelo cuando sus contratos estén claros. No se debe bloquear trabajo independiente por una ADR no relacionada, pero tampoco se debe codificar una semántica que dependa de una decisión abierta.

## 4. Política de evidencia y finalización

- La matriz MDES es el registro de verdad de requisitos y evidencias.
- Cada capacidad tendrá estado por backend: implementada, parcial, bloqueada o no implementada.
- Los resultados sintéticos se etiquetan como sintéticos; los datos reales conservan fuente, licencia y transformación.
- Los diagnósticos locales no se describen como pruebas globales de identificabilidad.
- Los benchmarks requieren script, entorno, semilla, datos y resultado reproducible.
- La CI verde certifica solo los tests ejecutados.
- No se declara cumplimiento integral hasta que todas las obligaciones normativas tengan evidencia y las discrepancias estén resueltas formalmente.

**Objetivo final inalterado:** completar MDES v0.5. El perfil candidato v1.0, el runtime actual y las entregas incrementales son escalones del programa, no sustitutos de ese objetivo.
