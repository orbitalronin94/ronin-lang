# Propuesta de perfil de compatibilidad — RONIN Runtime v0.5

**Estado:** propuesta para aprobación del mantenedor; no es todavía un compromiso de compatibilidad.  
**Objetivo:** delimitar el producto publicable `RONIN Runtime v0.5.0`.  
**Base normativa:** MDES v0.5.  
**Versionado:** Runtime v0.5.0 y MDES v0.5 son líneas independientes. Esta propuesta no declara completa MDES v0.5.

## 1. Qué se pretende declarar

RONIN Runtime v0.5 será un runtime declarativo reproducible para proyectos `system` del subconjunto compartido Python/Rust. Debe permitir:

1. parsear proyectos del subconjunto documentado;
2. validar invariantes compartidas;
3. resolver los modelos con fixtures de referencia;
4. simular trayectorias con semilla común en el corpus declarado;
5. compilar a JSON IR v1;
6. ejecutar comandos CLI comunes y exportar resultados JSON/CSV.

No será todavía el lenguaje general de MDES: no incluye funciones generales, módulos, imports, macros, concurrencia ni un sistema de tipos de usuario completo.

## 2. Perfil candidato incluido

| Área | IDs de matriz | Compromiso propuesto para v0.5 | Evidencia / gate |
|---|---|---|---|
| Modelo de proyecto | CORE-001, LANG-001–004, TYPE-001, TYPE-003 | Declaraciones system/agent/params, campos escalares y metadata admitida; AST/modelo Python y Rust | Corpus positivo/negativo; metadata anidada; no implica tipos de usuario |
| Parser | PARSER-001, PY-003/004, RS-001/002, subconjunto LANG-005 | Tokens, escapes, Unicode, ubicaciones de error y arrays/objetos en los contextos admitidos | `scripts/check_parser_parity.py`; 9 archivos válidos, 3 fuentes inline válidas y 29 inválidas |
| Validación | VAL-CLI-001, TYPE-004/005 en alcance común | Invariantes compartidas antes de solve/compile/check; diferencias internas de arquitectura no visibles al usuario | `scripts/check_validation_parity.py`; mismos casos aceptados/rechazados del corpus |
| Solver | CORE-002, NORM-006, subconjunto PY-006/RS-006 | PUSFRE, CES, Hill y CES-Hill para los vectores/casos cubiertos; fitness y allocation con tolerancias explícitas | `scripts/check_runtime_parity.py` y `scripts/check_randomized_runtime_parity.py`; 11 proyectos más 80 sistemas deterministas generados y override de delta |
| Simulación | PY-007, SIM-002, subconjunto RS-007 | Kernel documentado, historial, simplex, supervivencia y trayectoria común bajo semilla en el corpus | `scripts/check_simulation_contracts.py` y `scripts/check_randomized_simulation_parity.py`; 12 proyectos más 15 sistemas generados, 24 pasos, seeds fijas, tolerancia 1e-12 |
| IR | INTEROP-008, BUILD-001, RS-004/005 | Compilación validada a JSON IR v1; metadata anidada y números no finitos normalizados | `scripts/check_ir_parity.py`; 12 proyectos válidos y 4 rechazos |
| CLI | PY-009, RS-009, BUILD-007, subconjunto BUILD-013/014 | `list`, `check`, `solve`, `run`, `compile`, `simulate`; `run` procesa todos los sistemas y `solve` selecciona el primero por defecto | Tests de integración; 13 fallos compartidos; textos/códigos exactos de error no son idénticos |
| CSV | INTEROP-009 | Exportación CLI de resultados del esquema actual en Python y Rust | `scripts/check_csv_parity.py`; 11 proyectos y un multi-sistema; helpers CSV cubren coma, comillas, CR/LF en tests unitarios |
| Ejemplos | EX-001/002/003 | Maquinas, Maquinas CES y Pesca como ejemplos ejecutables del perfil | Tests y scripts de paridad; no sustituye datasets normativos ausentes |

### Límites internos del contrato

- `coexistence` y `k_min` se exponen actualmente, pero su contrato normativo completo permanece parcial (CORE-003/NORM-003); no se usarán como criterio de conformidad plena.
- `debt` permanece `null`; no se interpreta como cero ni como estimación.
- Los números no finitos de JSON se representan como cadenas `"inf"`, `"-inf"`, `"nan"`.
- IR v1 es una salida validada; no existe importador IR→RONIN ni round-trip.
- Python y Rust comparten los casos declarados, no toda la superficie de MDES.
- Los errores deben fallar limpiamente con stdout vacío y stderr explicativo; no se exige igualdad textual ni códigos de salida idénticos.

## 3. Capacidades experimentales o fuera del perfil estable

| Área | IDs / referencia | Tratamiento propuesto |
|---|---|---|
| Diagnóstico de degeneración e identificabilidad | CORE-007, SIM-003, PY-008, RS-008, NORM-005 | Mantener disponible como experimental hasta aprobar ADR-0002 y definir modos libres/fijos/desconocidos; no prometer identificabilidad individual |
| Bootstrap CI | PY-008, RS-008 | No implementado; `bootstrap_ci: null`; fuera del perfil |
| Límite CES lambda→0 | NORM-007, OPEN-001, ADR-0001 | Fuera del perfil hasta decisión normativa; no afirmar CES(lambda→0)=PUSFRE |
| Umbral exacto N.2 Test 6 | OPEN-002, NORM-009 | Fuera del perfil normativo hasta corregir la discrepancia 2.9952 vs 3.0 |
| Coexistencia normativa completa | CORE-003, NORM-003 | Parcial; requiere fuente/decisión aprobada |
| Deuda | CORE-004, NORM-004, OPEN-007 | Fuera; contrato/estimador no recuperado |
| Geometría y fatiga de routing | CORE-005/006 | No implementadas |
| Memoria temporal de orden superior | referencia R.9 | Fuera; kernel no definido/implementado |
| Datasets normativos ausentes | OPEN-003/004, EX-006/007/008 | Fuera; no inventar datos ni reproducir ejemplos incompletos |
| Referencia N.6/N.5 | OPEN-005 | Fuera hasta recuperar la fuente |
| Sistema de tipos general | OPEN-006, TYPE-002, TYPE-006–009 | Fuera; solo se soportan los tipos/estructuras del subconjunto |
| Lenguaje general | LANG-006–015 | Funciones, expresiones generales, control de flujo, módulos/imports y macros fuera |
| Concurrencia | CONC-001–006 | Actores, canales, futures, streams y backpressure fuera |
| Interoperabilidad y backends | INTEROP-001–007, RS-011–013, BUILD-002–006 | PyO3, WASM, C, generación nativa y conectores externos fuera |
| REPL y Office | PY-009 (REPL), Parte VII | REPL Python básico y prototipo Office no son capacidades comunes/estables |
| Investigación avanzada | PR #35 | FIM/Jacobianos, D-optimal, Sobol y SIR quedan experimentales hasta revisión, API y validación por dominio |

## 4. Condiciones de aprobación

- [ ] C1 cerrado: revisión semántica de las 62 filas I/P, estados y suficiencia de evidencia.
- [x] C2 cerrado para el contrato compartido documentado (issue #39).
- [ ] C3: cada OPEN-001…OPEN-007 resuelto por fuente/ADR aprobada o excluido expresamente del perfil.
- [ ] C4: gramática/subconjunto, errores y separación parser/validación/ejecución revisados.
- [ ] C5: PR #35 particionada; solo se integra en v0.5 lo que tenga contrato, tests y paridad. El resto queda experimental.
- [ ] C6: instalación limpia, quickstart, ejemplos, dependencias y plataformas declaradas verificados.
- [ ] C7: release candidate con matriz, changelog, migración y CI completa.
- [ ] C8: tag `v0.5.0`, artefactos y checksums.

## 5. Declaración permitida al aprobarse

La declaración permitida será:

> “RONIN Runtime v0.5.0 implementa el perfil de compatibilidad RONIN Runtime v0.5 descrito en este documento, en los backends y casos de prueba enumerados. No declara conformidad integral con MDES v0.5.”

No se permite afirmar “RONIN es completamente conforme con MDES v0.5” mientras existan requisitos excluidos, ambiguos o sin evidencia.

## 6. Decisiones que requieren al mantenedor

1. Aprobar o modificar el alcance de este perfil.
2. Resolver si diagnóstico de identificabilidad queda experimental (recomendación actual) o si se prioriza aprobar ADR-0002 e implementarlo.
3. Aprobar ADR-0001 o mantener el límite CES próximo a cero fuera del perfil.
4. Confirmar que las capacidades avanzadas de PR #35 permanecen experimentales para v0.5 o seleccionar explícitamente cuáles deben entrar.
