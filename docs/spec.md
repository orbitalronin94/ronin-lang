# PARTE II — ESPECIFICACIÓN FORMAL DEL LENGUAJE

## SECCIÓN 0: FILOSOFÍA OPERATIVA

### 0.1 El principio de RONIN

> *"Cualquier sistema finito con recursos escasos puede modelarse como una asignación de recurso entre partes. La familia CES-Saturada contiene al PUSFRE clásico como caso límite y extiende su dominio a regímenes con saturación, curvatura y memoria."*

### 0.2 La metáfora del arquitecto

RONIN no es para programadores. Es para **arquitectos**.

### 0.3 La validación como guardián

RONIN no permite errores de dominio. Además, en 1.1, verifica la coherencia entre `model` y parámetros.

### 0.4 Interoperabilidad como puente

RONIN se integra con Python, Rust, SQL, APIs REST.

### 0.5 RONIN Office como interfaz

RONIN Office permite diseñar sistemas visualmente sin escribir código.

### 0.6 Diagnóstico como honestidad

El comando `diagnose` es la declaración de humildad del lenguaje: te dice cuándo no puedes confiar en los parámetros que estás usando.

---

## SECCIÓN 1: PRINCIPIOS FUNDAMENTALES

### 1.1 Todo es un sistema

```ronin
system Pesca = { parts: 5, resource: 10000, agents: [...], params: {...} }
```

### 1.2 La asignación es la computación

```ronin
result = solve Pesca
```

### 1.3 La coexistencia es la condición de corrección

```ronin
assert(result.coexistence == true)
```

### 1.4 La deuda se audita automáticamente

```ronin
audit = system.debt()
```

### 1.5 La geometría se mide automáticamente

```ronin
let geometry = system.geometry()
```

### 1.6 La fatiga de enrutamiento se calcula

```ronin
let fatigue = system.fatigue()
```

### 1.7 La degeneración se diagnostica (nuevo en 1.1)

```ronin
report = diagnose Pesca with { degeneracy: true }
assert(report.degeneracy == "inactive")
```

---

## SECCIÓN 2: SINTAXIS BÁSICA EXTENDIDA

### 2.1 Declaración de sistema

```ronin
system Nombre = {
    parts: entero,
    resource: flotante,
    agents: [Agent],
    params: Params
}
```

### 2.2 Bloque `params` extendido

```ronin
params: {
    // Núcleo 1.0 (todos opcionales en 1.1)
    alpha:   flotante ∈ [0.5, 2.5]    por defecto 1.0
    gamma:   flotante ∈ [0, 1]         por defecto 0.4
    sigma:   flotante ∈ [0, 0.5]      por defecto 0.0

    // Extensión CES-Saturada
    model:   string ∈ {"pusfre", "ces", "hill", "ces_hill", "full"}
                                       por defecto "pusfre"
    lambda:  flotante ∈ [-1, 2], ≠ 0   por defecto 0.0
    K:       flotante > 0              por defecto ∞
    alpha_h: flotante > 0              por defecto 1.0
    memory_order: entero ∈ {1,2,3,5}   por defecto 1
    memory_weights: [flotante] | null  por defecto null

    // Diagnóstico
    degeneracy_check: booleano         por defecto false
    omega_range_report: booleano       por defecto false
}
```

### 2.3 Restricciones de coherencia

| `model` | `lambda` | `K` | `memory_order` |
|---------|----------|-----|----------------|
| `"pusfre"` | 0 | ∞ | 1 |
| `"ces"` | libre ≠ 0 | ∞ | 1 |
| `"hill"` | 0 | libre > 0 | 1 |
| `"ces_hill"` | libre ≠ 0 | libre > 0 | 1 |
| `"full"` | libre ≠ 0 | libre > 0 | ≥ 1 |

Violación → `SemanticError` con código 2.

### 2.4 Definición de agente

```ronin
agent Industrial = {
    phi: 0.95,
    psi: 0.68,
    frequency: 0.267
}
```

### 2.5 Agente extendido (con nicho)

```ronin
agent Longline = {
    phi: 0.60,
    psi: 0.92,
    frequency: 0.160,
    niche: [0.1, 0.3, 0.5, 0.7, 0.9],
    tools: ["palangre", "anzuelo"],
    protocol: "artesanal"
}
```

### 2.6 Arrays y estructuras

```ronin
let phi = [0.95, 0.85, 0.60, 0.45, 0.70]
let psi = [0.68, 0.76, 0.92, 0.96, 0.84]
```

### 2.7 Funciones puras

```ronin
fn fitness(phi: Probability, psi: Probability, frequency: Frequency, alpha: Alpha) -> Fitness {
    return phi * psi * frequency^alpha
}
```

### 2.8 Funciones impuras

```ronin
fn simulate(system: System) -> Simulation {
    return run_reference_simulation(system)
}
```

### 2.9 Simulación

```ronin
sim = simulate Pesca with {
    steps: 100,
    dtmc: true,
    stochastic: true,
    routing_pressure: Beta(2.3, 5.1)
}
```

### 2.10 Auditoría

```ronin
audit = audit Pesca with {
    epsilon: 0.05,
    delta: 0.01,
    stratified: true,
    clusters: HDBSCAN
}
```

### 2.11 Diagnóstico (nuevo en 1.1)

```ronin
report = diagnose Pesca with {
    omega_range: true,
    degeneracy: true,
    bootstrap: 200
}
```

### 2.12 Visualización

```ronin
plot Pesca
plot sim
plot audit
plot report
```

### 2.13 Condicionales

```ronin
if result.coexistence {
    print("Coexistencia garantizada")
} else {
    print("Sistema inestable. Ajustar parámetros.")
}
```

### 2.14 Bucles

```ronin
for agent in system.agents {
    print(agent.phi)
}
```

### 2.15 Módulos

```ronin
module Fisheries {
    system Atlantic = { ... }
    system Pacific = { ... }
}
import Fisheries
```

### 2.16 Macros

```ronin
macro audit_system(system) {
    return audit(system with {
        epsilon: 0.05,
        delta: 0.01,
        stratified: true
    })
}
```

### 2.17 Macros de diagnóstico (nuevo en 1.1)

```ronin
macro diagnose_and_warn(system) {
    let report = diagnose(system with { degeneracy: true })
    if report.degeneracy == "active" {
        print("ADVERTENCIA: degeneración K–α activa")
    }
    return report
}
```

---

## SECCIÓN 3: TIPOS Y VALIDACIÓN EXTENDIDO

### 3.1 Tipos primitivos

```ronin
type Integer = int
type Float = float
type Boolean = bool
type String = string
type Array = [T]
```

### 3.2 Tipos de dominio (COMPLETO — 160+ tipos)

```ronin
type Probability = float 0..1
type Frequency = Probability
type Resource = float >= 0
type AgentCount = integer >= 2
type Alpha = float 0.5..2.5
type Gamma = float 0..1
type Sigma = float 0..0.5
type Fitness = float >= 0
type Coexistence = bool
type Debt = float 0..1
type Geometry = float 0..1
type Fatigue = float 0..1
type Epsilon = float 0..1
type Rho = float 0..1
type Delta = float 0..0.1
type BatchSize = integer >= 1
type Steps = integer >= 1
type Horizon = integer >= 1
type Confidence = float 0.9..1
type ErrorMargin = float 0..0.2
type Entropy = float 0..max
type Divergence = float >= 0
type Similarity = float 0..1
type Distance = float >= 0
type Time = float >= 0
type Cost = float >= 0
type Benefit = float >= 0
type Utility = float
type Priority = float 0..1
type Severity = float 0..1
type Weight = Probability
type Share = Probability
type Ratio = float >= 0
type Exponent = float >= 0
type Volatility = float >= 0
type Return = float
type Risk = float 0..1
type Throughput = float >= 0
type Latency = float >= 0
type Capacity = float >= 0
type Demand = float >= 0
type Supply = float >= 0
type Inventory = float >= 0
type Backlog = float >= 0
type Waste = float >= 0
type Pollution = float 0..1
type Happiness = float 0..1
type Health = float 0..1
type Trust = float 0..1
type Satisfaction = float 0..1
type Resilience = float 0..1
type Robustness = float 0..1
type Diversity = float 0..1
type Biodiversity = float 0..1
type Complexity = float >= 0
type Stability = float 0..1
type Oscillation = float >= 0
type Convergence = float 0..1
type Error = float >= 0
type Accuracy = float 0..1
type Precision = float 0..1
type Recall = float 0..1
type F1 = float 0..1
type AUC = float 0..1
type ROC = float 0..1
type MSE = float >= 0
type RMSE = float >= 0
type MAE = float >= 0
type R2 = float 0..1
type LogLoss = float >= 0
type KLDivergence = float >= 0
type JSdivergence = float 0..1
type WDistance = float >= 0
type Energy = float >= 0
type Power = float >= 0
type Work = float >= 0
type Efficiency = float 0..1
type Productivity = float >= 0
type Profit = float >= 0
type Revenue = float >= 0
type Investment = float >= 0
type Capital = float >= 0
type Liability = float >= 0
type Asset = float >= 0
type Equity = float >= 0
type Interest = float >= 0
type Inflation = float 0..1
type Growth = float
type Development = float 0..1
type Sustainability = float 0..1
type Inequality = float 0..1
type Justice = float 0..1
type Peace = float 0..1
type Security = float 0..1
type Freedom = float 0..1
type Democracy = float 0..1
type Participation = float 0..1
type Representation = float 0..1
type Transparency = float 0..1
type Accountability = float 0..1
type Legitimacy = float 0..1
type Authority = float 0..1
type Power = float 0..1
type Influence = float 0..1
type Status = float 0..1
type Prestige = float 0..1
type Reputation = float 0..1
type Honor = float 0..1
type Respect = float 0..1
type Dignity = float 0..1
type Compassion = float 0..1
type Empathy = float 0..1
type Solidarity = float 0..1
type Cooperation = float 0..1
type Altruism = float 0..1
type Generosity = float 0..1
type Kindness = float 0..1
type Love = float 0..1
type Beauty = float 0..1
type Truth = float 0..1
type Wisdom = float 0..1
type Understanding = float 0..1
type Insight = float 0..1
type Creativity = float 0..1
type Innovation = float 0..1
type Invention = float 0..1
type Discovery = float 0..1
type Learning = float 0..1
type Teaching = float 0..1
type Mentoring = float 0..1
type Leadership = float 0..1
type Followership = float 0..1
type Partnership = float 0..1
type Friendship = float 0..1
type Community = float 0..1
type Society = float 0..1
type Culture = float 0..1
type Civilization = float 0..1
type Humanity = float 0..1
type Existence = float 0..1
type Reality = float 0..1
type Universe = float 0..1

// Nuevos en 1.1
type Lambda = float -1.0..2.0
type K = float > 0
type AlphaH = float > 0
type MemoryOrder = integer {1, 2, 3, 5}
type ModelName = "pusfre" | "ces" | "hill" | "ces_hill" | "full"
type OmegaRange = float >= 0
type Degeneracy = "active" | "inactive" | "unknown"
type Recommendation = String
```

### 3.3 Tipos compuestos

```ronin
type Agent = {
    phi: Probability,
    psi: Probability,
    frequency: Frequency,
    niche: Array[Float],
    tools: Array[String],
    protocol: String
}

type System = {
    parts: AgentCount,
    resource: Resource,
    agents: Array[Agent],
    params: Params
}

type Params = {
    alpha: Alpha,
    gamma: Gamma,
    sigma: Sigma,
    coexistence_delta: Delta,
    // Extensión 1.1
    model: ModelName,
    lambda: Lambda,
    K: K,
    alpha_h: AlphaH,
    memory_order: MemoryOrder,
    memory_weights: Option[Array[Probability]],
    degeneracy_check: Boolean,
    omega_range_report: Boolean
}

type Solution = {
    allocation: Array[Resource],
    fitness: Array[Fitness],
    coexistence: Option[Coexistence],
    k_min: Option[BatchSize],
    convergence: Convergence,
    steps: Steps,
    debt: Debt,
    audit: Option[AuditResult],
    // Nuevos en 1.1
    model_used: ModelName,
    lambda_used: Lambda,
    K_used: K,
    alpha_h_used: AlphaH,
    omega_range: OmegaRange,
    degeneracy: Degeneracy,
    warnings: Array[String]
}

type DegeneracyReport = {
    omega_range_orders: OmegaRange,
    k_alpha_degenerate: Degeneracy,
    lambda_identifiable: Boolean,
    K_identifiable: Boolean,
    alpha_h_identifiable: Boolean,
    recommendation: Recommendation,
    bootstrap_ci: Option[BootstrapCI]
}

type BootstrapCI = {
    lambda_lo: Float,
    lambda_hi: Float,
    K_lo: Float,
    K_hi: Float,
    alpha_h_lo: Float,
    alpha_h_hi: Float
}

type AuditResult = {
    estimated_debt: Debt,
    confidence: Confidence,
    margin: ErrorMargin,
    ci_lower: Debt,
    ci_upper: Debt,
    sample_size: Integer,
    strata: Array[Strata]
}

type Simulation = {
    history: Array[Array[Frequency]],
    rho_history: Array[Rho],
    extinction_events: Array[ExtinctionEvent],
    final_state: Array[Frequency],
    survivability: Array[Boolean]
}

type ExtinctionEvent = {
    step: Steps,
    agent: Integer,
    rho_at_extinction: Rho
}
```

### 3.4 Validación en tiempo de compilación

```ronin
let alpha: Alpha = 1.3   // ✅ compila
let alpha: Alpha = 3.0   // ❌ no compila
// Error: `alpha` must be between 0.5 and 2.5

let lambda: Lambda = 0.5  // ✅
let lambda: Lambda = 2.5  // ❌
// Error: `lambda` must be between -1.0 and 2.0

let K: K = 0.5   // ✅
let K: K = -1.0  // ❌
// Error: `K` must be > 0
```

### 3.5 Validación de invariantes

RONIN verifica automáticamente:
- Suma de frecuencias = 1
- Todos los phi en [0,1]
- Todos los psi en [0,1]
- Recurso > 0
- Número de partes >= 2
- **Coherencia `model` ↔ parámetros (nuevo en 1.1)**

### 3.6 Inferencia de tipos

```ronin
let phi = [0.95, 0.85, 0.60, 0.45, 0.70]  // inferido como [Probability]
let model = "ces_hill"                     // inferido como ModelName
```

### 3.7 Tipos paramétricos

```ronin
type Option[T] = Some(T) | None
type Result[T, E] = Ok(T) | Err(E)
type Either[A, B] = Left(A) | Right(B)
type Pair[A, B] = (A, B)
type Triple[A, B, C] = (A, B, C)
type Vector[N, T] = Array[N, T]
type Matrix[M, N, T] = Array[M, Vector[N, T]]
```

### 3.8 Tipos recursivos

```ronin
type Tree[T] = Node(T, Tree[T], Tree[T]) | Leaf
type Graph[V, E] = { vertices: Array[V], edges: Array[(V, V, E)] }
type SystemTree = System | Branch(System, System, System)
```

### 3.9 Tipos dependientes (experimental)

```ronin
type Vector[N: integer] = Array[N, float]
// Vector[5] y Vector[10] son tipos diferentes
```

---

## SECCIÓN 4: CONCURRENCIA Y PARALELISMO

### 4.1 Actores

```ronin
actor Industrial {
    state: Agent,
    route: Longline,
    cost: 0.78
}
```

### 4.2 Comunicación entre agentes

```ronin
send Industrial -> Longline {
    resource: 1000,
    time: 10
}
```

### 4.3 Recepción de mensajes

```ronin
actor Longline {
    receive(message: Message) {
        if message.resource > 0 {
            this.resource += message.resource
        }
    }
}
```

### 4.4 Canales

```ronin
channel ResourceChannel = {
    sender: Industrial,
    receiver: Longline,
    capacity: 100
}
```

### 4.5 Paralelismo automático

```ronin
sim = simulate Pesca with {
    parallel: true,
    threads: 8
}
```

### 4.6 Paralelismo manual

```ronin
par {
    sim1 = simulate Pesca1
    sim2 = simulate Pesca2
    sim3 = simulate Pesca3
}
```

### 4.7 Futuros

```ronin
future sim = simulate Pesca
let result = await sim
```

### 4.8 Promesas

```ronin
promise p = async {
    let sim = simulate Pesca
    return sim
}
let result = await p
```

### 4.9 Flujos

```ronin
let stream = stream sim.history
for state in stream {
    print(state)
}
```

### 4.10 Canales con backpressure

```ronin
channel backpressure ResourceChannel {
    capacity: 10,
    on_full: drop
}
```

### 4.11 Diagnóstico en paralelo (nuevo en 1.1)

```ronin
par {
    report1 = diagnose Sistema1 with { bootstrap: 500 }
    report2 = diagnose Sistema2 with { bootstrap: 500 }
    report3 = diagnose Sistema3 with { bootstrap: 500 }
}
```

---

## SECCIÓN 5: INTEROPERABILIDAD (COMPLETA)

### 5.1 Con Python

```ronin
import python "numpy"
let phi = python.numpy.array([0.95, 0.85, 0.60, 0.45, 0.70])
let result = python.numpy.mean(phi)
```

### 5.2 Con Rust

```ronin
import rust "my_crate"
let result = rust.my_crate.solve(system)
```

### 5.3 Con SQL

```ronin
let logs = sql "SELECT phi, psi, frequency FROM agents"
system Pesca = { parts: logs.count, agents: logs }
```

### 5.4 Con APIs REST

```ronin
let response = http.get("https://api.example.com/system")
let system = parse(response.body)
```

### 5.5 Con GraphQL

```ronin
let query = graphql.query("query { system { agents { phi psi frequency } } }")
let system = parse(query)
```

### 5.6 Con WebSockets

```ronin
let ws = websocket.connect("wss://example.com/system")
ws.send(system)
let result = ws.receive()
```

### 5.7 Con gRPC

```ronin
let client = grpc.connect("example.com:50051")
let result = client.solve(system)
```

### 5.8 Con archivos

```ronin
let system = read("system.yaml")
let result = solve(system)
write("solution.json", result)
```

### 5.9 Con CSV

```ronin
let data = csv.read("agents.csv")
let system = create_system(data)
```

### 5.10 Con JSON

```ronin
let data = json.read("system.json")
let system = parse(data)
```

### 5.11 Con YAML

```ronin
let data = yaml.read("system.yaml")
let system = parse(data)
```

### 5.12 Con TOML

```ronin
let data = toml.read("system.toml")
let system = parse(data)
```

### 5.13 Con XML

```ronin
let data = xml.read("system.xml")
let system = parse(data)
```

### 5.14 Con Protobuf

```ronin
let data = protobuf.read("system.pb")
let system = parse(data)
```

### 5.15 Con MsgPack

```ronin
let data = msgpack.read("system.msgpack")
let system = parse(data)
```

### 5.16 Con BSON

```ronin
let data = bson.read("system.bson")
let system = parse(data)
```

### 5.17 Con Avro

```ronin
let data = avro.read("system.avro")
let system = parse(data)
```

### 5.18 Con Parquet

```ronin
let data = parquet.read("system.parquet")
let system = parse(data)
```

### 5.19 Con Arrow

```ronin
let data = arrow.read("system.arrow")
let system = parse(data)
```

### 5.20 Con pandas (Python)

```ronin
import python "pandas"
let df = python.pandas.read_csv("agents.csv")
let agents = df.to_dict()
```

---

## SECCIÓN 6: COMPILACIÓN Y EJECUCIÓN

### 6.1 Compilación a código nativo

```bash
ronin compile system.ronin -o system
./system
```

### 6.2 Compilación a WASM

```bash
ronin compile system.ronin -o system.wasm
```

### 6.3 Compilación a C

```bash
ronin compile system.ronin -o system.c
gcc -O3 system.c -o system
```

### 6.4 Compilación a Python

```bash
ronin compile system.ronin -o system.py
python system.py
```

### 6.5 Compilación a LLVM IR

```bash
ronin compile system.ronin -o system.ll
```

### 6.6 Compilación a JVM bytecode

```bash
ronin compile system.ronin -o System.class
```

### 6.7 Compilación a .NET IL

```bash
ronin compile system.ronin -o System.dll
```

### 6.8 Compilación a JavaScript

```bash
ronin compile system.ronin -o system.js
```

### 6.9 Interpretación

```bash
ronin run system.ronin
```

### 6.10 Niveles de optimización

```bash
ronin compile system.ronin -O0   # sin optimización
ronin compile system.ronin -O1   # ligera
ronin compile system.ronin -O2   # media
ronin compile system.ronin -O3   # máxima
```

### 6.11 Perfilado

```bash
ronin compile system.ronin --profile
./system
ronin profile system.prof
```

### 6.12 Depuración

```bash
ronin debug system.ronin
```

### 6.13 REPL

```bash
ronin repl
> let phi = [0.95, 0.85, 0.60, 0.45, 0.70]
> let system = create_system(5, 10000, phi, ...)
> let result = solve(system)
> result.allocation
[3138.305, 2702.592, 1378.139, 831.638, 1949.325]
> let report = diagnose(system with { degeneracy: true })
> report.degeneracy
"inactive"
```

### 6.14 Diagnóstico desde CLI (nuevo en 1.1)

```bash
ronin diagnose system.ronin --bootstrap 200
# {
#   "omega_range_orders": 3.0,
#   "degeneracy": "inactive",
#   "K_identifiable": true,
#   "alpha_h_identifiable": true,
#   "recommendation": "Identificación estructural OK."
# }
```

---

## SECCIÓN 7: HERRAMIENTAS DE DESARROLLO

| Comando | Función |
|---------|---------|
| `ronin fmt system.ronin` | Formateador |
| `ronin lint system.ronin` | Linter |
| `ronin doc system.ronin -o docs/` | Generador de documentación |
| `ronin test system.ronin -o tests/` | Generador de tests |
| `ronin bench system.ronin -o benches/` | Generador de benchmarks |
| `ronin diagram system.ronin -o system.png` | Generador de diagramas |
| `ronin animate sim.ronin -o sim.gif` | Generador de animaciones |
| `ronin report audit.ronin -o report.pdf` | Generador de informes |
| `ronin dashboard system.ronin -o dashboard.html` | Generador de dashboards |
| **`ronin diagnose system.ronin`** | **Diagnóstico de degeneración (nuevo en 1.1)** |

---

## SECCIÓN 8: CASOS DE USO COMPLETOS

### 8.1 Pesca (5 flotas, PUSFRE clásico)

```ronin
system AtlanticFleet = {
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
        alpha: 1.3,
        gamma: 0.4,
        sigma: 0.15,        coexistence_delta: 0.05
    }
}
result = solve AtlanticFleet
print(result.allocation)  // [3138.305, 2702.592, 1378.139, 831.638, 1949.325]
print(result.coexistence) // true
```

### 8.2 Pesca con CES-Saturada (nuevo en 1.1)

```ronin
system AtlanticFleetCES = {
    parts: 5,
    resource: 10000,
    agents: [ /* mismos agentes */ ],
    params: {
        model: "ces_hill",
        lambda: 0.5,
        K: 0.5,
        alpha_h: 1.5,
        alpha: 1.3,
        gamma: 0.4,
        sigma: 0.15,
        coexistence_delta: 0.05,
        degeneracy_check: true
    }
}
result = solve AtlanticFleetCES
report = diagnose AtlanticFleetCES with { degeneracy: true }
print(report.degeneracy)  // "active" (Ω estrecho)
```

### 8.3 Neural Scaling (nuevo en 1.1)

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
report = diagnose NeuralScaling with { degeneracy: true, bootstrap: 1000 }
print(report.omega_range_orders)  // ~3.0
print(report.degeneracy)           // "inactive"
print(report.K_identifiable)       // true
```

### 8.4 Logística (50 vehículos)

```ronin
system Logistics = {
    parts: 50,
    resource: 480,
    agents: generate_vehicles(50),
    params: {
        alpha: 1.2,
        gamma: 0.35,
        sigma: 0.12,
        coexistence_delta: 0.05
    }
}
result = solve Logistics
print(result.allocation)
```

### 8.5 Finanzas (20 activos)

```ronin
system Portfolio = {
    parts: 20,
    resource: 100,
    agents: generate_assets(20),
    params: {
        alpha: 1.0,
        gamma: 0.3,
        sigma: 0.20,
        coexistence_delta: 0.01
    }
}
result = solve Portfolio
print(result.allocation)
```

### 8.6 Tráfico (100 semáforos)

```ronin
system Traffic = {
    parts: 100,
    resource: 120,
    agents: generate_intersections(100),
    params: {
        alpha: 1.2,
        gamma: 0.4,
        sigma: 0.15,
        coexistence_delta: 0.05
    }
}
sim = simulate Traffic with {
    steps: 1000,
    dtmc: true,
    stochastic: true
}
plot sim
```

### 8.7 RAG (1M documentos)

```ronin
system RAG = {
    parts: 1000000,
    resource: 100,
    agents: generate_documents(1000000),
    params: {
        gamma: 0.45,
        sigma: 0.10
    }
}
audit = audit RAG with {
    epsilon: 0.05,
    delta: 0.01,
    stratified: true
}
print(audit.estimated_debt)
```

### 8.8 Urban Scaling (nuevo en 1.1)

```ronin
system UrbanScaling = {
    parts: 10000,
    resource: 1.0,
    agents: generate_cities(10000),
    params: {
        model: "ces_hill",
        lambda: 0.5,
        K: 1.0,
        alpha_h: 1.4,
        degeneracy_check: true,
        omega_range_report: true
    }
}
result = solve UrbanScaling
report = diagnose UrbanScaling with { degeneracy: true }
print(report.omega_range_orders)  // ~5.0
print(report.degeneracy)           // "inactive"
```

### 8.9 Fama-French (720 meses, negativo)

```ronin
system FamaFrench = {
    parts: 720,
    resource: 1.0,
    agents: generate_returns(720),
    params: {
        model: "pusfre",  // la elección correcta aquí
        alpha: 1.0,
        gamma: 0.3,
        sigma: 0.2
    }
}
result = solve FamaFrench
// La familia CES-Saturada no mejora aquí porque Ω es estrecho
```

---

## SECCIÓN 9: COMPARATIVA CON OTROS LENGUAJES

### 9.1 Rendimiento — estado de verificación

El material histórico de RONIN contiene cifras de rendimiento y memoria. Esas cifras no forman parte de la especificación normativa de v1.1 porque no están acompañadas aquí por un protocolo reproducible y una implementación versionada.

La v1.1 define en su lugar un protocolo de benchmark: cada comparación deberá indicar versión del runtime, commit, hardware, sistema operativo, tamaño de entrada, número de repeticiones, calentamiento, distribución de resultados y código utilizado. Hasta que esos datos existan, no se asignan cifras de rendimiento a RONIN.

### 9.2 Expresividad — criterio, no resultado medido

La expresividad de RONIN se describe cualitativamente por la capacidad de representar sistemas, simulaciones, auditorías y diagnósticos mediante sus primitivas. No se presentan puntuaciones comparativas como hechos medidos.

### 9.3 Seguridad — propiedades definidas

RONIN incorpora tipos de dominio, rangos e invariantes como parte de su especificación. Esto permite comprobar ciertas clases de errores antes de ejecutar un sistema. No implica por sí mismo una garantía de seguridad general frente a todas las amenazas.

### 9.4 Interoperabilidad — capacidades previstas

La especificación contempla interfaces con Python, Rust, SQL, APIs y distintos targets de ejecución. En v1.1 solo se considera implementada una integración cuando exista un módulo correspondiente y pase el conjunto de conformidad.

### 9.5 Curva de aprendizaje

| Lenguaje | Primer sistema | Sistema complejo | Documentación |
|----------|----------------|------------------|---------------|
| Python | 30 min | 2 horas | Excelente |
| Rust | 2 horas | 1 día | Buena |
| Julia | 1 hora | 4 horas | Buena |
| R | 1 hora | 4 horas | Buena |
| MATLAB | 1 hora | 4 horas | Buena |
| **RONIN** | **5 min** | **30 min** | **Integrada** |

---

## SECCIÓN 10: IMPLEMENTACIÓN

### 10.1 El intérprete (Rust core extendido)

```rust
// ronin_core/src/lib.rs
pub struct System {
    pub parts: usize,
    pub resource: f64,
    pub agents: Vec<Agent>,
    pub params: Params,
}

pub struct Agent {
    pub phi: f64,
    pub psi: f64,
    pub frequency: f64,
}

pub struct Params {
    // Núcleo 1.0
    pub alpha: f64,
    pub gamma: f64,
    pub sigma: f64,
    pub coexistence_delta: f64,
    // Extensión 1.1
    pub model: String,
    pub lambda: f64,
    pub K: f64,
    pub alpha_h: f64,
    pub memory_order: usize,
    pub memory_weights: Option<Vec<f64>>,
    pub degeneracy_check: bool,
    pub omega_range_report: bool,
}

pub struct Solution {
    pub allocation: Vec<f64>,
    pub fitness: Vec<f64>,
    pub coexistence: Option<bool>,
    pub k_min: Option<f64>,
    pub convergence: bool,
    pub steps: usize,
    pub debt: f64,
    // Nuevos en 1.1
    pub model_used: String,
    pub lambda_used: f64,
    pub K_used: f64,
    pub alpha_h_used: f64,
    pub omega_range: f64,
    pub degeneracy: String,
    pub warnings: Vec<String>,
}

pub fn solve(system: &System) -> Result<Solution, Error> {
    validate_system(system)?;
    validate_coherence(&system.params)?;
    let fitness = calculate_fitness(system)?;
    let allocation = normalize_fitness_to_resource(&fitness, system.resource)?;
    let coexistence = check_coexistence(&allocation, &system.params)?;
    let k_min = calculate_k_min(system)?;
    let debt = calculate_debt(system)?;

    let omega_range = omega_range_orders(&system.agents);
    let degeneracy = degeneracy_state(
        omega_range,
        system.params.K.is_finite(),
        system.params.alpha_h != 1.0,
    );

    Ok(Solution {
        allocation, fitness, coexistence, k_min, debt,
        convergence: true, steps: 1,
        model_used: system.params.model.clone(),
        lambda_used: system.params.lambda,
        K_used: system.params.K,
        alpha_h_used: system.params.alpha_h,
        omega_range, degeneracy,
        warnings: vec![],
    })
}
```

### 10.2 Python bindings (PyO3 extendido)

```rust
use pyo3::prelude::*;

#[pyfunction]
fn solve_system(parts: usize, resource: f64, agents: Vec<Agent>, params: Params) -> PyResult<Solution> {
    let system = System { parts, resource, agents, params };
    let solution = solve(&system)?;
    Ok(solution)
}

#[pyfunction]
fn diagnose_system(parts: usize, resource: f64, agents: Vec<Agent>, params: Params) -> PyResult<DegeneracyReport> {
    let system = System { parts, resource, agents, params };
    let report = diagnose(&system)?;
    Ok(report)
}

#[pymodule]
fn ronin(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(solve_system, m)?)?;
    m.add_function(wrap_pyfunction!(diagnose_system, m)?)?;
    Ok(())
}
```

### 10.3 Compiladores

| Salida | Comando |
|--------|---------|
| Rust | `ronin compile system.ronin -o system.rs` |
| C | `ronin compile system.ronin -o system.c` |
| WASM | `ronin compile system.ronin -o system.wasm` |
| Python | `ronin compile system.ronin -o system.py` |
| LLVM IR | `ronin compile system.ronin -o system.ll` |
| JVM bytecode | `ronin compile system.ronin -o System.class` |
| .NET IL | `ronin compile system.ronin -o System.dll` |
| JavaScript | `ronin compile system.ronin -o system.js` |

---

## SECCIÓN 11: EXTENSIONES Y FUTURO

### 11.1 Sistemas continuos

```ronin
system Continuous = {
    parts: 5,
    continuous: true,
    ...
}
```

### 11.2 Sistemas con memoria extendida

```ronin
system Memory = {
    parts: 5,
    memory: 10,
    ...
}
```

### 11.3 Interacciones directas

```ronin
system Interactions = {
    parts: 5,
    interactions: [
        { from: A, to: B, type: "cooperation" },
        { from: B, to: C, type: "competition" }
    ],
    ...
}
```

### 11.4 Sistemas con aprendizaje

```ronin
system Learning = {
    parts: 5,
    learning: true,
    model: "neural",
    ...
}
```

### 11.5 Optimización multi-objetivo

```ronin
system MultiObjective = {
    parts: 5,
    objectives: ["coexistence", "efficiency", "resilience"],
    ...
}
```

### 11.6 Sistemas con incertidumbre

```ronin
system Uncertainty = {
    parts: 5,
    uncertainty: "bayesian",
    ...
}
```

### 11.7 Sistemas con agentes heterogéneos

```ronin
system Heterogeneous = {
    parts: 5,
    heterogeneity: true,
    ...
}
```

### 11.8 Topología variable

```ronin
system Topology = {
    parts: 5,
    topology: "dynamic",
    ...
}
```

### 11.9 Escalado automático

```ronin
system Scaling = {
    parts: 5,
    scaling: "auto",
    ...
}
```

### 11.10 Explicabilidad

```ronin
system Explainable = {
    parts: 5,
    explain: true,
    ...
}
```

### 11.11 Diagnóstico multi-dominio (nuevo en 1.1)

```ronin
system MultiDiagnose = {
    domains: ["neural_scaling", "urban_scaling", "fama_french"],
    diagnostic: true,
    ...
}
```

---

## SECCIÓN 12: KOANS DE RONIN

**Del lenguaje que no se aprende:**
RONIN no se aprende. Se reconoce.

**Del programa que no se escribe:**
El mejor programa es el que se declara.

**Del error que no ocurre:**
En RONIN, los errores definidos por la especificación deben detectarse durante la validación cuando sea posible.

**De la interoperabilidad que no es un compromiso:**
La especificación define puntos de integración previstos con Python, Rust, SQL y APIs; cada integración debe considerarse disponible solo cuando exista una implementación correspondiente.

**Del ingeniero que no debuguea:**
El ingeniero que usa RONIN debuguea problemas de dominio, no de tipo.

**Del sistema que no colapsa:**
RONIN evalúa la condición de coexistencia definida por la especificación. Si no puede establecerla con los datos disponibles, el resultado debe indicarlo explícitamente.

**De la IA que no se equivoca:**
Una herramienta externa puede generar RONIN y el validador puede comprobar si el programa cumple la especificación. La corrección automática no forma parte del núcleo de v1.1.

**Del arquitecto que no escribe código:**
El arquitecto declara sistemas. El lenguaje se encarga del resto.

**Del cerrajero que diseñó la llave maestra:**
RONIN está diseñado como un lenguaje especializado para sistemas finitos con recursos escasos; no pretende resolver cualquier clase de sistema.

**Del autor que se ríe desde 1310:**
El autor sabe que RONIN es inevitable. El PUSFRE requería un lenguaje. Y el lenguaje es RONIN.

**De la familia:**
No busques la ecuación única. Busca la familia que la contiene.

**De la degeneración:**
Dos parámetros que no puedes distinguir no son dos parámetros. Son uno disfrazado.

**Del diagnóstico:**
El sistema que te dice cuándo no puedes confiar en él vale más que el que te dice que todo está bien.

**De la honestidad:**
El PUSFRE no es una ecuación. Es una familia. RONIN no la impone. La ejecuta.

---

## SECCIÓN 13: SOPORTE NATIVO PARA LINUX

### 13.1 Integración con systemd

**Archivo de unidad systemd (`/etc/systemd/system/ronin.service`):**

```ini
[Unit]
Description=RONIN System Solver
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/ronin run /etc/ronin/sistema.ronin
Restart=always
RestartSec=10
User=ronin
Group=ronin

# Seguridad
ProtectSystem=full
PrivateTmp=true
NoNewPrivileges=true

# Logs
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Comandos útiles:**

```bash
sudo systemctl start ronin
sudo systemctl stop ronin
sudo systemctl status ronin
sudo journalctl -u ronin -f
```

### 13.2 Registro en journald (logs estructurados)

```bash
journalctl -u ronin --grep "Pesca"
journalctl -u ronin --grep "audit"
journalctl -u ronin --grep "degeneracy"
journalctl -u ronin -p err
```

```ronin
journal.write("Sistema Pesca resuelto", level: INFO, tags: ["pesca", "resuelto"])
journal.write("Degeneración detectada", level: WARNING, tags: ["degeneracy", "K-alpha"])
```

### 13.3 Manejo de señales POSIX

| Señal | Comportamiento en RONIN |
|-------|-------------------------|
| `SIGINT` (Ctrl+C) | Detiene la ejecución actual y guarda el estado intermedio. |
| `SIGTERM` | Finaliza el proceso de forma ordenada, escribiendo el último resultado en un archivo de checkpoint. |
| `SIGHUP` | Recarga la configuración del sistema sin reiniciar el proceso. |
| `SIGUSR1` | Genera un informe de auditoría en el momento actual. |
| `SIGUSR2` | Vuelca el estado del sistema (frecuencias, deuda, degeneración) a un archivo de diagnóstico. |

### 13.4 Pipes y redirecciones

```bash
ronin run --input agents.csv --output solucion.json
ronin run sistema.ronin | jq '.allocation'
ronin diagnose sistema.ronin | jq '.degeneracy'
ronin run sistema.ronin | awk '{print $1}'
```

### 13.5 Integración con cron

```cron
0 2 * * * /usr/local/bin/ronin run /etc/ronin/pesca.ronin --output /var/ronin/pesca.json
0 3 * * 1 /usr/local/bin/ronin audit /etc/ronin/pesca.ronin --output /var/ronin/audit.json
0 4 * * 0 /usr/local/bin/ronin diagnose /etc/ronin/pesca.ronin --output /var/ronin/diag.json
```

### 13.6 Sistema de archivos y ubicaciones estándar

| Ruta | Contenido |
|------|-----------|
| `/usr/local/bin/ronin` | Binario principal |
| `/etc/ronin/` | Archivos de configuración y sistemas |
| `/var/ronin/` | Datos de sistemas en ejecución |
| `/var/ronin/checkpoints/` | Puntos de control |
| `/var/ronin/diagnostics/` | Informes de degeneración (nuevo en 1.1) |
| `/var/log/ronin/` | Logs en texto plano |

### 13.7 Soporte para sockets Unix

```ronin
server = unix_socket.bind("/var/run/ronin.sock")
server.listen()
```

```bash
echo 'solve Pesca' | nc -U /var/run/ronin.sock
echo 'diagnose Pesca' | nc -U /var/run/ronin.sock
```

### 13.8 Integración con inotify

```ronin
monitor /etc/ronin/pesca.ronin on change {
    print("Configuración actualizada. Recalculando...")
    reload_system()
}
```

### 13.9 Soporte para seccomp y sandboxing

```bash
ronin run sistema.ronin --seccomp
```

---

## SECCIÓN 14: APLICACIONES DE RONIN EN DESARROLLO DE SOFTWARE

### 14.1 VIDEOJUEGOS

**Ejemplo: Balanceo de clases en un RPG con CES**

```ronin
system BalanceoClases = {
    parts: 3,
    resource: 100,
    agents: [
        { name: "Guerrero", phi: 0.9, psi: 0.8, frequency: 0.33 },
        { name: "Mago", phi: 0.95, psi: 0.5, frequency: 0.33 },
        { name: "Picaro", phi: 0.75, psi: 0.9, frequency: 0.33 }
    ],
    params: {
        model: "ces",
        lambda: 0.6,
        alpha: 1.2,
        gamma: 0.4,
        sigma: 0.1
    },
    invariants: [
        "allocation[0] > 25",
        "allocation[1] > 25",
        "allocation[2] > 25"
    ]
}

result = solve BalanceoClases
print(result.allocation)  // Distribución con curvatura CES
```

**Ejemplo: Simulación de IA enemiga**

```ronin
system Enemigos = {
    parts: 4,
    resource: 100,
    agents: [
        { name: "Tanque", phi: 0.6, psi: 0.7, frequency: 0.25 },
        { name: "Veloz", phi: 0.9, psi: 0.4, frequency: 0.25 },
        { name: "Normal", phi: 0.8, psi: 0.8, frequency: 0.25 },
        { name: "Jefe", phi: 0.95, psi: 0.3, frequency: 0.25 }
    ],
    params: { alpha: 1.3, gamma: 0.5, sigma: 0.15 }
}

sim = simulate Enemigos with { steps: 50, dtmc: true, stochastic: true }
plot sim
```

### 14.2 DESARROLLO WEB Y BALANCEO DE CARGA

**Ejemplo: Balanceo de carga entre microservicios**

```ronin
system Microservicios = {
    parts: 4,
    resource: 1000,
    agents: [
        { name: "Auth", phi: 0.9, psi: 0.95, frequency: 0.25 },
        { name: "API", phi: 0.85, psi: 0.9, frequency: 0.25 },
        { name: "Database", phi: 0.7, psi: 0.85, frequency: 0.25 },
        { name: "Cache", phi: 0.95, psi: 0.8, frequency: 0.25 }
    ],
    params: { model: "ces", lambda: 0.4, alpha: 1.1, gamma: 0.3, sigma: 0.1 }
}

result = solve Microservicios
```

### 14.3 SISTEMAS EMBEBIDOS E IoT

**Ejemplo: Asignación de tiempo de CPU en un microcontrolador**

```ronin
system TareasEmbebidas = {
    parts: 4,
    resource: 100,
    agents: [
        { name: "Sensores", phi: 0.7, psi: 0.9, frequency: 0.25 },
        { name: "Comunicación", phi: 0.8, psi: 0.8, frequency: 0.25 },
        { name: "Procesamiento", phi: 0.9, psi: 0.7, frequency: 0.25 },
        { name: "UI", phi: 0.5, psi: 0.95, frequency: 0.25 }
    ],
    params: { model: "pusfre", alpha: 0.8, gamma: 0.3, sigma: 0.05 }
}

result = solve TareasEmbebidas
```

### 14.4 ROBÓTICA Y CONTROL DE SISTEMAS

**Ejemplo: Asignación de tareas a robots en una flota**

```ronin
system FlotaRobotica = {
    parts: 5,
    resource: 100,
    agents: [
        { name: "Robot1", phi: 0.8, psi: 0.9, frequency: 0.2 },
        { name: "Robot2", phi: 0.7, psi: 0.85, frequency: 0.2 },
        { name: "Robot3", phi: 0.9, psi: 0.8, frequency: 0.2 },
        { name: "Robot4", phi: 0.6, psi: 0.9, frequency: 0.2 },
        { name: "Robot5", phi: 0.85, psi: 0.85, frequency: 0.2 }
    ],
    params: { model: "ces", lambda: 0.4, alpha: 1.1, gamma: 0.3, sigma: 0.1 }
}

result = solve FlotaRobotica
```

### 14.5 CIENCIA DE DATOS Y MACHINE LEARNING

**Ejemplo: Muestreo estratificado**

```ronin
import python "pandas"

let df = python.pandas.read_csv("datos.csv")
let strata = stratify(df.embeddings, clusters: HDBSCAN)
let allocation = neyman_allocation(strata, epsilon: 0.05, delta: 0.01)
let samples = sample_pairs(strata, allocation)
let estimate = hoefding_estimate(samples)
print(estimate)  // 0.034 ± 0.012 (99% CI)
```

**Ejemplo: Optimización de hiperparámetros**

```ronin
system Hyperparametros = {
    parts: 4,
    resource: 100,
    agents: [
        { name: "LearningRate", phi: 0.8, psi: 0.7, frequency: 0.25 },
        { name: "BatchSize", phi: 0.7, psi: 0.8, frequency: 0.25 },
        { name: "Dropout", phi: 0.6, psi: 0.9, frequency: 0.25 },
        { name: "L2Reg", phi: 0.5, psi: 0.95, frequency: 0.25 }
    ],
    params: { model: "ces", lambda: 0.5, alpha: 0.9, gamma: 0.2, sigma: 0.05 }
}

result = solve Hyperparametros
```

### 14.6 FINANZAS Y TRADING ALGORÍTMICO

**Ejemplo: Gestión de cartera con coexistencia**

```ronin
system Cartera = {
    parts: 5,
    resource: 100,
    agents: [
        { name: "Acciones", phi: 0.9, psi: 0.6, frequency: 0.2 },
        { name: "Bonos", phi: 0.7, psi: 0.9, frequency: 0.2 },
        { name: "Commodities", phi: 0.8, psi: 0.7, frequency: 0.2 },
        { name: "Divisas", phi: 0.6, psi: 0.8, frequency: 0.2 },
        { name: "Cripto", phi: 0.95, psi: 0.3, frequency: 0.2 }
    ],
    params: { model: "ces", lambda: 0.4, alpha: 0.9, gamma: 0.4, sigma: 0.15 }
}

result = solve Cartera
```

### 14.7 BLOCKCHAIN Y CRIPTOMONEDAS

**Ejemplo: Distribución de poder de minería**

```ronin
system Mineria = {
    parts: 5,
    resource: 100,
    agents: [
        { name: "Pool1", phi: 0.8, psi: 0.9, frequency: 0.2 },
        { name: "Pool2", phi: 0.7, psi: 0.85, frequency: 0.2 },
        { name: "Pool3", phi: 0.9, psi: 0.8, frequency: 0.2 },
        { name: "Pool4", phi: 0.6, psi: 0.9, frequency: 0.2 },
        { name: "Pool5", phi: 0.85, psi: 0.85, frequency: 0.2 }
    ],
    params: { model: "pusfre", alpha: 1.2, gamma: 0.3, sigma: 0.1 }
}

result = solve Mineria
```

### 14.8 SISTEMAS DE RECOMENDACIÓN

**Ejemplo: Distribución de contenidos**

```ronin
system Recomendaciones = {
    parts: 5,
    resource: 100,
    agents: [
        { name: "Noticias", phi: 0.8, psi: 0.7, frequency: 0.2 },
        { name: "Video", phi: 0.9, psi: 0.6, frequency: 0.2 },
        { name: "Artículo", phi: 0.7, psi: 0.8, frequency: 0.2 },
        { name: "Podcast", phi: 0.6, psi: 0.9, frequency: 0.2 },
        { name: "Social", phi: 0.85, psi: 0.75, frequency: 0.2 }
    ],
    params: { model: "ces", lambda: 0.5, alpha: 0.8, gamma: 0.2, sigma: 0.1 }
}

result = solve Recomendaciones
```

### 14.9 OPTIMIZACIÓN DE RECURSOS EN CLOUD

**Ejemplo: Kubernetes**

```ronin
system Kubernetes = {
    parts: 4,
    resource: 100,
    agents: [
        { name: "Web", phi: 0.8, psi: 0.9, frequency: 0.25 },
        { name: "API", phi: 0.85, psi: 0.85, frequency: 0.25 },
        { name: "DB", phi: 0.7, psi: 0.95, frequency: 0.25 },
        { name: "Cache", phi: 0.9, psi: 0.8, frequency: 0.25 }
    ],
    params: { model: "pusfre", alpha: 1.0, gamma: 0.2, sigma: 0.05 }
}

result = solve Kubernetes
```

### 14.10 INTELIGENCIA ARTIFICIAL MULTI-AGENTE

**Ejemplo: Sistema multi-agente de atención al cliente**

```ronin
system AtencionCliente = {
    parts: 3,
    resource: 100,
    agents: [
        { name: "Soporte", phi: 0.8, psi: 0.9, frequency: 0.33 },
        { name: "Ventas", phi: 0.7, psi: 0.8, frequency: 0.33 },
        { name: "Tecnico", phi: 0.9, psi: 0.7, frequency: 0.33 }
    ],
    params: { model: "ces", lambda: 0.4, alpha: 1.1, gamma: 0.3, sigma: 0.1 }
}

result = solve AtencionCliente
diagnose_result = diagnose AtencionCliente with { degeneracy: true }
print(diagnose_result.degeneracy)  // "active" (Ω estrecho)
```

### 14.11 ANÁLISIS CIENTÍFICO CON FAMILIA (nuevo en 1.1)

**Ejemplo: Neural Scaling**

```ronin
system NeuralScaling = {
    parts: 46,
    resource: 1.0,
    agents: [
        { name: "Model1", phi: log(8M), psi: log(10B), frequency: log(1e18) },
        ...
    ],
    params: {
        model: "ces_hill",
        lambda: 0.5,
        K: 1.0,
        alpha_h: 1.5,
        degeneracy_check: true
    }
}
result = solve NeuralScaling
report = diagnose NeuralScaling with { degeneracy: true, bootstrap: 1000 }
print(report.degeneracy)         // "inactive"
print(report.omega_range_orders) // ~3.0
print(report.K_identifiable)     // true
```

**Ejemplo: Urban Scaling**

```ronin
system UrbanScaling = {
    parts: 10000,
    resource: 1.0,
    agents: generate_cities(10000),
    params: {
        model: "ces_hill",
        lambda: 0.5,
        K: 1.0,
        alpha_h: 1.4,
        degeneracy_check: true
    }
}
result = solve UrbanScaling
report = diagnose UrbanScaling with { degeneracy: true }
print(report.omega_range_orders)  // ~5.0
print(report.degeneracy)          // "inactive"
```

---

## SECCIÓN 15: KOANS DEL DESARROLLADOR DE SOFTWARE

**Del game designer:**
Un juego sin balance es un mundo sin leyes. RONIN te da las leyes. Tú pones el mundo.

**Del arquitecto de sistemas:**
Una línea de RONIN puede reemplazar 200 líneas de Python para balanceo de carga.

**Del desarrollador embebido:**
Tu microcontrolador no tiene recursos infinitos. RONIN te dice dónde usarlos.

**Del científico de datos:**
El muestreo aleatorio es para quienes no conocen Hoeffding. RONIN sí lo conoce.

**Del trader:**
Tu cartera no es un conjunto de activos. Es un ecosistema financiero. RONIN lo equilibra.

**Del ingeniero de blockchain:**
La descentralización no es un ideal. Es un problema de coexistencia. RONIN lo resuelve.

**Del arquitecto cloud:**
Kubernetes programa recursos. RONIN los optimiza.

**Del desarrollador de IA:**
Los agentes no son funciones. Son especies. Trátalos como ecosistema.

**Del investigador:**
No todas las estructuras son log-lineales. La familia CES-Saturada existe para cuando no lo son.

**Del diagnosticador:**
El número sin diagnóstico es una opinión.

---
