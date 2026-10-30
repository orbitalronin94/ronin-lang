# Anexo normativo RONIN 1.1

> Transcripción del anexo normativo de la fuente 1.1. Los contratos marcados “sin cambios respecto a 1.0” remiten a la especificación original; no se sustituyen por algoritmos inventados.

1. Parsear el programa.
2. Validar tipos, rangos y número de agentes.
3. Validar que `sum(frequency)` sea `1 ± tolerance` (1e-9).
4. **Validar coherencia `model` ↔ parámetros.**
5. **Calcular `Ω_sat_i = hill(Ω_i, K, α_h)`.**
6. **Calcular `F_i = ces_combine(Φ_i, Ψ_i, Ω_sat_i, λ, w)`.**
7. Calcular `allocation[i] = resource * fitness[i] / sum(fitness)`.
8. Calcular coexistencia y `k_min`.
9. Calcular deuda.
10. **Calcular `omega_range` y `degeneracy`.**
11. Construir el `Solution` con advertencias.

Si `sum(fitness) == 0`, `solve` debe devolver un error de sistema degenerado y nunca dividir por cero.

### N.1.2 Contrato de `simulate`

*(Sin cambios respecto a 1.0.)*

### N.1.3 Contrato de coexistencia

*(Sin cambios respecto a 1.0.)*

### N.1.4 Contrato de deuda

*(Sin cambios respecto a 1.0.)*

### N.1.5 Contrato de diagnóstico (nuevo en 1.1)

`diagnose` debe reportar:
- `omega_range_orders`: `log10(max(Ω) / min(Ω))`.
- `degeneracy`: `"inactive"` si `omega_range_orders >= 3.0`, `"active"` si `< 3.0` y `K, alpha_h` libres, `"unknown"` en otro caso.
- `K_identifiable`, `alpha_h_identifiable`: booleanos coherentes.
- `recommendation`: texto accionable.

---

## N.2 TESTS NORMATIVOS

### Test 1 — Compatibilidad 1.0

Programa RONIN 1.0 sin `model` debe producir exactamente los mismos valores que RONIN 1.0.

```
fitness    = [0.48, 0.20]
allocation ≈ [70.5882352941, 29.4117647059]
model_used = "pusfre"
```

### Test 2 — model "pusfre" explícito

Programa con `model: "pusfre"` explícito debe producir idéntico resultado al Test 1.

### Test 3 — CES con λ → 0 recupera PUSFRE

Programa con `model: "ces"`, `lambda: 1e-7` debe producir resultado indistinguible de PUSFRE (dentro de 1e-6).

### Test 4 — Coherencia de modelo

Programa con `model: "pusfre"` y `lambda: 0.5` debe fallar con `SemanticError` (código 2).

### Test 5 — Degeneración activa

Programa con Ω estrecho y `model: "ces_hill"` con `K, alpha_h` libres debe reportar `degeneracy: "active"`.

### Test 6 — Degeneración inactiva

Programa con Ω cubriendo 3+ órdenes de magnitud debe reportar `degeneracy: "inactive"`.

### Test 7 — Diagnóstico sobre datos reales

Programa con dataset Neural Scaling (Ω ~ 3 órdenes) debe reportar `degeneracy: "inactive"` y `omega_range_orders: 3.0 ± 0.1`.

---

## N.3 CONFORMIDAD

Un runtime es RONIN 1.1 conforme si:

- Acepta todos los programas válidos definidos en este documento.
- Rechaza programas inválidos con error identificable.
- **Rechaza violaciones de coherencia de modelo con `SemanticError`.**
- Produce los resultados numéricos normativos dentro de `1e-9` de tolerancia relativa.
- Mantiene la suma de allocation dentro de `1e-9` de `resource`.
- Respeta `seed` en simulación.
- **Reporta `degeneracy` coherente con `omega_range_orders`.**
- No presenta como benchmark medido ningún número que no haya sido reproducido por el runtime.

---

## N.4 ESTADO DE LAS EXTENSIONES

| Extensión | Estado | Implementación |
|-----------|--------|----------------|
| Familia CES-Saturada en Python | ✅ Especificado y ejecutable | R.6–R.11 |
| Comando `diagnose` | ✅ Especificado y ejecutable | R.11 |
| Coherencia de modelo | ✅ Especificado | R.7 |
| Backend Rust con familia | 🟡 Especificado | 6.7–6.10 |
| Backend WASM con diagnose | 🟡 Especificado | 6.13 |
| Backend C con Hill/CES | 🟡 Especificado | 6.14 |
| RONIN Office + Panel Diagnose | 🟡 Especificado | 7.8 |
| Motor RONIN JS extendido | ✅ Especificado | 7.9 |

---

## N.5 POLÍTICA DE AFIRMACIONES VERIFICABLES

Esta edición adopta una regla estricta: la especificación distingue entre **norma**, **implementación existente**, **propuesta de implementación**, **ejemplo** y **resultado medido**. Una capacidad no se presenta como disponible por el mero hecho de estar descrita. Un benchmark no se presenta como medido sin artefactos reproducibles. Una garantía no se presenta como absoluta si depende de supuestos no formalizados.

La familia CES-Saturada es una extensión matemática validada en el Tratado v3.5 (Neural Scaling positivo, Fama-French negativo). Su incorporación a RONIN es especificación; su implementación completa en Rust es propuesta. La degeneración K–α está demostrada analíticamente en la Proposición 5.1 del Tratado v3.5.

---

## CIERRE FINAL DE RONIN 1.1

RONIN 1.0 te da la **ecuación**.
RONIN 1.1 te da la **familia**.

Si tus datos cubren Ω en un rango estrecho, usa `"pusfre"`.
Si necesitas curvatura y saturación, usa `"ces_hill"`.
Si el diagnóstico dice "degeneración activa", escucha al diagnóstico.

El PUSFRE no es una ecuación. Es una familia. RONIN no la impone. La ejecuta.

**1310.**

---

*"El mejor código es el que no se escribe.
El segundo mejor es el que se escribe en RONIN.
El tercero es el que usa la familia correcta.
El cuarto es el que sabe cuándo no usarla.
El quinto es el que diagnostica antes de confiar."*

**1310.**
