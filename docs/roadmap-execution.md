# Plan de ejecución del roadmap

**Corte de estado:** 2026-11-03  
**Base:** `docs/roadmap.md`, `docs/conformance-matrix.md`, catálogo de fixtures y CI de GitHub Actions.  
**Estado:** v0.2 y v0.3 han ganado cobertura y automatización; ambos siguen abiertos. v0.4/v0.5 no están cerrados. No se declara conformidad global ni aprobación normativa del perfil v1.0.

## Avances integrados desde la línea base anterior

- Validación numérica compartida: sumas de frecuencias dentro/fuera de la tolerancia de 1e-9, y rechazo de pesos de memoria con longitud o suma inválidas.
- CLI: paridad de selección por defecto/explícita en `solve`, `simulate`, `diagnose`, `run` y `check`; diez rutas de fallo compartidas con stdout vacío y diagnóstico en stderr.
- Parser: aceptación/rechazo del subconjunto común, rechazo de escapes Unicode surrogate aislados y un caso testigo de ubicación línea/columna.
- CSV: pruebas unitarias de campos con comas, comillas y saltos de línea en Python y Rust. La paridad CLI sigue cubriendo cabecera, identidad de filas y valores numéricos; no se afirma aún round-trip cross-runtime de todos los casos de escape.
- Trazabilidad: job CI independiente que verifica que todos los fixtures `.ronin` del catálogo existen, están catalogados y enlazan IDs presentes en la matriz.
- Última ejecución completa de CI observada para la validación de memoria: [15/15 jobs correctos](https://github.com/orbitalronin94/ronin-lang/actions/runs/41658388618).

Estos resultados son evidencia de los alcances concretos enumerados, no un porcentaje de conformidad ni sustituyen la revisión de cada requisito MDES.

## v0.2 — matriz, fixtures y trazabilidad

**Estado: en curso.**

- [x] Matriz con IDs y estados Python/Rust.
- [x] Catálogo de fixtures positivos, negativos, diagnósticos y check-only.
- [x] Trazabilidad inicial fixture → requisito.
- [x] Job CI para detectar fixtures sin catalogar, referencias a archivos ausentes y IDs desconocidos.
- [ ] Auditar cada fila I/P y enlazar evidencia específica o una limitación.
- [ ] Completar trazabilidad inversa y revisar que cada requisito del perfil tenga fixture/prueba cuando sea automatizable.
- [ ] Delimitar y aprobar el denominador del perfil v1.0 antes de calcular métricas.
- [ ] Registrar resultados CI por área con enlaces vigentes desde la matriz.

**No cerrar v0.2:** el verificador comprueba integridad del inventario y de los IDs, no que cada fixture demuestre por sí solo el requisito asociado.

## v0.3 — paridad Python/Rust e IR

**Estado: en curso, con cobertura amplia en el subconjunto actual.**

- [x] JSON IR v1: 11 proyectos válidos y cuatro rechazos comparados.
- [x] Solver: 11 proyectos válidos, cuatro rechazos y override explícito de delta.
- [x] Diagnóstico: cuatro fixtures; bootstrap continúa `null`.
- [x] Simulación: 12 proyectos, 12 pasos, semilla 73 y comparación de trayectorias con tolerancia (10^{-12}).
- [x] CSV: 11 proyectos y un proyecto multi-sistema; tests unitarios adicionales de escape en ambos backends.
- [x] Validación: 13 entradas válidas, diez inválidas y cinco casos multi-sistema.
- [x] CLI: selección y diez rutas de error comparadas entre runtimes.
- [ ] Revisar las diferencias intencionadas y los contratos de error/códigos de salida.
- [ ] Completar round-trip de IR y ampliar corpus donde exista una expectativa normativa fiable.
- [ ] Decidir explícitamente si el RNG común forma parte del contrato; por ahora la evidencia se limita a los casos y semilla documentados.
- [ ] Añadir vectores de referencia completos para las fórmulas aún no cubiertas.

La paridad se limita a los casos y campos enumerados por cada script. No equivale a paridad completa de todos los comandos, fórmulas o capacidades de MDES.

## v0.4 — decisiones normativas

**Estado: bloqueado por decisiones/fuentes pendientes.**

Siguen abiertos OPEN-001 a OPEN-007: límite CES cuando lambda tiende a cero, umbral N.2 Test 6, datos NeuralScaling/FamaFrench incompletos, referencia N.6 ausente, catálogo de tipos y contrato de deuda. No implementar deuda, bootstrap ni memoria temporal de orden superior a partir de fórmulas inferidas. Cada resolución requiere fuente normativa completa o propuesta aprobada explícitamente.

## v0.5 — perfil de lenguaje

**Estado: parcial; no declarar completitud.**

- [x] Endurecer y comparar casos del parser compartido, escapes, Unicode y ubicaciones de error.
- [ ] Delimitar explícitamente el subconjunto de lenguaje comprometido.
- [ ] Completar inventario de construcciones léxicas/sintácticas y pruebas positivas/negativas para el perfil aprobado.
- [ ] Resolver si imports/módulos y construcciones de alto nivel pertenecen al perfil v1.0.
- [ ] Recuperar fuentes completas de ejemplos/datasets ausentes; no reconstruirlos por conjetura.
- [ ] Revisar la matriz de errores para contexto y sugerencias sin exigir igualdad textual innecesaria entre backends.

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
