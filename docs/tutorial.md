# PARTE I — TUTORIAL PARA MORTALES

## CAPÍTULO 1: QUÉ ES UN SISTEMA

### 1.1 Un sistema es cualquier cosa que tiene:

- **Partes**: varias entidades que compiten por algo.
- **Un recurso**: algo escaso que las partes quieren.
- **Un problema**: no sabes cómo repartirlo de forma justa.

**Ejemplos:**

- 5 flotas pesqueras (partes) y 10.000 toneladas de pescado (recurso).
- 20 activos financieros (partes) y 100 millones de euros (recurso).
- 100 semáforos (partes) y 120 segundos de ciclo (recurso).
- 50 regiones (partes) y 10.000 camas UCI (recurso).
- **10 clases de un juego RPG (partes) y 100 puntos de balance (recurso).**
- **8 microservicios (partes) y 1000 peticiones por segundo (recurso).**
- **1000 ciudades (partes) y presupuesto de infraestructura (recurso).**
- **46 modelos de lenguaje (partes) y cómputo total (recurso).**

### 1.2 Qué necesitas saber de cada parte

Solo tres números por cada parte:

- **Φ (phi)**: capacidad para usar el recurso (0..1).
- **Ψ (psi)**: consistencia, cuánto "debe" o "falla" (0..1).
- **Ω (omega)**: frecuencia inicial, cuánto se usa ahora (0..1). **La suma de todas las frecuencias debe ser 1.**

**Nuevo en 1.1:** Opcionalmente puedes especificar cómo se combinan estos tres números. Por defecto se multiplican (PUSFRE clásico), pero puedes elegir otras formas (CES, Hill, CES-Saturada).

### 1.3 La pregunta correcta

Antes de resolver, pregúntate: **¿mis datos cubren un rango amplio de Ω?**

Si tu Ω cubre menos de 3 órdenes de magnitud, usa `model: "pusfre"` (el default).
Si tu Ω cubre 3+ órdenes, prueba `model: "ces_hill"` y ejecuta `diagnose`.
Si tu Ω cubre 5+ órdenes, la familia CES-Saturada es completamente identificable.

---

## CAPÍTULO 2: TU PRIMER SISTEMA

### 2.1 El problema

2 máquinas: A y B. 100 horas de trabajo.
A: phi=0.8, psi=1.0, freq=0.6
B: phi=0.5, psi=1.0, freq=0.4

**Pregunta:** ¿cuántas horas recibe cada una?

### 2.2 El código (compatibilidad 1.0)

```ronin
system Maquinas = {
    parts: 2,
    resource: 100,
    agents: [
        { phi: 0.8, psi: 1.0, frequency: 0.6 },
        { phi: 0.5, psi: 1.0, frequency: 0.4 }
    ],
    params: {
        alpha: 1.0,
        gamma: 0.4,
        sigma: 0.1
    }
}

result = solve Maquinas
print(result.allocation)  // [70.588235, 29.411765]
print(result.model_used)  // "pusfre"
print(result.omega_range) // 0.18 órdenes de magnitud
```

### 2.3 El mismo problema con familia (nuevo en 1.1)

```ronin
system MaquinasCES = {
    parts: 2,
    resource: 100,
    agents: [
        { phi: 0.8, psi: 1.0, frequency: 0.6 },
        { phi: 0.5, psi: 1.0, frequency: 0.4 }
    ],
    params: {
        model: "ces",
        lambda: 0.5,
        alpha: 1.0,
        gamma: 0.4,
        sigma: 0.1
    }
}

result = solve MaquinasCES
print(result.model_used)  // "ces"
print(result.lambda_used) // 0.5
```

**Nota:** Con `lambda = 0.5` y dos agentes, el resultado difiere del PUSFRE clásico. La familia da más peso a los agentes con valores altos.

---

## CAPÍTULO 3: QUÉ SIGNIFICA CADA COSA

### 3.1 `phi` — Capacidad
- `phi = 0.9` → muy eficiente
- `phi = 0.3` → poco eficiente

### 3.2 `psi` — Consistencia
- `psi = 0.95` → casi sin deuda
- `psi = 0.5` → mucha deuda

### 3.3 `frequency` — Frecuencia
- `0.6` → se usa el 60% del tiempo
- **La suma de todas las frecuencias debe ser 1.**

### 3.4 `alpha` — Competencia
- `1.0` → competencia lineal (normal)
- `> 1.0` → winner-takes-all
- `< 1.0` → más biodiversidad

### 3.5 `gamma` — Penalización por deuda
- `0.0` → la deuda no importa
- `0.5` → la deuda importa mucho

### 3.6 `sigma` — Ruido
- `0.0` → determinista
- `0.2` → variabilidad alta

### 3.7 `model` — Modelo de la familia (nuevo en 1.1)
- `"pusfre"` → PUSFRE clásico (default, compatibilidad total)
- `"ces"` → Curvatura CES sin saturación
- `"hill"` → Saturación Hill sin curvatura
- `"ces_hill"` → M6: curvatura + saturación
- `"full"` → Con memoria temporal

### 3.8 `lambda` — Curvatura CES (nuevo en 1.1)
- `0` → log-lineal (PUSFRE)
- `-1` → Leontief (complementos perfectos)
- `1` → lineal (suma ponderada)
- `0.5` → curvatura moderada
- `2` → compensación fuerte

### 3.9 `K` — Constante de saturación Hill (nuevo en 1.1)
- `∞` → sin saturación (PUSFRE/CES)
- `0.5` → saturación a partir de Ω ≈ 0.5
- `1.0` → saturación a partir de Ω ≈ 1.0
- `10` → saturación tardía

### 3.10 `alpha_h` — Exponente Hill (nuevo en 1.1)
- `1.0` → saturación suave
- `1.5` → saturación pronunciada
- `2.0` → saturación muy abrupta

---

## CAPÍTULO 4: EJEMPLOS PROGRESIVOS

### 4.1 Dos partes (fácil)

```ronin
system DosPartes = {
    parts: 2,
    resource: 100,
    agents: [
        { phi: 0.9, psi: 0.9, frequency: 0.5 },
        { phi: 0.5, psi: 0.5, frequency: 0.5 }
    ],
    params: { alpha: 1.0, gamma: 0.3, sigma: 0.1 }
}
result = solve DosPartes  // [~76.415, ~23.585]
```

### 4.2 Tres partes

```ronin
system TresPartes = {
    parts: 3,
    resource: 1000,
    agents: [
        { phi: 0.9, psi: 0.9, frequency: 0.4 },
        { phi: 0.7, psi: 0.8, frequency: 0.35 },
        { phi: 0.4, psi: 0.9, frequency: 0.25 }
    ],
    params: { alpha: 1.2, gamma: 0.4, sigma: 0.15 }
}
result = solve TresPartes  // [~542.932, ~319.785, ~137.284]
```

### 4.3 Cinco partes (pesca)

```ronin
system Pesca = {
    parts: 5,
    resource: 10000,
    agents: [
        { phi: 0.95, psi: 0.68, frequency: 0.267 },
        { phi: 0.85, psi: 0.76, frequency: 0.238 },
        { phi: 0.60, psi: 0.92, frequency: 0.160 },
        { phi: 0.45, psi: 0.96, frequency: 0.131 },
        { phi: 0.70, psi: 0.84, frequency: 0.204 }
    ],
    params: { alpha: 1.3, gamma: 0.4, sigma: 0.15 }
}
result = solve Pesca  // [3138.305, 2702.592, 1378.139, 831.638, 1949.325]
```

### 4.4 Con auditoría de deuda

```ronin
audit = audit Pesca with {
    epsilon: 0.05,
    delta: 0.01,
    stratified: true
}
print(audit.estimated_debt)  // 0.034 ± 0.012 (99% CI)
```

### 4.5 Con simulación DTMC

```ronin
sim = simulate Pesca with {
    steps: 100,
    dtmc: true,
    stochastic: true
}
plot sim
```

### 4.6 Con CES explícito (nuevo en 1.1)

```ronin
system PescaCES = {
    parts: 5,
    resource: 10000,
    agents: [
        { phi: 0.95, psi: 0.68, frequency: 0.267 },
        { phi: 0.85, psi: 0.76, frequency: 0.238 },
        { phi: 0.60, psi: 0.92, frequency: 0.160 },
        { phi: 0.45, psi: 0.96, frequency: 0.131 },
        { phi: 0.70, psi: 0.84, frequency: 0.204 }
    ],
    params: {
        model: "ces",
        lambda: 0.5,
        alpha: 1.3,
        gamma: 0.4,
        sigma: 0.15
    }
}
result = solve PescaCES
print(result.model_used)  // "ces"
print(result.lambda_used) // 0.5
```

### 4.7 Con CES-Saturada (M6, nuevo en 1.1)

```ronin
system PescaFull = {
    parts: 5,
    resource: 10000,
    agents: [
        { phi: 0.95, psi: 0.68, frequency: 0.267 },
        { phi: 0.85, psi: 0.76, frequency: 0.238 },
        { phi: 0.60, psi: 0.92, frequency: 0.160 },
        { phi: 0.45, psi: 0.96, frequency: 0.131 },
        { phi: 0.70, psi: 0.84, frequency: 0.204 }
    ],
    params: {
        model: "ces_hill",
        lambda: 0.5,
        K: 0.5,
        alpha_h: 1.5,
        alpha: 1.3,
        gamma: 0.4,
        sigma: 0.15,
        degeneracy_check: true,
        omega_range_report: true
    }
}
result = solve PescaFull
print(result.degeneracy)  // "active" (Ω cubre solo 0.2 órdenes)
print(result.warnings)    // ["K–α_h degeneracy active..."]
```

---

## CAPÍTULO 5: LA FAMILIA CES-SATURADA

### 5.1 La idea en una frase

El PUSFRE clásico dice: `F_i = Φ_i · Ψ_i · Ω_i^α`.

La familia CES-Saturada dice: **los tres factores no tienen por qué combinarse multiplicativamente, y Ω puede saturarse.**

### 5.2 Los cinco modelos

| `model` | Qué hace diferente | Cuándo usarlo |
|---------|-------------------|---------------|
| `"pusfre"` | Nada (default) | Datos log-lineales, Ω estrecho |
| `"ces"` | Curvatura en la combinación de Φ, Ψ, Ω | Factores no separables |
| `"hill"` | Saturación en Ω | Ω amplio con rendimientos decrecientes |
| `"ces_hill"` | Curvatura + saturación | Estructura multiplicativa + saturación visible |
| `"full"` | + memoria temporal | Sistemas con dependencia temporal |

### 5.3 El caso real: Neural Scaling

Los datos de Hoffmann et al. (2022) sobre cómputo óptimo en entrenamiento de LLMs cubren Ω ~ 3 órdenes de magnitud. La familia CES-Saturada detecta saturación donde el PUSFRE clásico falla.

```ronin
system NeuralScaling = {
    parts: 46,
    resource: 1.0,
    agents: [ /* 46 modelos con log N, log D, log C */ ],
    params: {
        model: "ces_hill",
        lambda: 0.5,
        K: 1.0,
        alpha_h: 1.5,
        degeneracy_check: true,
        omega_range_report: true
    }
}
result = solve NeuralScaling
print(result.degeneracy)      // "inactive"
print(result.omega_range)     // 3.0
```

### 5.4 El caso real: Fama-French

Los datos del modelo de tres factores de Fama-French tienen Ω ~ 0.5 órdenes de magnitud. La familia CES-Saturada **no mejora** al modelo lineal clásico.

```ronin
system FamaFrench = {
    parts: 720,
    resource: 1.0,
    agents: [ /* retornos mensuales */ ],
    params: {
        model: "pusfre",  // la elección correcta aquí
        alpha: 1.0,
        gamma: 0.3,
        sigma: 0.2
    }
}
```

**Lección:** No todos los dominios se benefician de la familia. La familia es útil cuando la estructura es multiplicativa y la saturación es visible.

---

## CAPÍTULO 6: DIAGNÓSTICO DE DEGENERACIÓN

### 6.1 Por qué necesitas `diagnose`

La familia CES-Saturada tiene un problema: **K y α_h son indistinguibles si tu Ω cubre un rango estrecho**. Esto se llama **degeneración K–α**.

El comando `diagnose` te lo dice.

### 6.2 Cómo usarlo

```ronin
diagnose PescaFull with {
    omega_range: true,
    degeneracy: true,
    bootstrap: 200
}
```

### 6.3 La salida

```json
{
  "omega_range_orders": 0.42,
  "degeneracy": "active",
  "K_identifiable": false,
  "alpha_h_identifiable": false,
  "recommendation": "Ω cubre < 1 orden de magnitud. K y α_h son indistinguibles. Recolectar datos con Ω en un rango mayor o fijar K externamente."
}
```

### 6.4 Qué hacer con la respuesta

**Si `degeneracy: "active"`:**
- No uses `model: "ces_hill"` con K y α_h libres.
- Fija K a un valor conocido o usa `model: "pusfre"`.
- Si necesitas la familia, recolecta datos con Ω más amplio.

**Si `degeneracy: "inactive"`:**
- Tu Ω cubre ≥ 3 órdenes.
- K y α_h son identificables.
- Usa la familia con confianza.

### 6.5 Ejemplo numérico

| Ω range | degeneracy | K identificable | alpha_h identificable |
|---------|------------|-----------------|----------------------|
| 0.42 órdenes | active | ❌ | ❌ |
| 1.5 órdenes | active | ❌ | ❌ |
| 3.0 órdenes | inactive | ✅ | ✅ |
| 5.0 órdenes | inactive | ✅ | ✅ |

---

## CAPÍTULO 7: ERRORES COMUNES

### 7.1 Frecuencias que no suman 1

```ronin
agents: [
    { phi: 0.8, psi: 1.0, frequency: 0.6 },
    { phi: 0.5, psi: 1.0, frequency: 0.5 }   // ❌ 0.6+0.5=1.1
]
```
**Error:** `Error: Las frecuencias deben sumar 1 (suma actual: 1.1)`

### 7.2 `phi` fuera de rango

```ronin
{ phi: 1.5, psi: 1.0, frequency: 0.5 }  // ❌
```
**Error:** `Error: phi debe estar entre 0 y 1 (valor actual: 1.5)`

### 7.3 `alpha` fuera de rango

```ronin
params: { alpha: 3.0, gamma: 0.4, sigma: 0.1 }  // ❌
```
**Error:** `Error: alpha debe estar entre 0.5 y 2.5 (valor actual: 3.0)`

### 7.4 Menos de 2 partes

```ronin
parts: 1  // ❌
```
**Error:** `Error: Un sistema debe tener al menos 2 partes.`

### 7.5 Incoherencia de modelo (nuevo en 1.1)

```ronin
params: { model: "pusfre", lambda: 0.5 }  // ❌
```
**Error:** `Error: model "pusfre" requiere lambda = 0`

```ronin
params: { model: "ces", K: 0.5 }  // ❌
```
**Error:** `Error: model "ces" requiere K = ∞`

```ronin
params: { model: "hill", lambda: 0.5 }  // ❌
```
**Error:** `Error: model "hill" requiere lambda = 0`

### 7.6 Coexistencia imposible

```ronin
system Imposible = {
    parts: 5,
    resource: 1,
    agents: [
        { phi: 0.99, psi: 0.99, frequency: 0.5 },
        { phi: 0.01, psi: 0.01, frequency: 0.5 }
    ],
    params: { alpha: 2.5, gamma: 0.9, sigma: 0.0 }
}
```
**Advertencia normativa:** `Warning: k_min (5313.81) > k_actual (1.0). La coexistencia no es posible.`

### 7.7 Degeneración no diagnosticada (nuevo en 1.1)

Si usas `model: "ces_hill"` con Ω estrecho y no activas `degeneracy_check`, el runtime no te avisa. Los parámetros K y α_h serán inidentificables pero el sistema te dará una solución.

**Buena práctica:** Activa siempre `degeneracy_check: true` cuando uses la familia.

---

## CAPÍTULO 8: REFERENCIA RÁPIDA

### 8.1 Estructura básica

```ronin
system Nombre = {
    parts: N,
    resource: R,
    agents: [
        { phi: ..., psi: ..., frequency: ... },
        ...
    ],
    params: {
        // Núcleo 1.0
        alpha: ..., gamma: ..., sigma: ...,
        // Extensión 1.1
        model: "...", lambda: ..., K: ..., alpha_h: ...,
        memory_order: ..., degeneracy_check: ...
    }
}
```

### 8.2 Parámetros recomendados por dominio

| Dominio | model | lambda | K | alpha_h | alpha | gamma | sigma |
|---------|-------|--------|---|---------|-------|-------|-------|
| Logística | pusfre | 0 | ∞ | 1.0 | 1.2 | 0.35 | 0.12 |
| Finanzas | ces | 0.5 | ∞ | 1.0 | 1.0 | 0.30 | 0.20 |
| Energía | ces_hill | 0.4 | 0.8 | 1.3 | 1.3 | 0.50 | 0.10 |
| Salud | pusfre | 0 | ∞ | 1.0 | 1.1 | 0.40 | 0.15 |
| Ciberseguridad | ces | 0.3 | ∞ | 1.0 | 1.2 | 0.50 | 0.12 |
| Telecom | ces | 0.5 | ∞ | 1.0 | 1.2 | 0.40 | 0.15 |
| Agricultura | pusfre | 0 | ∞ | 1.0 | 1.0 | 0.30 | 0.20 |
| Retail | ces | 0.4 | ∞ | 1.0 | 1.1 | 0.40 | 0.15 |
| Manufactura | ces_hill | 0.5 | 1.0 | 1.5 | 1.2 | 0.30 | 0.10 |
| Videojuegos | ces | 0.6 | ∞ | 1.0 | 1.1 | 0.35 | 0.10 |
| Web | ces | 0.4 | ∞ | 1.0 | 1.2 | 0.30 | 0.15 |
| IoT | pusfre | 0 | ∞ | 1.0 | 1.0 | 0.40 | 0.08 |
| Neural Scaling | ces_hill | 0.5 | 1.0 | 1.5 | 1.3 | 0.4 | 0.15 |
| **Fama-French** | **pusfre** | **0** | **∞** | **1.0** | **1.0** | **0.3** | **0.2** |
| Urban Scaling | ces_hill | 0.5 | 1.0 | 1.4 | 1.1 | 0.4 | 0.15 |

### 8.3 Comandos básicos

| Comando | Función |
|---------|---------|
| `solve Nombre` | Resuelve el sistema |
| `simulate Nombre with { ... }` | Simula |
| `audit Nombre with { ... }` | Audita la deuda |
| **`diagnose Nombre with { ... }`** | **Diagnóstico de degeneración (nuevo)** |
| `plot Nombre` | Visualiza |
| `print(result)` | Muestra el resultado |

### 8.4 Opciones comunes

| Opción | Valores | Defecto |
|--------|---------|---------|
| `steps` | entero > 0 | 100 |
| `dtmc` | true/false | true |
| `stochastic` | true/false | true |
| `parallel` | true/false | false |
| `threads` | entero > 0 | 8 |
| `epsilon` | 0.01 - 0.2 | 0.05 |
| `delta` | 0.01 - 0.1 | 0.01 |
| `stratified` | true/false | true |
| `bootstrap` | entero ≥ 0 | 0 |
| `degeneracy_check` | true/false | false |
| `omega_range_report` | true/false | false |

---

## CAPÍTULO 9: KOANS DEL TUTORIAL

**Del que no sabe nada:** El que no sabe nada es el que más puede aprender.

**De la línea que resuelve todo:** Una línea de RONIN puede reemplazar 200 líneas de Python.

**Del error que no ocurre:** La arquitectura del compilador de RONIN no te deja equivocarte.

**Del torpe que resuelve:** No hace falta saber matemáticas para usar RONIN.

**Del miedo que desaparece:** El primer sistema da miedo. El décimo da risa.

**De la familia:** No busques la ecuación única. Busca la familia que la contiene.

**De la degeneración:** Dos parámetros que no puedes distinguir no son dos parámetros. Son uno disfrazado.

**Del diagnóstico:** El sistema que te dice cuándo no puedes confiar en él vale más que el que te dice que todo está bien.

**De la honestidad:** El PUSFRE no es una ecuación. Es una familia. RONIN no la impone. La ejecuta.

---
