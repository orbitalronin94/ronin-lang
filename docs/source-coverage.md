# Cobertura de RONIN 1.1 y notas de conformidad

**Versión principal en castellano. English version follows below.**

Este documento relaciona el comportamiento del repositorio con *RONIN 1.1 — Edición Familia*. Distingue el código ejecutable de las propuestas de arquitectura y de los ejemplos incompletos.

## Runtime de referencia Python

| Sección fuente | Estado en el repositorio |
|---|---|
| R.3–R.4: modelo de datos y errores | Implementado en `ronin/model.py` y `ronin/errors.py` |
| R.5–R.6: lexer y parser | Implementado para bloques `system`, agentes en línea, cadenas, arrays, comentarios y números |
| R.7: validador | Rangos, normalización de frecuencias y coherencia entre modelos |
| R.8–R.9: semántica y solver | PUSFRE, CES, Hill, CES-Hill, asignación, `k_min` y diagnóstico de rango K–α |
| R.10: simulador | Kernel reproducible de deriva, ruido y simplex |
| R.11: diagnóstico | Rango Ω, estado de degeneración, identificabilidad y recomendación |
| R.12: CLI | Comandos `check`, `solve`, `simulate` y `diagnose` |
| R.13: pruebas | Pruebas de aceptación y regresión con pytest |
| R.14: ejemplos | Maquinas, Pesca, CES y ejemplos de degeneración ejecutables |

## Límites de implementación explícitos

1. **Estimador de deuda.** El código Python de R.8 define `debt(system)` como `0.0`. No se proporciona un estimador ejecutable en R.3–R.14. El runtime conserva ese placeholder y no afirma auditar deuda.
2. **Bootstrap.** La implementación de diagnóstico de la fuente deja pendiente el ajuste bootstrap. El runtime devuelve `bootstrap_ci: null`.
3. **Memoria temporal.** Se definen `memory_order` y `memory_weights`, pero no un kernel temporal ejecutable. Los órdenes superiores a 1 se rechazan en ejecución en vez de aproximarse silenciosamente.
4. **Datos NeuralScaling/FamaFrench.** Los ejemplos suministrados contienen `...` en lugar de los 46/720 registros completos. No son fixtures ejecutables y no fabricamos observaciones.
5. **Cobertura del lenguaje del parser.** El parser Python implementa el subconjunto ejecutable de bloques `system` descrito en R.6; no es un intérprete general de todas las construcciones de alto nivel (`let`, bucles, condicionales, DSL de auditoría, etc.).

## Discrepancias de la fuente que requieren decisión

### Umbral del fixture de degeneración inactiva

El test de la fuente usa frecuencias `0.001, 0.01, 0.989`. Su rango real es `log10(0.989 / 0.001) = log10(989) ≈ 2.9952`, inferior al umbral declarado de 3.0 órdenes. Por tanto, el algoritmo lo clasifica correctamente como activo. El repositorio conserva este hecho en una prueba de regresión y usa `0.0009, 0.0090, 0.9901` para un fixture realmente inactivo.

### Contradicción de rango en NeuralScaling

El extracto NeuralScaling incluye `phi: 19.2` y `psi: 25.3`, mientras R.7 restringe ambos campos a [0,1]. Además, faltan 44 de los 46 registros. El ejemplo no puede superar el validador tal como está escrito.

### Límite CES cuando λ tiende a cero

La media de potencia CES converge a la media geométrica ponderada cuando λ tiende a cero. El runtime aplica ese límite para los modelos `ces` y `ces_hill`, incluso cuando `abs(lambda) < 1e-6`. PUSFRE y Hill mantienen su fórmula específica y no entran en la rama CES. Esta decisión prioriza el límite matemático descrito en el apéndice A.1.1 frente a la rama de compatibilidad de R.8 que reutilizaba el producto PUSFRE. La prueba `test_ces_near_zero_lambda_uses_geometric_mean` fija este comportamiento.

### Coexistencia y delta

La fuente proporciona la fórmula de `k_min` e indica que se advierta cuando el recurso disponible sea inferior a ese umbral, pero no define un estimador separado de deuda/coexistencia. El runtime expone `k_min` para que el consumidor pueda inspeccionar la comparación.

## Otros objetivos descritos en el Markdown

- **Rust (Parte VI / 6.1–6.14):** hay arquitectura y bocetos; el parser se describe como esqueleto funcional y memoria/IR/backends siguen incompletos. Este repositorio no presenta un crate Rust como conforme.
- **WASM y C (6.13–6.14):** son bocetos de extensión; el generador C contiene puntos suspensivos y no es un backend completo.
- **RONIN Office (Parte VII):** se describen paneles, mockups y tablas de estado. Este runtime Python no incluye la interfaz Office.
- **Motor JavaScript (7.9):** el ejemplo contiene puntos suspensivos y no es un backend completo ni conforme.
- **Funciones futuras:** sistemas continuos, orquestación, optimización, DSL de auditoría y construcciones avanzadas permanecen como especificación o trabajo futuro.

## Política de conformidad

Que CI esté en verde significa que la implementación Python supera las pruebas y ejemplos ejecutables de este repositorio. No certifica Rust, WASM, C, Office, bootstrap, auditoría de deuda, memoria temporal ni datasets ausentes de la fuente. No se afirma rendimiento sin un benchmark reproducible.

---

# RONIN 1.1 source coverage and conformance notes (English)

This document maps repository behavior to *RONIN 1.1 — Edición Familia* and distinguishes executable code from proposals and incomplete examples.

## Python reference runtime

| Source section | Repository status |
|---|---|
| R.3–R.4 data model and errors | Implemented |
| R.5–R.6 lexer and parser | Implemented for the executable `system` subset |
| R.7 validator | Ranges, frequency normalization and model coherence |
| R.8–R.9 semantics and solver | PUSFRE, CES, Hill, CES-Hill, allocation, `k_min` and K–alpha diagnostics |
| R.10 simulator | Seeded drift/noise/simplex kernel |
| R.11 diagnostics | Omega range, degeneracy, identifiability and recommendation |
| R.12 CLI | `check`, `solve`, `simulate`, `diagnose` |
| R.13 tests | pytest acceptance and regression suite |
| R.14 examples | Runnable Maquinas, Pesca, CES and degeneracy fixtures |

## Known implementation limits

Debt estimation remains a `0.0` placeholder; bootstrap confidence intervals return null; higher-order temporal memory has no executable kernel; NeuralScaling and FamaFrench source datasets are incomplete; and Rust, WASM, C, Office and the JavaScript engine are proposal/sketch material rather than complete backends.

## CES limit as lambda approaches zero

The CES power mean converges to the weighted geometric mean as lambda approaches zero. The runtime now applies that limit for `ces` and `ces_hill`; PUSFRE and Hill retain their dedicated formula. This follows Appendix A.1.1 over the compatibility branch in R.8. A regression test locks in this decision.

## Conformance policy

Green CI certifies only the Python implementation, tests and executable examples in this repository. It does not certify unspecified or incomplete backends, estimators, temporal memory kernels or missing datasets.
