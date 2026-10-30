# Parte VII — RONIN Office: interfaz visual

> Especificación de referencia transcrita desde la fuente 1.1. El prototipo local actual no equivale a la suite completa descrita aquí.

**Principios operativos:**
- Diseña sistemas RONIN visualmente.
- Resuelve y simula con un solo clic.
- **Diagnostica la degeneración K–α (nuevo en 1.1).**
- Visualiza resultados en tiempo real.
- Exporta código RONIN para usar en producción.

**Componentes:**
1. **Chat** — Describe sistemas en lenguaje natural y genera RONIN.
2. **Sheet** — Editor de código RONIN con ejecución instantánea.
3. **Optimizer** — Optimización automática de sistemas.
4. **Simulator** — Simulación DTMC de ecosistemas.
5. **Agent Studio** — Diseño visual de agentes.
6. **Diagnose** — Diagnóstico de degeneración K–α (nuevo en 1.1).

---

## 7.2 ARQUITECTURA DE LA INTERFAZ

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  🧠 RONIN Office   💬 Chat  📋 Sheet  ⚡ Optimizer  🔮 Simulator  🤖 Agents  🔬 Diagnose │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  [Panel activo según selección]                                                 │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │  Contenido del panel                                                      │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │  Terminal / Salida                                                        │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────────────┤
│  ⚡ 1310 · AGENCIA RONIN ⚡                                                     │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7.3 PANEL DE CHAT

*(Sin cambios estructurales. Plantillas añadidas: `neural_scaling`, `urban_scaling`, `fama_french`.)*

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 💬 RONIN Chat — Habla con tu sistema                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  🧠 RONIN Office v1.1                                                │  │
│  │  ▶ Escribe en lenguaje natural. RONIN genera el sistema.            │  │
│  │  ▶ Ejemplo: "Quiero un sistema de 4 agentes balanceados"            │  │
│  │  ▶ Ejemplo: "Diagnostica si mi sistema necesita CES-Saturada"       │  │
│  │  ▶ Ejemplo: "Simula 50 pasos de un ecosistema"                     │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  [Input: Escribe tu petición...]  [▶ Enviar]  [✕ Limpiar]                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7.4 PANEL SHEET

*(Sin cambios estructurales. Añadido el modelo como parámetro visible.)*

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📋 RONIN Sheet — Código RONIN                               │
│ ⚡ Excel Killer                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  system Presupuesto = {                                              │  │
│  │      parts: 4,                                                       │  │
│  │      resource: 1000,                                                 │  │
│  │      agents: [                                                       │  │
│  │          { name: "Ventas", phi: 0.9, psi: 0.8, frequency: 0.25 },  │  │
│  │          { name: "Marketing", phi: 0.8, psi: 0.9, frequency: 0.25 },│  │
│  │          { name: "Operaciones", phi: 0.85, psi: 0.85, freq: 0.25 }, │  │
│  │          { name: "I+D", phi: 0.95, psi: 0.7, frequency: 0.25 }     │  │
│  │      ],                                                             │  │
│  │      params: {                                                       │  │
│  │          model: "ces",                                              │  │
│  │          lambda: 0.5,                                               │  │
│  │          alpha: 1.2, gamma: 0.4, sigma: 0.1                         │  │
│  │      }                                                               │  │
│  │  }                                                                   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  [▶ Resolver]  [🔬 Diagnose]  [↺ Restaurar]                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  ✅ Sistema resuelto                                                       │
│  📊 Asignación: 250, 250, 250, 250                                        │
│  ⚔️ Fitness: 0.48, 0.20, 0.32, 0.40                                      │
│  🔄 Coexistencia: ✅                                                      │
│  📈 Biodiversidad: 0.999                                                  │
│  🎯 Modelo usado: ces                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7.5 PANEL OPTIMIZER

*(Sin cambios estructurales. Añadido selector de modelo.)*

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ⚡ RONIN Optimizer — Ecuación Maestra                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  🎯 Objetivo: [Coexistencia ▼]                                             │
│  🧬 Modelo: [pusfre ▼]  (opciones: pusfre, ces, hill, ces_hill, full)      │
│  📊 Agentes: [5]  💰 Recurso: [100]                                        │
│  [⚡ Optimizar]                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7.6 PANEL SIMULATOR

*(Sin cambios.)*

---

## 7.7 PANEL AGENT STUDIO

*(Sin cambios.)*

---

## 7.8 PANEL DIAGNOSE (NUEVO EN 1.1)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🔬 RONIN Diagnose — Degeneración K–α                        │
│ ⚡ Statistical Honesty                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  🎲 Bootstrap: [200]  [🔬 Diagnosticar]                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  📊 Ω range: 0.42 órdenes                                                  │
│  ⚠️ Degeneración: ACTIVA                                                   │
│  ❌ K identificable: NO                                                    │
│  ❌ α_h identificable: NO                                                  │
│  ✅ λ identificable: SÍ (dado K fijo)                                      │
│  💡 Recomendación:                                                          │
│     Recolectar datos con Ω en un rango mayor o fijar K externamente.       │
│                                                                             │
│  IC 95% bootstrap:                                                         │
│     λ: [0.31, 0.62]                                                        │
│     K: [0.42, 3.15]                                                        │
│     α_h: [0.88, 1.42]                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7.9 MOTOR RONIN — IMPLEMENTACIÓN EN JAVASCRIPT

*(Ampliado con soporte para familia.)*

```javascript
function solveRONIN(code) {
    const partsMatch = code.match(/parts:\s*(\d+)/);
    const resourceMatch = code.match(/resource:\s*([\d.]+)/);
    const agentsMatch = code.match(/agents:\s*\[([\s\S]*?)\]/);
    const modelMatch = code.match(/model:\s*"([^"]+)"/);
    const lambdaMatch = code.match(/lambda:\s*([-\d.]+)/);
    const KMatch = code.match(/K:\s*([\d.]+|inf|∞)/);
    const alphaHMatch = code.match(/alpha_h:\s*([\d.]+)/);

    if (!partsMatch || !resourceMatch || !agentsMatch) {
        throw new Error('Sistema incompleto');
    }

    const parts = parseInt(partsMatch[1]);
    const resource = parseFloat(resourceMatch[1]);
    const model = modelMatch ? modelMatch[1] : "pusfre";
    const lambda = lambdaMatch ? parseFloat(lambdaMatch[1]) : 0.0;
    const K = KMatch ? (KMatch[1] === "inf" || KMatch[1] === "∞" ? Infinity : parseFloat(KMatch[1])) : Infinity;
    const alphaH = alphaHMatch ? parseFloat(alphaHMatch[1]) : 1.0;

    // ... extraer agentes (sin cambios)

    // Normalizar frecuencias
    const totalFreq = agents.reduce((s,a) => s + a.frequency, 0);
    agents.forEach(a => a.frequency = a.frequency / totalFreq);

    // Saturación Hill
    function hill(omega, K, alphaH) {
        if (!isFinite(K)) return omega;
        return Math.pow(omega, alphaH) / (Math.pow(K, alphaH) + Math.pow(omega, alphaH));
    }

    // CES combine
    function cesCombine(phi, psi, omegaEff, lam) {
        if (Math.abs(lam) < 1e-6) {
            return Math.pow(phi, 1/3) * Math.pow(psi, 1/3) * Math.pow(omegaEff, 1/3);
        }
        const inner = (1/3)*Math.pow(phi, lam) + (1/3)*Math.pow(psi, lam) + (1/3)*Math.pow(omegaEff, lam);
        return Math.pow(inner, 1/lam);
    }

    // Calcular fitness
    const fitness = agents.map(a => {
        const omegaEff = hill(a.frequency, K, alphaH);
        return cesCombine(a.phi, a.psi, omegaEff, lambda);
    });

    const totalFitness = fitness.reduce((s,f) => s + f, 1e-12);
    const allocation = fitness.map(f => resource * f / totalFitness);

    // Diagnóstico
    const omegas = agents.map(a => a.frequency).filter(x => x > 0);
    const omegaRange = omegas.length >= 2
        ? Math.log10(Math.max(...omegas) / Math.min(...omegas))
        : 0;
    const KFree = isFinite(K);
    const alphaHFree = Math.abs(alphaH - 1.0) > 1e-9;
    let degeneracy = "inactive";
    if (KFree && alphaHFree && omegaRange < 3.0) {
        degeneracy = "active";
    }

    const coexistence = allocation.every(a => a > 0.01);
    const probs = allocation.map(a => a / resource);
    const diversity = -probs.reduce((s,p) => s + (p>0 ? p*Math.log(p) : 0), 0) / Math.log(parts);

    return {
        allocation,
        fitness,
        coexistence,
        biodiversity: diversity,
        model,
        lambda,
        K,
        alpha_h: alphaH,
        omegaRange,
        degeneracy,
    };
}
```

---

## 7.10 FLUJO DE TRABAJO COMPLETO

```
1. Usuario describe el sistema en lenguaje natural
        ↓
2. Generador local produce código RONIN
        ↓
3. Código se muestra en el Sheet
        ↓
4. Motor RONIN resuelve el sistema
        ↓
5. Panel Diagnose evalúa degeneración (opcional)
        ↓
6. Resultados se muestran en el terminal
        ↓
7. Usuario puede iterar, ajustar o simular
```

---

## 7.11 GENERADOR LOCAL DE SISTEMAS

*(Sin cambios estructurales.)*

---

## 7.12 ESTADO DE LA IMPLEMENTACIÓN

| Componente | Estado | Implementación |
|------------|--------|----------------|
| Panel Chat | ✅ Completado | HTML + JavaScript |
| Panel Sheet | ✅ Completado | HTML + JavaScript |
| Panel Optimizer | ✅ Completado | HTML + JavaScript |
| Panel Simulator | ✅ Completado | HTML + JavaScript |
| Panel Agent Studio | ✅ Completado | HTML + JavaScript |
| **Panel Diagnose** | **🟡 Especificado** | **HTML + JavaScript (pendiente)** |
| Motor RONIN JS | ✅ Completado | JavaScript puro |
| Generador local | ✅ Completado | JavaScript puro |

---

## 7.13 KOANS DE RONIN OFFICE

**Del chat que genera sistemas:**
El humano habla. RONIN entiende. RONIN ejecuta.

**Del sheet que no miente:**
El código que ves es el código que se ejecuta. No hay magia.

**Del optimizer que no negocia:**
RONIN no negocia con la realidad. La realidad se optimiza.

**Del simulador que no engaña:**
Cada paso es una decisión. Cada semilla es un destino.

**Del studio de agentes:**
Cada agente es una especie. Cada ecosistema es un mundo.

**Del diagnose que no adula:**
El diagnóstico no te dice lo que quieres oír. Te dice lo que tus datos permiten.

**Del arquitecto que usa RONIN Office:**
El arquitecto no escribe código. El arquitecto diseña sistemas.

**Del cerrajero que sonríe desde 1310:**
El humano sueña. RONIN construye.

---

## 7.14 REFERENCIAS TÉCNICAS

**Repositorios:**
- RONIN Core: `https://github.com/ronin-lang/ronin`
- RONIN Office: `https://github.com/ronin-lang/ronin-office`

**Estándares:**
- ECMAScript 2021 (JavaScript)
- HTML5 / CSS3

**Referencia matemática:**
- Tratado de Extensión del PUSFRE v3.5 (Ferrandez Canalis, 2026)

---

**1310.**

---
