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
| Ejemplos | EX-001–005 | Maquinas, Maquinas CES, Pesca, fixtures de degeneración y parser de ejemplos | Alineado; EX-005 es parser-only y se mantiene P |

**Total:** 62 filas I/P revisadas. El estado se conserva salvo correcciones ya integradas: NORM-005/P por la heurística de libertad de parámetros, y deuda `None/null` en NORM-004/PY-006. No se elevan estados P a I por añadir más casos de estrés.

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
- Tipos generales, concurrencia, streams consumibles, imports, funciones, macros y backends no implementados siguen fuera del perfil.
- La prueba de 1.000 agentes es funcional; no constituye benchmark ni claim de rendimiento.

## Gate C1

C1 podrá cerrarse cuando el workflow de trazabilidad pase sobre el commit que contiene esta auditoría y la matriz/profile mantengan las referencias y estados coherentes. La aprobación del perfil es C4, y las decisiones normativas OPEN-* son C3; no se mezclan con el cierre de la auditoría de evidencia.
