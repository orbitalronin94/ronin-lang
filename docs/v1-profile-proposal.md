# Propuesta de perfil de conformidad RONIN v1.0

**Estado:** propuesta técnica para revisión; no aprobada como cambio normativo.
**Base:** MDES v0.5, `docs/conformance-matrix.md`, `docs/roadmap.md`.
**Objetivo:** fijar un denominador honesto y verificable para medir el primer release estable.

Esta propuesta delimita un perfil inicial de producto. No redefine MDES, no convierte requisitos opcionales en obligatorios y no afirma conformidad integral con MDES v0.5. La aprobación final del alcance requiere revisión explícita del mantenedor del proyecto.

## 1. Reglas del perfil

1. Un requisito entra en el perfil solo si su comportamiento está definido y puede probarse con fixtures reproducibles.
2. La evidencia de parser, validación, ejecución, CLI e interoperabilidad se contabiliza por separado.
3. Un requisito marcado I para un subconjunto solo cubre ese subconjunto.
4. Un requisito ambiguo o con datos fuente ausentes queda excluido hasta que exista una decisión o evidencia válida.
5. Python y Rust deben compartir el contrato anunciado; las capacidades exclusivas de un backend se etiquetan como tales.
6. El perfil se versiona independientemente de MDES. La exclusión de una función no borra su condición de objetivo futuro.

## 2. Candidato de alcance incluido

La siguiente tabla propone el núcleo mínimo que ya tiene evidencia significativa. La inclusión definitiva depende de que la revisión de matriz confirme cada prueba y de que se cierren las diferencias señaladas.

| Área | IDs de matriz | Alcance candidato | Condición de aceptación |
|---|---|---|---|
| Modelo de proyecto | CORE-001, LANG-001–004, TYPE-001 | Sistemas, agentes, parámetros, escalares y metadatos admitidos | Fixtures positivos/negativos en ambos parsers; round-trip de IR |
| Parser compartido | PARSER-001, PY-003/004, RS-001/002 | Subconjunto léxico/sintáctico implementado y documentado | Corpus compartido y pruebas de rechazo |
| Validación | VAL-CLI-001, TYPE-004/005 en alcance común | Validación previa a ejecución/compilación para invariantes compartidas | Mismos proyectos aceptados/rechazados y errores clasificados |
| Solver | CORE-002, NORM-006 y subconjunto probado de PY-006/RS-006 | PUSFRE y perfiles CES/Hill/CES-Hill que superan fixtures compartidos | Vectores de referencia, tolerancias explícitas y paridad |
| Simulación | PY-007, SIM-002 | Contrato de simulación actualmente compartido | Semilla, invariantes, historial y tolerancia documentados |
| Diagnóstico | CORE-007, SIM-003, subconjunto PY-008/RS-008 | Rango/degeneración para los casos compartidos; sin bootstrap inferido | Fixtures activos/inactivos/indeterminados y paridad de informe |
| IR | INTEROP-008, BUILD-001, RS-004/005 | JSON IR v1 normalizado, validado y equivalente | Fixtures canónicos, comparación estructural y errores |
| CLI | PY-009, RS-009, BUILD-013/014 | Comandos list/check/solve/run/compile/simulate/diagnose en el alcance real de cada backend | Pruebas de integración; diferencias de selección documentadas |
| CSV | INTEROP-009 | Exportación CSV en Python y Rust para el corpus compartido | `scripts/check_csv_parity.py` compara cabecera, filas y valores numéricos; tests unitarios por backend cubren comas, comillas y CR/LF combinados, pero falta incorporarlos a la paridad CLI cross-runtime antes de declarar cobertura general de CSV |

**Restricción importante:** que un ID aparezca aquí no lo convierte automáticamente en conforme. El perfil solo lo incorpora cuando la condición de aceptación se satisface en CI y la matriz apunta a esa evidencia.

## 3. Exclusiones explícitas del primer perfil

Estas capacidades permanecen fuera del perfil candidato inicial. Pueden incorporarse en una versión posterior mediante pruebas y, cuando corresponda, decisiones normativas.

| Área | IDs / referencia | Motivo de exclusión |
|---|---|---|
| Estimación de deuda | CORE-004, NORM-004, OPEN-007 | No existe contrato normativo íntegro; `debt: null` es el comportamiento honesto |
| Geometría y routing fatigue | CORE-005/006 | No hay implementación ejecutable demostrada |
| Coexistencia normativa completa | CORE-003, NORM-003 | La fórmula/contrato requiere cierre; no basta con el campo o el cálculo parcial |
| Equivalencia CES cuando lambda→0 | NORM-007, OPEN-001 | La fuente contiene formulaciones incompatibles |
| Umbral exacto de órdenes del test N.2 | OPEN-002 | La cifra publicada no coincide con el cálculo indicado |
| Bootstrap e intervalos | PY-008, RS-008 | Método, semillas y niveles de confianza no definidos; no devolver estimaciones ficticias |
| Memoria temporal de orden superior | Referencia R.9 / matriz correspondiente | Kernel no definido/implementado |
| Ejemplos y datasets incompletos | EX-006/007/008, OPEN-003/004 | No hay datos fuente completos y verificables |
| Sistema de tipos general | TYPE-002, TYPE-006–009 | Catálogo y sistema de tipos no implementados |
| Funciones, control de flujo y módulos | LANG-006–015 | No existe intérprete general |
| Concurrencia | CONC-001–006 | No existe runtime de actores/canales/futures |
| Interoperabilidad general | INTEROP-001–007 | Bridges y formatos no implementados |
| Code generation y backends | BUILD-002–006, RS-011–013 | Nativo, WASM, C, bindings y otros backends no implementados |
| Office y herramientas gráficas | v0.7 / Parte VII | Requiere alcance propio, prototipo y pruebas de interfaz |
| Optimizador, profiler y debugger | BUILD-008–010 | No implementados |
| Conformidad integral MDES v0.5 | Global | El perfil inicial no cubre todas las secciones de la especificación |

## 4. Política de medición

No se publicará un porcentaje hasta que cada requisito del perfil tenga:
- ID único y referencia exacta a MDES;
- clasificación de obligatoriedad y backend aplicable;
- estado I/P/D/N/A con definición consistente;
- evidencia de test o justificación documentada;
- peso unitario igual dentro de su categoría, sin mezclar requisitos de producto, ejemplos y propuestas de plataforma.

Se publicarán al menos cuatro métricas separadas:
1. **Trazabilidad:** requisitos del perfil con ID y referencia / requisitos del perfil.
2. **Evidencia:** requisitos con prueba identificada / requisitos del perfil.
3. **Implementación:** requisitos con comportamiento implementado / requisitos del perfil.
4. **Conformidad:** requisitos que superan todas sus pruebas de aceptación / requisitos del perfil.

Las métricas se calcularán por área y backend. No se promediarán porcentajes de áreas con denominadores distintos.

## 5. Puertas para aprobar el perfil

- [ ] Revisión de cada ID incluido contra la especificación y el código actual.
- [ ] Confirmación de pruebas de aceptación para cada requisito incluido.
- [ ] Diferencias Python/Rust documentadas y aceptadas explícitamente.
- [ ] Exclusiones y sus impactos visibles documentados.
- [ ] Aprobación explícita del mantenedor.
- [ ] Enlace desde la matriz, roadmap y documentación de release.

Hasta completar estas puertas, este archivo es una propuesta de trabajo y no un compromiso de compatibilidad publicado.

## 6. Siguiente revisión

La siguiente revisión debe resolver el mapeo requisito → test concreto. Prioridad:
1. CORE-001/002, PARSER-001 y TYPE-001.
2. VAL-CLI-001 y TYPE-004/005.
3. Solver y vectores normativos disponibles.
4. SIM-002 y SIM-003.
5. BUILD-001 / INTEROP-008 y selección de sistemas CLI.
6. CSV Python y brecha CSV Rust.

Cada cambio de estado debe actualizar también `docs/conformance-matrix.md`; no mantener estados divergentes entre documentos.
