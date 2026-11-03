# Plan de ejecución del roadmap

**Base revisada:** `docs/roadmap.md`, `docs/conformance-matrix.md` y `README.md`.
**Estado de partida:** v0.2 y v0.3 en curso; no se declara conformidad global ni paridad completa.
**Propósito:** convertir los criterios existentes en una secuencia de trabajo verificable, sin alterar MDES v0.5.

## Prioridad inmediata: cerrar la línea base v0.2

### 1. Delimitar el perfil candidato v1.0
- [ ] Identificar qué requisitos de MDES entran en el perfil estable inicial.
- [ ] Separar requisitos normativos obligatorios, capacidades opcionales y propuestas de plataforma.
- [ ] Para cada exclusión, registrar el ID, motivo, impacto visible y condición para reconsiderarla.
- [ ] Aprobar el denominador antes de calcular cualquier porcentaje.

**Salida:** una sección versionada del perfil v1.0, revisable y enlazada desde la matriz. No contar filas heterogéneas como si tuvieran el mismo peso.

### 2. Completar evidencia de la matriz
- [ ] Revisar cada fila I/P y enlazar una prueba concreta o explicar por qué no es automatizable.
- [ ] Distinguir evidencia de parser, validación semántica, ejecución numérica, CLI e interoperabilidad.
- [ ] Corregir estados que hayan quedado obsoletos respecto al código actual.
- [ ] Mantener explícita la diferencia entre “implementado y probado” y “conforme a MDES”.

**Salida:** ninguna fila I/P sin evidencia auditable o nota de limitación.

### 3. Consolidar el corpus de conformidad
- [ ] Mantener fixtures positivos y negativos mínimos para cada comportamiento del perfil.
- [ ] Añadir referencias a requisitos desde el catálogo de fixtures y viceversa.
- [ ] Verificar que los casos parser-only no se ejecuten accidentalmente como aceptación semántica.
- [ ] Mantener los datasets incompletos fuera de la aceptación de ejecución.

**Salida:** corpus compartido Python/Rust trazable, reproducible y sin datos reconstruidos por conjetura.

### 4. Resolver la publicación de resultados CI
- [ ] Confirmar que los jobs Python y Rust publican resultados separados por área.
- [ ] Asegurar que los scripts de paridad se ejecutan como jobs independientes y fallan ante divergencias.
- [ ] Documentar qué suites cubre cada job y qué queda fuera.
- [ ] Registrar enlaces a ejecuciones recientes verificadas; no reutilizar enlaces históricos como prueba del estado actual.

**Salida:** evidencia CI actual enlazada desde la matriz o desde un informe de conformidad.

## Línea paralela: cerrar v0.3 sin bloquear v0.2

- [ ] Mantener fixtures canónicos de JSON IR y comparar Python/Rust en ambos sentidos cuando proceda.
- [ ] Extender la paridad a errores, defaults, selección multi-sistema, serialización y límites numéricos.
- [ ] Documentar diferencias intencionadas, especialmente el contrato de `solve` frente a `run`/ `check`.
- [ ] Definir explícitamente si el RNG común forma parte del contrato; hasta entonces, validar invariantes y trayectorias compartidas con el alcance documentado.
- [ ] Añadir pruebas de integración Rust para cada comando que se anuncie como soportado.

**Salida:** conjunto de fixtures compartidos con resultados equivalentes y diferencias intencionadas justificadas.

## Registro de bloqueos normativos

| ID | Bloqueo | Acción segura hasta tener decisión |
|---|---|---|
| OPEN-001 | Límite CES cuando lambda tiende a cero | Conservar comportamiento actual y excluir la equivalencia disputada del perfil conforme |
| OPEN-002 | Umbral de órdenes en N.2 Test 6 | Mantener fixture verificable separado y documentar el cálculo de la fuente |
| OPEN-003 | NeuralScaling incompleto y fuera de rango | No usar como aceptación; recuperar datos fuente completos |
| OPEN-004 | FamaFrench sin los 720 registros | No sintetizar observaciones; recuperar dataset original |
| OPEN-005 | Referencia N.6 ausente | Registrar discrepancia editorial |
| OPEN-006 | Catálogo de tipos sin sistema de tipos implementado | No anunciar tipado general |
| OPEN-007 | Definición normativa de deuda ausente | Mantener `debt: null`; no sustituirlo por cero ni inventar estimador |

La implementación de deuda, bootstrap o memoria temporal de orden superior no debe comenzar con fórmulas inferidas. Primero hace falta una fuente normativa completa o una decisión de diseño aprobada y registrada.

## Orden recomendado de ejecución

1. Delimitar el perfil v1.0 y sus exclusiones.
2. Completar evidencia de las filas I/P de la matriz.
3. Cerrar trazabilidad bidireccional de fixtures y requisitos.
4. Verificar la separación y publicación de CI.
5. Cerrar discrepancias normativas o excluirlas expresamente del perfil.
6. Completar la paridad Python/Rust del perfil compartido.
7. Solo entonces calcular cobertura y evaluar el cierre de v0.2/v0.3.

## Regla de aceptación

Cada tarea cerrada debe dejar: cambio de código o documento, prueba reproducible, requisito enlazado, resultado CI y limitaciones conocidas. Una tarea documental no cierra por sí sola una carencia de implementación; una prueba verde tampoco resuelve una ambigüedad normativa.
