# APÉNDICE FAMILIA CES-SATURADA

## A.1 DEFINICIÓN MATEMÁTICA

### A.1.1 La familia

La familia CES-Saturada se define como:

$$F_i = \left( w_1 \Phi_i^\lambda + w_2 \Psi_i^\lambda + w_3 \left[\Omega_i^{\text{sat}}\right]^\lambda \right)^{1/\lambda} \cdot \varepsilon_i$$

donde:

$$\Omega_i^{\text{sat}} = \frac{\Omega_i^{\alpha_h}}{K^{\alpha_h} + \Omega_i^{\alpha_h}}$$

**Parámetros:**
- `lambda ∈ [-1, 2], ≠ 0`: curvatura del agregador.
- `K > 0`: constante de saturación Hill.
- `alpha_h > 0`: exponente Hill.
- `w_1, w_2, w_3 ∈ [0.1, 0.8], Σw = 1`: pesos del agregador.

### A.1.2 Casos degenerados

| `model` | λ | K | k | Resultado |
|---------|---|---|---|-----------|
| `"pusfre"` | 0 | ∞ | 1 | `Φ · Ψ · Ω^α` |
| `"ces"` | libre ≠ 0 | ∞ | 1 | CES sin saturación |
| `"hill"` | 0 | libre | 1 | PUSFRE con Ω saturado |
| `"ces_hill"` | libre ≠ 0 | libre | 1 | M6: curvatura + saturación |
| `"full"` | libre ≠ 0 | libre | ≥ 1 | + memoria temporal |

---

## A.2 CASOS LÍMITE CON VERIFICACIÓN

### A.2.1 Verificación numérica

| Caso | Parámetros | Valor analítico | Valor numérico | Error relativo |
|------|-----------|-----------------|----------------|----------------|
| A (PUSFRE base) | λ=1e-6, K=1e6 | 1.0 | 1.000000 | < 1e-9 |
| B (Hill) | λ=1e-6, K=1.5, α_h=1.0 | 0.2105 | 0.21053 | 1.5e-5 |
| C (Lineal) | λ=1 | 1.0 | 1.000000 | < 1e-9 |
| D (Leontief) | λ=-10 | 1.0 | 0.99998 | 2e-5 |
| E (CES estándar) | λ=0.5 | 1.0 | 1.000000 | < 1e-9 |
| F (Compensatorio) | λ=1.5 | 1.0 | 1.000000 | < 1e-9 |

### A.2.2 Interpretación de σ

**Advertencia formal.** En el PUSFRE extendido, `σ = 1/(1-λ)` describe exclusivamente la curvatura del agregador. **No posee interpretación económica de elasticidad de sustitución.** Cualquier inferencia sobre sustituibilidad de atributos basada en σ es inválida en este marco.

---

## A.3 DEGENERACIÓN K–α

### A.3.1 Proposición 5.1 (demostración)

**Enunciado:** Sean $K_1, K_2 > 0$ y $\alpha_1, \alpha_2 > 0$. Si $\Omega \ll \min(K_1, K_2)$, entonces la función Hill satisface:

$$\frac{\Omega^{\alpha_1}}{K_1^{\alpha_1} + \Omega^{\alpha_1}} \approx \frac{\Omega^{\alpha_2}}{K_2^{\alpha_2} + \Omega^{\alpha_2}}$$

siempre que:

$$\alpha_1 \log \Omega - \alpha_1 \log K_1 = \alpha_2 \log \Omega - \alpha_2 \log K_2.$$

**Demostración.** Si $\Omega \ll K$, entonces $\Omega^\alpha/K^\alpha \ll 1$ y

$$\text{Hill}(\Omega; K, \alpha) = \frac{\Omega^\alpha}{K^\alpha + \Omega^\alpha} \approx \frac{\Omega^\alpha}{K^\alpha} = \Omega^\alpha \cdot K^{-\alpha}.$$

Tomando logaritmos:

$$\log \text{Hill} \approx \alpha \log \Omega - \alpha \log K.$$

Definiendo $\beta = -\alpha \log K$, la expresión es $\alpha \log \Omega + \beta$, que depende solo de $(\alpha, \beta)$ y no de $(\alpha, K)$ por separado. Cualquier par $(\alpha, K)$ que produzca el mismo $\beta$ da la misma Hill en el régimen $\Omega \ll K$. $\square$

### A.3.2 Corolarios

**Corolario 5.1.1.** Más N no rompe la degeneración.

**Corolario 5.1.2.** La degeneración se rompe solo cuando $\Omega \approx K$ es observable. Requiere que $\Omega/K$ varíe al menos entre 0.1 y 10.

**Corolario 5.1.3 (rompimiento).** Si $\Omega$ cubre un rango donde $\Omega/K$ varía entre $\epsilon$ y $1/\epsilon$, entonces la curvatura Hill es visible y $K$ se separa de $\alpha_h$.

### A.3.3 Aplicación en RONIN

```ronin
diagnose MiSistema with { degeneracy: true }

// Si omega_range_orders < 3:
//   degeneracy = "active"
//   K y α_h NO identificables
// Si omega_range_orders >= 3:
//   degeneracy = "inactive"
//   K y α_h identificables
```

---

## A.4 GUÍA DE USO POR DOMINIO

| Dominio | Ω range | model recomendado | Justificación |
|---------|---------|-------------------|---------------|
| Logística | 1 orden | `"pusfre"` | Estructura multiplicativa simple |
| Finanzas | 0.5-1 orden | `"pusfre"` | Aditivo, Ω estrecho |
| Neural Scaling | 3 órdenes | `"ces_hill"` | Multiplicativo + saturación visible |
| Urban Scaling | 5+ órdenes | `"ces_hill"` | Multiplicativo + Ω amplio |
| Species-Area | 6+ órdenes | `"ces_hill"` | Multiplicativo + Ω amplio |
| Fama-French | <1 orden | `"pusfre"` | Aditivo, Ω estrecho |
| RAG | 1-2 órdenes | `"ces"` | Curvatura sin saturación |

---

## A.5 REFERENCIAS AL TRATADO

El desarrollo completo de la familia CES-Saturada, con demostraciones analíticas, validación cruzada en dos dominios (Neural Scaling positivo, Fama-French negativo), y análisis de degeneración, está en:

**Tratado de Extensión del PUSFRE v3.5** — Ferrandez Canalis, D. (2026).

Contribuciones principales:
1. Demostración analítica de la degeneración K–α (Proposición 5.1).
2. Caracterización axiomática del PUSFRE como caso límite.
3. Validación externa en Neural Scaling (ΔBIC = -14.3).
4. Validación externa negativa en Fama-French (ΔBIC = +8.7).
5. Desarrollo formal de GSE (Apéndice G).
6. Test con Ω cubriendo 5+ órdenes (Apéndice I).

**Implicación operativa:** El reporte de parámetros debe incluir siempre el rango de Ω. Si Ω cubre < 3 órdenes, K y α_h no son interpretables individualmente. Si cubre > 5, sí lo son.

---

*Fin del Apéndice Familia CES-Saturada.*

**1310.**

*"La universalidad no está en el punto. Está en la familia.
Pero la familia, a veces, tampoco es identificable.
Y cuando no lo es, conviene decirlo — con demostración analítica,
con verificación numérica, con validación externa contrastada,
y con delimitación explícita del caso de uso."*

**1310.**

---
