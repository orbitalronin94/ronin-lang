# Plan de ejecución del roadmap

**Corte de estado:** 2026-11-03  
**Base:** `docs/roadmap.md`, `docs/conformance-matrix.md`, catálogo de fixtures y CI de GitHub Actions.  
**Estado:** v0.2 sigue en curso. v0.3 queda cerrado para el contrato de paridad Python/Rust e IR v1 delimitado en esta hoja; esto no implica conformidad global MDES ni cierra v0.2. v0.4 sigue bloqueado por decisiones normativas; el baseline técnico v0.5 del parser está completado, pero el perfil v1.0 no está aprobado. No se declara conformidad global.

## Avances integrados desde la línea base anterior

- Validación numérica compartida: sumas de frecuencias dentro/fuera de la tolerancia de 1e-9, y rechazo de pesos de memoria con longitud o suma inválidas.
- CLI: paridad de selección por defecto/explícita en `solve`, `simulate`, `diagnose`, `run` y `check`; trece rutas de fallo compartidas con stdout vacío y diagnóstico en stderr.
- Parser: aceptación/rechazo del subconjunto común, rechazo de escapes Unicode surrogate aislados y un caso testigo de ubicación línea/columna.
- CSV: pruebas unitarias de campos con comas, comillas y saltos de línea en Python y Rust. La paridad CLI sigue cubriendo cabecera, identidad de filas y valores numéricos; no se afirma aún round-trip cross-runtime de todos los casos de escape.
- Trazabilidad: job CI independiente que verifica el inventario de fixtures, los IDs del catálogo, las notas de evidencia/limitación de filas I/P y las rutas de archivo citadas en esas evidencias. Las filas marcadas I enlazan también a tests, fixtures o scripts que respaldan el alcance indicado.
- Última ejecución completa de CI observada para la validación de memoria: [15/15 jobs correctos](https://github.com/orbitalronin94/ronin-lang/actions/runs/41658388618).

Estos resultados son evidencia de los alcances concretos enumerados, no un porcentaje de conformidad ni sustituyen la revisión de cada requisito MDES.

## v0.2 — matriz, fixtures y trazabilidad

**Estado: en curso.**

- [x] Matriz con IDs y estados Python/Rust.
- [x] Catálogo de fixtures positivos, negativos, diagnósticos y check-only.
- [x] Trazabilidad inicial fixture → requisito.
- [x] Job CI para detectar fixtures sin catalogar, referencias a archivos ausentes e IDs desconocidos.
- [x] Comprobación inversa automatizada: cada fila I/P de la matriz debe incluir una nota de evidencia o limitación ([PR #67](https://github.com/orbitalronin94/ronin-lang/pull/67), [CI 15/15](https://github.com/orbitalronin94/ronin-lang/actions/runs/41667655968)).
- [x] Verificar unicidad de IDs de fila y exigir que las referencias del catálogo apunten a IDs que existan como filas reales de la matriz.
- [x] Exigir al menos una referencia explícita a test, fixture o script de paridad en cada fila I/P.
- [x] Comprobar que todos los IDs de la propuesta v1.0 mapean a filas reales de la matriz con referencia MDES y que los IDs del alcance candidato están marcados I/P; la revisión de exactitud y aprobación del perfil siguen pendientes.
- [x] Auditar NORM-009 / N.2 Test 6: separar la prueba sintética de la rama inactiva del vector literal de la fuente, cuyo rango real (2.9952) contradice el esperado (3.0); registrar estado A y mantener OPEN-002 sin alterar la semántica.
- [x] Añadir referencias a archivos concretos de implementación en las filas I/P y enlazar tests, fixtures o scripts en las filas marcadas I; el job CI comprueba que las rutas citadas existen.
- [x] Validar referencias `ruta::símbolo` contra declaraciones `def`/`fn` reales; tests unitarios rechazan menciones en comentarios/cadenas y coincidencias por prefijo ([CI](https://github.com/orbitalronin94/ronin-lang/actions/runs/41688569556)).
- [ ] Revisar sustantivamente el resto de filas I/P y confirmar que la evidencia enlazada cubre el alcance descrito.
- [ ] Completar trazabilidad inversa de requisitos a pruebas/fixtures cuando sea automatizable.
- [ ] Delimitar y aprobar el denominador del perfil v1.0 antes de calcular métricas.
- [ ] Registrar resultados CI por área con enlaces vigentes desde la matriz.

**No cerrar v0.2 todavía:** el verificador comprueba inventario, unicidad y existencia de IDs de fila, mapeo de IDs del perfil candidato, presencia de notas, referencias explícitas a pruebas y resolución de rutas; no juzga si la referencia MDES es semánticamente exacta ni si cada prueba demuestra el requisito.

## v0.3 — paridad Python/Rust e IR

**Estado: cerrado para el contrato compartido documentado (no conformidad integral MDES).**

- [x] JSON IR v1: 12 proyectos válidos y cuatro rechazos comparados; `ir_json_escaping.ronin` cubre escapes JSON, Unicode y metadata anidada.
- [x] Solver: 11 proyectos válidos, cuatro rechazos y override explícito de delta.
- [x] Diagnóstico: cuatro fixtures; bootstrap continúa `null`.
- [x] Simulación: 12 proyectos, 12 pasos, semilla 73 y comparación de trayectorias con tolerancia (10^{-12}).
- [x] CSV: 11 proyectos y un proyecto multi-sistema; tests unitarios adicionales de escape en ambos backends.
- [x] Validación: 13 entradas válidas, diez inválidas y cinco casos multi-sistema.
- [x] CLI: selección y trece rutas de error comparadas entre runtimes.
- [x] Documentar diferencias intencionadas y contratos observados: selección por comando; errores comparados por fallo no-cero, stdout vacío y stderr explicativo, sin exigir igualdad textual ni códigos numéricos idénticos.
- [x] Alinear opciones CLI Rust con Python: `--system` solo en check/solve/simulate/diagnose y `--delta` solo en solve/run; añadir tres casos de rechazo a la paridad CLI.
- [x] Normalizar números no finitos del JSON CLI Python a cadenas `inf`/`-inf`/`nan`, con `allow_nan=False`, y fijar el mismo contrato en tests Rust/Python.
- [x] Verificar el ciclo de serialización del IR v1 en ambos runtimes mediante parseo JSON estructural y comparación de objetos; el IR sigue siendo un formato de salida, no un importador/round-trip de vuelta a `.ronin`.
- [x] Delimitar RNG: la misma semilla garantiza reproducibilidad dentro de cada backend; no se declara secuencia aleatoria común Python/Rust.
- [x] Registrar vectores ausentes como fuera del alcance de paridad ejecutable mientras falten datos/fuentes normativas (OPEN-001 a OPEN-007); no se inventan resultados esperados.

La paridad se limita a los casos y campos enumerados por cada script. Los contratos de error no exigen texto/código idéntico; la simulación no promete secuencia RNG común; IR v1 se emite y compara estructuralmente, pero no se importa como fuente. No equivale a paridad completa de todos los comandos, fórmulas o capacidades de MDES.

## v0.4 — decisiones normativas

**Estado: bloqueado por decisiones/fuentes pendientes.**

Siguen abiertos OPEN-001 a OPEN-007: límite CES cuando lambda tiende a cero, umbral N.2 Test 6 (NORM-009 A por discrepancia numérica del vector fuente), datos NeuralScaling/FamaFrench incompletos, referencia N.6 ausente, catálogo de tipos y contrato de deuda. `docs/v1-profile-proposal.md` asigna ahora una exclusión candidata explícita a cada uno; esto no es aprobación del perfil ni una decisión normativa. No implementar deuda, bootstrap ni memoria temporal de orden superior a partir de fórmulas inferidas. Cada resolución requiere fuente normativa completa o propuesta aprobada explícitamente.

## v0.5 — perfil técnico del lenguaje

**Estado: baseline técnico del parser compartido completado; el compromiso de compatibilidad del perfil v1.0 sigue pendiente de aprobación explícita.**

- [x] Endurecer y comparar el parser compartido: escapes, Unicode, controles sin escape, espacios admitidos, literales, claves y ubicaciones de error.
- [x] Delimitar el subconjunto actualmente implementado en [language-subset.md](language-subset.md), sin presentarlo como gramática completa de MDES ni como aprobación normativa.
- [x] Inventariar construcciones léxicas/sintácticas del subconjunto y añadir evidencia positiva/negativa en ambos backends.
- [x] Revisar el contrato de errores: categoría/fallo y ubicaciones en casos testigo; no exigir igualdad textual entre runtimes.
- [ ] Aprobar explícitamente qué construcciones de alto nivel, imports y módulos formarían parte del perfil v1.0; hasta entonces quedan fuera del subconjunto comprometido.
- [ ] Recuperar fuentes completas de ejemplos/datasets ausentes; no reconstruirlos por conjetura.

## Bloqueos normativos

| ID | Bloqueo | Tratamiento actual |
|---|---|---|
| OPEN-001 | Límite CES cuando lambda tiende a cero | Mantener la formulación implementada documentada; no declarar equivalencia disputada |
| OPEN-002 | Umbral de órdenes en N.2 Test 6 | Mantener fixture verificable y registrar discrepancia de fuente |
| OPEN-003 | NeuralScaling incompleto/fuera de rango | Excluir de aceptación hasta recuperar fuente válida |
| OPEN-004 | FamaFrench sin los 720 registros | No sintetizar observaciones |
| OPEN-005 | Referencia N.6 ausente | Discrepancia editorial abierta |
| OPEN-006 | Catálogo de tipos sin sistema de tipos | No anunciar tipado general |
| OPEN-007 | Definición normativa de deuda ausente | Mantener `debt: null`; no sustituirlo por cero ni inventar estimador |

## Regla de aceptación

Cada checkpoint cerrado debe enlazar requisito, implementación, prueba reproducible, resultado CI y límites. Una suite verde acredita únicamente los casos que ejecuta. Las decisiones normativas, la aprobación del perfil v1.0 y la conformidad integral requieren revisión explícita y no se deducen de la CI.
