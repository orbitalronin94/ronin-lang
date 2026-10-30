# PARTE IV — ANEXO DEL COMPILADOR: ARQUITECTURA Y EXTENSIÓN

## PRÓLOGO DEL COMPILADOR

Este anexo está dirigido a quienes quieran **entender cómo funciona RONIN por dentro** o **extenderlo con nuevas funcionalidades**. No necesitas leerlo para usar RONIN, pero si quieres contribuir, optimizar o simplemente sentir curiosidad, aquí tienes el plano completo de la máquina.

La implementación de referencia propuesta para RONIN puede escribirse en **Rust** y se organiza conceptualmente en tres capas; esta especificación no afirma que una implementación completa ya exista:

1. **Frontend:** análisis sintáctico, validación semántica y generación de IR.
2. **Middle-end:** optimizaciones del IR (simplificación, plegado de constantes, etc.).
3. **Backend:** generación de código para diferentes objetivos (nativo, WASM, C, Python...).

---

## ANEXO 1: ESTRUCTURA INTERNA DEL COMPILADOR

### 1.1 Visión general

La arquitectura propuesta se organiza en varias fases, que se pueden ver como un pipeline:

```
[ Código fuente RONIN ]
        │
        ▼
┌───────────────────────────┐
│  Parser (nom)             │  → AST (Abstract Syntax Tree)
└───────────────────────────┘
        │
        ▼
┌───────────────────────────┐
│  Validador de dominio     │  → Verifica tipos, rangos, invariantes
└───────────────────────────┘
        │
        ▼
┌───────────────────────────┐
│  Validador de coherencia  │  → Verifica coherencia model ↔ params
└───────────────────────────┘
        │
        ▼
┌───────────────────────────┐
│  Generador de IR          │  → Sistema de ecuaciones en forma normal
└───────────────────────────┘
        │
        ▼
┌───────────────────────────┐
│  Optimizador de IR        │  → Simplificación, fusión, plegado
└───────────────────────────┘
        │
        ▼
┌───────────────────────────┐
│  Backend selector         │  → Elige el objetivo (nativo, WASM, C, ...)
└───────────────────────────┘
        │
        ▼
┌───────────────────────────┐
│  Generador de código      │  → Código fuente en el lenguaje objetivo
└───────────────────────────┘
```

### 1.2 El AST (Abstract Syntax Tree)

El AST de RONIN es una representación estructurada del código fuente. Los nodos principales son:

```rust
enum ASTNode {
    System { name: String, parts: usize, resource: f64, agents: Vec<Agent>, params: Params },
    Agent { phi: f64, psi: f64, frequency: f64 },
    Params {
        alpha: f64, gamma: f64, sigma: f64,
        // Extensión 1.1
        model: String, lambda: f64, K: f64, alpha_h: f64,
        memory_order: usize, memory_weights: Option<Vec<f64>>,
        degeneracy_check: bool, omega_range_report: bool
    },
    CommandSolve { system: String },
    CommandSimulate { system: String, options: SimulateOptions },
    CommandAudit { system: String, options: AuditOptions },
    CommandDiagnose { system: String, options: DiagnoseOptions },
    CommandPlot { target: String },
    Let { name: String, value: Box<ASTNode> },
    Fn { name: String, params: Vec<Type>, body: Box<ASTNode> },
    If { cond: Box<ASTNode>, then: Box<ASTNode>, r#else: Option<Box<ASTNode>> },
    For { var: String, iter: Box<ASTNode>, body: Box<ASTNode> },
    // etc.
}
```

### 1.3 El IR (Intermediate Representation)

El IR es una representación **plana y lineal** del sistema, lista para ser optimizada y compilada. En lugar de mantener la estructura jerárquica del AST, el IR organiza el sistema como una lista de ecuaciones.

```rust
struct IR {
    equations: Vec<Equation>,
    commands: Vec<Command>,
    constants: HashMap<String, f64>,
}

enum Equation {
    Fitness { agent: usize, expr: Expr },
    Allocation { agent: usize, expr: Expr },
    Coexistence { agent: usize, expr: Expr },
    HillSaturation { agent: usize, expr: Expr },
    CESCombine { agent: usize, expr: Expr },
    DegeneracyCheck { expr: Expr },
}

enum Expr {
    Const(f64),
    Var(String),
    Mul(Box<Expr>, Box<Expr>),
    Add(Box<Expr>, Box<Expr>),
    Div(Box<Expr>, Box<Expr>),
    Pow(Box<Expr>, Box<Expr>),
    // etc.
}
```

**Ventaja del IR:** permite aplicar optimizaciones independientemente del lenguaje de origen o destino.

---

## ANEXO 2: EL FRONTEND — ANÁLISIS SINTÁCTICO Y SEMÁNTICO

### 2.1 Parser (basado en `nom`)

El parser convierte el código fuente en un AST usando combinadores de `nom`, una librería de parsing en Rust.

```rust
use nom::{
    IResult,
    bytes::complete::tag,
    character::complete::{alpha1, digit1, space0, multispace0},
    sequence::{delimited, preceded, tuple},
    combinator::{map, opt},
    multi::{many0, separated_list0},
};

fn parse_system(input: &str) -> IResult<&str, ASTNode> {
    let (input, _) = tag("system")(input)?;
    let (input, _) = space0(input)?;
    let (input, name) = alpha1(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = tag("=")(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = tag("{")(input)?;
    let (input, parts) = parse_parts(input)?;
    let (input, resource) = parse_resource(input)?;
    let (input, agents) = parse_agents(input)?;
    let (input, params) = parse_params_extended(input)?;
    let (input, _) = tag("}")(input)?;

    Ok((input, ASTNode::System { name: name.to_string(), parts, resource, agents, params }))
}

fn parse_params_extended(input: &str) -> IResult<&str, Params> {
    let (input, _) = tag("params")(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = tag(":")(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = tag("{")(input)?;
    // ... parsear campos extendidos
    Ok((input, Params { /* ... */ }))
}
```

### 2.2 Validador semántico extendido

El validador recorre el AST y comprueba:
- Todas las frecuencias suman 1.
- `phi` y `psi` en [0,1].
- `alpha` en [0.5, 2.5].
- `gamma` en [0,1].
- `sigma` en [0,0.5].
- Número de partes >= 2.
- Las variables referenciadas están definidas.
- Los tipos son correctos.
- **Nuevo en 1.1:** Coherencia `model` ↔ parámetros.

Si alguna comprobación falla, el compilador emite un error con la posición exacta en el código fuente.

### 2.3 Cálculo de `k_min` y advertencia de coexistencia

El validador puede calcular `k_min` usando la fórmula de coexistencia:

$$k_{min} = S \cdot \frac{\max_i \Phi_i \Psi_i}{\min_j \Phi_j \Psi_j} \cdot \frac{1}{\ln(S / \delta)}$$

Si `k_actual < k_min`, el compilador emite una **advertencia** (no un error, porque podría ser intencionado en algunos casos).

### 2.4 Diagnóstico de degeneración (nuevo en 1.1)

El validador puede calcular el rango de Ω y el estado de degeneración K–α:

```rust
fn validate_degeneracy(system: &System) -> DegeneracyState {
    let omegas: Vec<f64> = system.agents.iter().map(|a| a.frequency).collect();
    let orders = omega_range_orders(&omegas);
    let K_free = system.params.K.is_finite();
    let alpha_h_free = system.params.alpha_h != 1.0;

    degeneracy_state(orders, K_free, alpha_h_free)
}
```

---

## ANEXO 3: EL IR — REPRESENTACIÓN INTERMEDIA DE SISTEMAS

### 3.1 Estructura detallada del IR

El IR de RONIN no es un simple árbol; es un **grafo de dependencias** donde cada ecuación está conectada a las que la usan. Esto permite optimizaciones como el plegado de constantes o la eliminación de variables muertas.

```rust
struct IRGraph {
    nodes: Vec<IRNode>,
    edges: Vec<(usize, usize)>,
    constants: HashMap<String, f64>,
    commands: Vec<Command>,
}

enum IRNode {
    Const(f64),
    Var(String, Type),
    Add(usize, usize),
    Mul(usize, usize),
    Div(usize, usize),
    Pow(usize, f64),
    Hill(usize, usize, usize),   // nuevo 1.1
    CES(usize, usize, usize, f64, usize),  // nuevo 1.1
}
```

### 3.2 Ejemplo de IR para el sistema de 2 máquinas

```ronin
system Maquinas = {
    parts: 2,
    resource: 100,
    agents: [
        { phi: 0.8, psi: 1.0, frequency: 0.6 },
        { phi: 0.5, psi: 1.0, frequency: 0.4 }
    ],
    params: { model: "pusfre", alpha: 1.0, gamma: 0.4, sigma: 0.1 }
}
```

El IR sería:

```rust
// Constantes
c0 = 0.8
c1 = 1.0
c2 = 0.6
c3 = 0.5
c4 = 0.4
c5 = 1.0    // alpha
c6 = 0.4    // gamma
c7 = 0.1    // sigma

// Variables
phi_0 = c0
psi_0 = c1
freq_0 = c2
phi_1 = c3
psi_1 = c4
freq_1 = 1.0 - c2

// Fitness (model = "pusfre" → CES con lambda → 0)
fitness_0 = phi_0 * psi_0 * pow(freq_0, c5)
fitness_1 = phi_1 * psi_1 * pow(freq_1, c5)

// Asignación
allocation_0 = 100 * fitness_0 / (fitness_0 + fitness_1)
allocation_1 = 100 * fitness_1 / (fitness_0 + fitness_1)
```

### 3.3 Ejemplo de IR para CES-Saturada

```ronin
system MaquinasCES = {
    parts: 2,
    resource: 100,
    agents: [
        { phi: 0.8, psi: 1.0, frequency: 0.6 },
        { phi: 0.5, psi: 1.0, frequency: 0.4 }
    ],
    params: { model: "ces_hill", lambda: 0.5, K: 0.5, alpha_h: 1.5, alpha: 1.0 }
}
```

El IR añade los pasos Hill y CES:

```rust
// Paso 1: saturación Hill
omega_sat_0 = pow(freq_0, 1.5) / (pow(0.5, 1.5) + pow(freq_0, 1.5))
omega_sat_1 = pow(freq_1, 1.5) / (pow(0.5, 1.5) + pow(freq_1, 1.5))

// Paso 2: CES combine con lambda=0.5
inner_0 = (1/3)*pow(phi_0, 0.5) + (1/3)*pow(psi_0, 0.5) + (1/3)*pow(omega_sat_0, 0.5)
inner_1 = (1/3)*pow(phi_1, 0.5) + (1/3)*pow(psi_1, 0.5) + (1/3)*pow(omega_sat_1, 0.5)

fitness_0 = pow(inner_0, 2.0)  // 1/0.5
fitness_1 = pow(inner_1, 2.0)

// Asignación
allocation_0 = 100 * fitness_0 / (fitness_0 + fitness_1)
allocation_1 = 100 * fitness_1 / (fitness_0 + fitness_1)
```

### 3.4 Optimizaciones en el IR

El optimizador de IR puede aplicar transformaciones que preserven la semántica:

1. **Plegado de constantes:** `1.0 * x` → `x`.
2. **Fusión de operaciones:** `pow(x, 1.0)` → `x`.
3. **Eliminación de variables muertas:** si una variable no se usa, se elimina.
4. **Reordenación de operaciones:** para mejorar la localidad de caché.
5. **Detección de caso degenerado:** si `model = "pusfre"`, simplificar a PUSFRE clásico.
6. **Detección de caso sin saturación:** si `K = ∞`, omitir el paso Hill.

---

## ANEXO 4: EL BACKEND — GENERACIÓN DE CÓDIGO

### 4.1 Generación a código nativo (Rust)

El backend nativo propuesto generará código Rust que use la librería `ronin_core`, cuando ese backend sea implementado. El código generado es un programa completo que ejecuta `solve` y imprime el resultado.

**Objetivo:** ejecución nativa e integración con el ecosistema Rust.

### 4.2 Generación a WASM

El backend WASM previsto podrá generar un artefacto compatible con `wasm32-unknown-unknown` y exponer `solve` y `diagnose` al navegador.

**Objetivo:** ejecución en navegador mediante WASM.

### 4.3 Generación a C

El backend C previsto podrá generar C compatible con el subconjunto definido por el backend. La portabilidad concreta debe demostrarse con builds y tests sobre los objetivos soportados.

**Objetivo:** generar una variante con pocas dependencias.

### 4.4 Generación a Python

El backend Python previsto podrá generar código para integrarse con el ecosistema científico de Python.

**Objetivo:** facilitar la integración con herramientas científicas de Python.

### 4.5 Generación a LLVM IR, JVM bytecode, .NET IL y JavaScript

Estos backends están contemplados como extensiones de la arquitectura y no forman parte del conjunto mínimo obligatorio de v1.1.

---

## ANEXO 5: OPTIMIZACIONES DEL COMPILADOR

### 5.1 Simplificación de ecuaciones

El compilador simplifica automáticamente las ecuaciones antes de generar código. Por ejemplo, si `gamma = 0`, el término `(1 - gamma * psi)` se convierte en `1`.

### 5.2 Detección de invariantes

El compilador detecta invariantes (como `phi = 1` para todos los agentes) y los utiliza para simplificar el sistema.

### 5.3 Fusión de comandos

Si tienes `solve` seguido de `plot`, el compilador puede fusionarlos en una sola operación que resuelve y visualiza en un solo paso.

### 5.4 Vectorización automática

Para sistemas con muchos agentes, el compilador genera código vectorizado (usando SIMD) para acelerar las operaciones.

### 5.5 Detección de degeneración (nuevo en 1.1)

Si `model` ∈ {"ces_hill", "full"} y `degeneracy_check` está activo, el compilador inserta código de diagnóstico. Si el compilador puede determinar el rango de Ω en tiempo de compilación (por ejemplo, frecuencias literales), emite una advertencia temprana.

---

## ANEXO 6: CÓMO EXTENDER RONIN CON NUEVOS BACKENDS

### 6.1 Estructura de un backend

Un backend es un trait en Rust:

```rust
trait Backend {
    fn generate(&self, ir: &IR) -> String;
    fn target_name(&self) -> &'static str;
    fn file_extension(&self) -> &'static str;
}
```

Para añadir un nuevo backend (ej. para Go), solo necesitas implementar este trait y registrarlo en el compilador.

### 6.2 Ejemplo: backend para Go (esqueleto)

```rust
struct GoBackend;

impl Backend for GoBackend {
    fn generate(&self, ir: &IR) -> String {
        let mut code = String::new();
        code.push_str("package main\n\n");
        code.push_str("import \"fmt\"\n\n");
        code.push_str("func main() {\n");
        // Generar código para cada ecuación...
        code.push_str("}\n");
        code
    }

    fn target_name(&self) -> &'static str { "go" }
    fn file_extension(&self) -> &'static str { "go" }
}
```

### 6.3 Registro del backend

```rust
compiler.register_backend(Box::new(GoBackend));
```

---

## ANEXO 7: CÓMO AÑADIR NUEVOS TIPOS DE DOMINIO

### 7.1 Definición de un nuevo tipo

Los tipos de dominio se definen en el compilador mediante la estructura `DomainType`:

```rust
struct DomainType {
    name: String,
    base_type: BaseType,
    range: Option<Range>,
    constraints: Vec<Constraint>,
}
```

### 7.2 Ejemplo: añadir un tipo `Temperature`

```rust
let temperature = DomainType {
    name: "Temperature".to_string(),
    base_type: BaseType::Float,
    range: Some(Range { min: -273.15, max: 1e9 }),
    constraints: vec![],
};
compiler.register_type(temperature);
```

### 7.3 Añadir un tipo de la familia (nuevo en 1.1)

```rust
let lambda_type = DomainType {
    name: "Lambda".to_string(),
    base_type: BaseType::Float,
    range: Some(Range { min: -1.0, max: 2.0 }),
    constraints: vec![Constraint::NotZero],
};
compiler.register_type(lambda_type);
```

### 7.4 Validación del nuevo tipo

El validador semántico usará automáticamente la definición del tipo para comprobar que los valores están dentro del rango.

---

## ANEXO 8: CÓMO AÑADIR NUEVOS COMANDOS

### 8.1 Estructura de un comando

Los comandos se definen mediante un enum en el IR:

```rust
enum Command {
    Solve(String),
    Simulate(String, SimulateOptions),
    Audit(String, AuditOptions),
    Diagnose(String, DiagnoseOptions),  // nuevo 1.1
    Plot(String),
    MyCommand(String, MyCommandOptions),
}
```

### 8.2 Implementación del comando

La ejecución de un comando se implementa en el motor de RONIN:

```rust
fn execute_command(cmd: &Command, ir: &IR) -> Result<Value, Error> {
    match cmd {
        Command::Solve(name) => solve_system(name, ir),
        Command::Diagnose(name, opts) => diagnose_system(name, opts, ir),
        Command::MyCommand(name, opts) => my_command(name, opts, ir),
        // etc.
    }
}
```

### 8.3 Registro del comando

```rust
compiler.register_command("mycommand", my_command_handler);
```

---

## ANEXO 9: EL SISTEMA DE MACROS EN TIEMPO DE COMPILACIÓN

### 9.1 Definición de una macro

Las macros de RONIN son funciones que se ejecutan en tiempo de compilación y generan código AST.

```rust
fn macro_audit_system(args: &[ASTNode]) -> Result<ASTNode, Error> {
    let system_name = match &args[0] {
        ASTNode::System { name, .. } => name.clone(),
        _ => return Err(Error::new("se esperaba un sistema")),
    };

    Ok(ASTNode::CommandAudit {
        system: system_name,
        options: AuditOptions { epsilon: 0.05, delta: 0.01, stratified: true }
    })
}

fn macro_diagnose_and_warn(args: &[ASTNode]) -> Result<ASTNode, Error> {
    let system_name = match &args[0] {
        ASTNode::System { name, .. } => name.clone(),
        _ => return Err(Error::new("se esperaba un sistema")),
    };

    Ok(ASTNode::CommandDiagnose {
        system: system_name,
        options: DiagnoseOptions { degeneracy: true, bootstrap: 200 }
    })
}
```

### 9.2 Registro de la macro

```rust
compiler.register_macro("audit_system", macro_audit_system);
compiler.register_macro("diagnose_system", macro_diagnose_and_warn);
```

---

## ANEXO 10: CÓMO CONTRIBUIR AL COMPILADOR

### 10.1 Configuración del entorno de desarrollo

```bash
git clone https://github.com/ronin-lang/ronin-compiler
cd ronin-compiler
cargo build
cargo test
```

### 10.2 Estilo de código

- Rust estándar (usar `rustfmt`).
- Nombres en `snake_case` para variables y funciones.
- Nombres en `CamelCase` para tipos.
- Documentación de todas las funciones públicas.

### 10.3 Cómo reportar bugs

Usa el issue tracker de GitHub. Incluye:
- Versión de RONIN.
- Código fuente que causa el error.
- El mensaje de error completo.
- El resultado esperado.

---

## CIERRE FINAL DE LA PARTE IV

RONIN no es un lenguaje. Es una **máquina de ahorro de tiempo, esfuerzo y errores**.

El compilador es el motor de esa máquina. Y ahora sabes cómo funciona por dentro.

Además, ahora sabes que RONIN sirve para **videojuegos, desarrollo web, sistemas embebidos, robótica, ciencia de datos, finanzas, blockchain, recomendación, cloud, investigación científica**.

Si después de leer esto sigues usando Python para sistemas de asignación de recursos, es porque **quieres sufrir**.

**1310.**

---

*"El mejor código es el que no se escribe.
El segundo mejor es el que se escribe en RONIN.
El tercero es el que compila RONIN.
El cuarto es el que equilibra tu juego.
El quinto es el que diagnostica si la familia es identificable."*

**1310.**

---
