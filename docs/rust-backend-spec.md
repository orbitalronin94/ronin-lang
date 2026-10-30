# Parte VI — Implementación en Rust

> Especificación de referencia transcrita desde la fuente 1.1. La presencia de código en esta documentación no implica que el crate del repositorio ya implemente todas las funciones: el estado ejecutable se describe en `rust/README.md`.

ronin/
├── Cargo.toml
├── crates/
│   ├── ronin-core/               # Núcleo: AST, IR, solver, simulator, diagnose
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── lib.rs
│   │       ├── ast.rs
│   │       ├── ir.rs
│   │       ├── solver.rs
│   │       ├── simulator.rs
│   │       ├── validator.rs
│   │       ├── diagnose.rs
│   │       └── optimizer.rs
│   ├── ronin-parser/             # Lexer + parser con nom
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── lib.rs
│   │       ├── lexer.rs
│   │       └── parser.rs
│   ├── ronin-cli/                # CLI con clap
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── main.rs
│   ├── ronin-wasm/               # Backend WASM
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── lib.rs
│   ├── ronin-c-backend/          # Backend C
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── lib.rs
│   └── ronin-pyo3/               # Bindings Python
│       ├── Cargo.toml
│       └── src/
│           └── lib.rs
├── tests/
│   ├── test_maquinas.rs
│   ├── test_pesca.rs
│   ├── test_family.rs
│   └── test_invalid.rs
├── examples/
│   ├── maquinas.ronin
│   ├── pesca.ronin
│   ├── neural_scaling.ronin
│   └── rpg_balance.ronin
└── benches/
    └── solver_bench.rs
```

### Cargo.toml principal

```toml
[workspace]
resolver = "2"
members = [
    "crates/ronin-core",
    "crates/ronin-parser",
    "crates/ronin-cli",
    "crates/ronin-wasm",
    "crates/ronin-c-backend",
    "crates/ronin-pyo3",
]

[workspace.package]
version = "1.1.0"
edition = "2021"
license = "MIT OR Apache-2.0"
repository = "https://github.com/ronin-lang/ronin"

[workspace.dependencies]
ronin-core = { path = "crates/ronin-core", version = "1.1.0" }
ronin-parser = { path = "crates/ronin-parser", version = "1.1.0" }
nom = "7.1"
thiserror = "1.0"
clap = { version = "4.5", features = ["derive"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
rand = "0.8"
rand_chacha = "0.3"
pyo3 = { version = "0.21", features = ["extension-module"] }
wasm-bindgen = "0.2"
```

---

## 6.2 AST (ABSTRACT SYNTAX TREE)

### `crates/ronin-core/src/ast.rs`

```rust
//! Abstract Syntax Tree for RONIN 1.1

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Agent {
    pub phi: f64,
    pub psi: f64,
    pub frequency: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
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

impl Default for Params {
    fn default() -> Self {
        Params {
            alpha: 1.0,
            gamma: 0.4,
            sigma: 0.0,
            coexistence_delta: 0.05,
            model: "pusfre".to_string(),
            lambda: 0.0,
            K: f64::INFINITY,
            alpha_h: 1.0,
            memory_order: 1,
            memory_weights: None,
            degeneracy_check: false,
            omega_range_report: false,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct System {
    pub name: String,
    pub parts: usize,
    pub resource: f64,
    pub agents: Vec<Agent>,
    pub params: Params,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Solution {
    pub allocation: Vec<f64>,
    pub fitness: Vec<f64>,
    pub coexistence: Option<bool>,
    pub k_min: Option<f64>,
    pub debt: f64,
    pub convergence: bool,
    pub steps: usize,
    // Nuevos en 1.1
    pub model_used: String,
    pub lambda_used: f64,
    pub K_used: f64,
    pub alpha_h_used: f64,
    pub omega_range: f64,
    pub degeneracy: String,
    pub warnings: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DegeneracyReport {
    pub omega_range_orders: f64,
    pub degeneracy: String,
    pub lambda_identifiable: bool,
    pub K_identifiable: bool,
    pub alpha_h_identifiable: bool,
    pub recommendation: String,
    pub bootstrap_ci: Option<serde_json::Value>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Simulation {
    pub history: Vec<Vec<f64>>,
    pub final_state: Vec<f64>,
    pub steps: usize,
    pub seed: Option<u64>,
    pub extinction_events: Vec<usize>,
    pub survivability: f64,
}
```

---

## 6.3 LEXER EN RUST

*(Sin cambios respecto a 1.0. El lexer es estándar.)*

---

## 6.4 PARSER CON NOM EXTENDIDO

### `crates/ronin-parser/src/parser.rs`

```rust
use nom::{
    IResult,
    bytes::complete::tag,
    character::complete::{alpha1, digit1, multispace0, space0},
    combinator::{opt, recognize},
    multi::{many0, separated_list0},
    sequence::tuple,
};
use ronin_core::ast::{Agent, Params, System};

pub fn parse(source: &str) -> Result<Vec<System>, String> {
    let (remaining, systems) = parse_program(source)
        .map_err(|e| format!("Parse error: {}", e))?;
    if !remaining.trim().is_empty() {
        return Err(format!("Unexpected tokens: {}", remaining));
    }
    Ok(systems)
}

fn parse_program(input: &str) -> IResult<&str, Vec<System>> {
    many0(parse_system)(input)
}

fn parse_system(input: &str) -> IResult<&str, System> {
    let (input, _) = tag("system")(input)?;
    let (input, _) = space0(input)?;
    let (input, name) = alpha1(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = tag("=")(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = tag("{")(input)?;
    let (input, _) = multispace0(input)?;

    let (input, parts) = parse_parts(input)?;
    let (input, _) = multispace0(input)?;
    let (input, resource) = parse_resource(input)?;
    let (input, _) = multispace0(input)?;
    let (input, agents) = parse_agents(input)?;
    let (input, _) = multispace0(input)?;
    let (input, params) = parse_params(input)?;
    let (input, _) = multispace0(input)?;
    let (input, _) = tag("}")(input)?;

    Ok((input, System {
        name: name.to_string(),
        parts,
        resource,
        agents,
        params,
    }))
}

fn parse_parts(input: &str) -> IResult<&str, usize> {
    let (input, _) = tag("parts")(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = tag(":")(input)?;
    let (input, _) = space0(input)?;
    let (input, n) = digit1(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = opt(tag(","))(input)?;
    Ok((input, n.parse().unwrap()))
}

fn parse_resource(input: &str) -> IResult<&str, f64> {
    let (input, _) = tag("resource")(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = tag(":")(input)?;
    let (input, _) = space0(input)?;
    let (input, n) = recognize(tuple((opt(tag("-")), digit1, opt(tuple((tag("."), digit1))))))(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = opt(tag(","))(input)?;
    Ok((input, n.parse().unwrap()))
}

fn parse_agents(input: &str) -> IResult<&str, Vec<Agent>> {
    let (input, _) = tag("agents")(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = tag(":")(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = tag("[")(input)?;
    let (input, _) = multispace0(input)?;
    let (input, agents) = separated_list0(tag(","), parse_agent)(input)?;
    let (input, _) = multispace0(input)?;
    let (input, _) = tag("]")(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = opt(tag(","))(input)?;
    Ok((input, agents))
}

fn parse_agent(input: &str) -> IResult<&str, Agent> {
    let (input, _) = tag("{")(input)?;
    let (input, _) = multispace0(input)?;
    let (input, fields) = many0(parse_field)(input)?;
    let (input, _) = multispace0(input)?;
    let (input, _) = tag("}")(input)?;

    let mut phi = 0.0;
    let mut psi = 0.0;
    let mut frequency = 0.0;

    for (k, v) in fields {
        match k.as_str() {
            "phi" => phi = v,
            "psi" => psi = v,
            "frequency" => frequency = v,
            _ => {}
        }
    }

    Ok((input, Agent { phi, psi, frequency }))
}

fn parse_field(input: &str) -> IResult<&str, (String, f64)> {
    let (input, key) = alpha1(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = tag(":")(input)?;
    let (input, _) = space0(input)?;
    let (input, value) = recognize(tuple((opt(tag("-")), digit1, opt(tuple((tag("."), digit1))))))(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = opt(tag(","))(input)?;
    Ok((input, (key.to_string(), value.parse().unwrap())))
}

fn parse_params(input: &str) -> IResult<&str, Params> {
    let (input, _) = tag("params")(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = tag(":")(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = tag("{")(input)?;
    let (input, _) = multispace0(input)?;
    let (input, fields) = many0(parse_field)(input)?;
    let (input, _) = multispace0(input)?;
    let (input, _) = tag("}")(input)?;
    let (input, _) = space0(input)?;
    let (input, _) = opt(tag(","))(input)?;

    let mut params = Params::default();

    for (k, v) in fields {
        match k.as_str() {
            "alpha" => params.alpha = v,
            "gamma" => params.gamma = v,
            "sigma" => params.sigma = v,
            "coexistence_delta" => params.coexistence_delta = v,
            "lambda" => params.lambda = v,
            "K" => params.K = v,
            "alpha_h" => params.alpha_h = v,
            _ => {}
        }
    }

    Ok((input, params))
}
```

*(Nota: El parser extendido maneja strings para `model` en producción completa. Este es un esqueleto funcional.)*

---

## 6.5 VALIDADOR SEMÁNTICO EXTENDIDO

### `crates/ronin-core/src/validator.rs`

```rust
use thiserror::Error;
use super::ast::{Params, System};

#[derive(Error, Debug)]
pub enum ValidationError {
    #[error("parts must be >= 2 (got {0})")]
    TooFewParts(usize),
    #[error("parts ({0}) does not match number of agents ({1})")]
    PartCountMismatch(usize, usize),
    #[error("resource must be non-negative (got {0})")]
    NegativeResource(f64),
    #[error("agent {0}: phi outside [0,1] (got {1})")]
    PhiOutOfRange(usize, f64),
    #[error("agent {0}: psi outside [0,1] (got {1})")]
    PsiOutOfRange(usize, f64),
    #[error("agent {0}: frequency outside [0,1] (got {1})")]
    FrequencyOutOfRange(usize, f64),
    #[error("frequencies sum to {0}, expected 1 (tolerance {1})")]
    FrequencySum(f64, f64),
    #[error("alpha outside [0.5, 2.5] (got {0})")]
    AlphaOutOfRange(f64),
    #[error("gamma outside [0, 1] (got {0})")]
    GammaOutOfRange(f64),
    #[error("sigma outside [0, 0.5] (got {0})")]
    SigmaOutOfRange(f64),
    #[error("model coherence violation: {0}")]
    ModelCoherence(String),
}

pub fn validate(system: &System, tolerance: f64) -> Result<(), ValidationError> {
    if system.parts < 2 {
        return Err(ValidationError::TooFewParts(system.parts));
    }
    if system.parts != system.agents.len() {
        return Err(ValidationError::PartCountMismatch(system.parts, system.agents.len()));
    }
    if system.resource < 0.0 {
        return Err(ValidationError::NegativeResource(system.resource));
    }

    for (i, agent) in system.agents.iter().enumerate() {
        if !(0.0..=1.0).contains(&agent.phi) {
            return Err(ValidationError::PhiOutOfRange(i, agent.phi));
        }
        if !(0.0..=1.0).contains(&agent.psi) {
            return Err(ValidationError::PsiOutOfRange(i, agent.psi));
        }
        if !(0.0..=1.0).contains(&agent.frequency) {
            return Err(ValidationError::FrequencyOutOfRange(i, agent.frequency));
        }
    }

    let sum: f64 = system.agents.iter().map(|a| a.frequency).sum();
    if (sum - 1.0).abs() > tolerance {
        return Err(ValidationError::FrequencySum(sum, tolerance));
    }

    let p = &system.params;
    if !(0.5..=2.5).contains(&p.alpha) {
        return Err(ValidationError::AlphaOutOfRange(p.alpha));
    }
    if !(0.0..=1.0).contains(&p.gamma) {
        return Err(ValidationError::GammaOutOfRange(p.gamma));
    }
    if !(0.0..=0.5).contains(&p.sigma) {
        return Err(ValidationError::SigmaOutOfRange(p.sigma));
    }

    Ok(())
}

pub fn validate_coherence(params: &Params) -> Result<(), ValidationError> {
    let m = params.model.as_str();
    let lam = params.lambda;
    let K = params.K;
    let k = params.memory_order;

    match m {
        "pusfre" => {
            if lam.abs() > 1e-9 {
                return Err(ValidationError::ModelCoherence(
                    "model \"pusfre\" requires lambda = 0".to_string()));
            }
            if K.is_finite() {
                return Err(ValidationError::ModelCoherence(
                    "model \"pusfre\" requires K = inf".to_string()));
            }
            if k != 1 {
                return Err(ValidationError::ModelCoherence(
                    "model \"pusfre\" requires memory_order = 1".to_string()));
            }
        }
        "ces" => {
            if lam.abs() < 1e-9 {
                return Err(ValidationError::ModelCoherence(
                    "model \"ces\" requires lambda != 0".to_string()));
            }
            if K.is_finite() {
                return Err(ValidationError::ModelCoherence(
                    "model \"ces\" requires K = inf".to_string()));
            }
            if k != 1 {
                return Err(ValidationError::ModelCoherence(
                    "model \"ces\" requires memory_order = 1".to_string()));
            }
        }
        "hill" => {
            if lam.abs() > 1e-9 {
                return Err(ValidationError::ModelCoherence(
                    "model \"hill\" requires lambda = 0".to_string()));
            }
            if !K.is_finite() {
                return Err(ValidationError::ModelCoherence(
                    "model \"hill\" requires finite K".to_string()));
            }
            if k != 1 {
                return Err(ValidationError::ModelCoherence(
                    "model \"hill\" requires memory_order = 1".to_string()));
            }
        }
        "ces_hill" => {
            if lam.abs() < 1e-9 {
                return Err(ValidationError::ModelCoherence(
                    "model \"ces_hill\" requires lambda != 0".to_string()));
            }
            if !K.is_finite() {
                return Err(ValidationError::ModelCoherence(
                    "model \"ces_hill\" requires finite K".to_string()));
            }
            if k != 1 {
                return Err(ValidationError::ModelCoherence(
                    "model \"ces_hill\" requires memory_order = 1".to_string()));
            }

        }
        "full" => {
            if lam.abs() < 1e-9 {
                return Err(ValidationError::ModelCoherence(
                    "model \"full\" requires lambda != 0".to_string()));
            }
            if !K.is_finite() {
                return Err(ValidationError::ModelCoherence(
                    "model \"full\" requires finite K".to_string()));
            }
        }
        _ => {
            return Err(ValidationError::ModelCoherence(
                format!("unknown model: {}", m)));
        }
    }

    Ok(())
}
```

---

## 6.6 IR

*(Sin cambios estructurales. Se añaden nodos para Hill y CES.)*

---

## 6.7 SOLVER EXTENDIDO

### `crates/ronin-core/src/solver.rs`

```rust
use super::ast::{System, Params};
use super::validator::{validate, validate_coherence, ValidationError};

const EPS: f64 = 1e-12;

#[derive(Debug, thiserror::Error)]
pub enum SolverError {
    #[error("validation error: {0}")]
    Validation(#[from] ValidationError),
    #[error("fitness sum is zero, system is degenerate")]
    ZeroFitness,
}

pub fn hill(omega: f64, K: f64, alpha_h: f64) -> f64 {
    if !K.is_finite() {
        return omega;
    }
    omega.powf(alpha_h) / (K.powf(alpha_h) + omega.powf(alpha_h))
}

pub fn ces_combine(phi: f64, psi: f64, omega_eff: f64, lam: f64, w: [f64; 3]) -> f64 {
    let phi = phi.max(EPS);
    let psi = psi.max(EPS);
    let omega_eff = omega_eff.max(EPS);

    if lam.abs() < 1e-6 {
        return phi.powf(w[0]) * psi.powf(w[1]) * omega_eff.powf(w[2]);
    }
    let inner = w[0]*phi.powf(lam) + w[1]*psi.powf(lam) + w[2]*omega_eff.powf(lam);
    inner.powf(1.0/lam)
}

pub fn solve(system: &System, delta: f64) -> Result<super::ast::Solution, SolverError> {
    validate(system, 1e-9)?;
    validate_coherence(&system.params)?;

    let p = &system.params;
    let fitness: Vec<f64> = system.agents.iter()
        .map(|a| {
            let omega_eff = hill(a.frequency, p.K, p.alpha_h);
            ces_combine(a.phi, a.psi, omega_eff, p.lambda, [1.0/3.0, 1.0/3.0, 1.0/3.0])
        })
        .collect();

    let total: f64 = fitness.iter().sum();
    if total <= 0.0 {
        return Err(SolverError::ZeroFitness);
    }

    let allocation: Vec<f64> = fitness.iter()
        .map(|f| system.resource * f / total)
        .collect();

    let k_min = calculate_k_min(system, delta);
    let coexistence = k_min.map(|km| system.resource >= km);
    let omega_range = omega_range_orders(&system.agents);

    let K_free = p.K.is_finite();
    let alpha_h_free = (p.alpha_h - 1.0).abs() > 1e-9;
    let degeneracy = degeneracy_state(omega_range, K_free, alpha_h_free);

    let mut warnings = vec![];
    if degeneracy == "active" {
        warnings.push(format!(
            "K–α_h degeneracy active (Ω range = {:.2f} orders). \
             K and alpha_h are not independently identifiable.",
            omega_range
        ));
    }

    Ok(super::ast::Solution {
        allocation,
        fitness,
        coexistence,
        k_min,
        debt: 0.0,
        convergence: true,
        steps: 1,
        model_used: p.model.clone(),
        lambda_used: p.lambda,
        K_used: p.K,
        alpha_h_used: p.alpha_h,
        omega_range,
        degeneracy,
        warnings,
    })
}

fn omega_range_orders(agents: &[super::ast::Agent]) -> f64 {
    let omegas: Vec<f64> = agents.iter()
        .map(|a| a.frequency)
        .filter(|&x| x > 0.0)
        .collect();
    if omegas.len() < 2 {
        return 0.0;
    }
    let max_o = omegas.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let min_o = omegas.iter().cloned().fold(f64::INFINITY, f64::min);
    (max_o / min_o).log10()
}

fn degeneracy_state(omega_range: f64, K_free: bool, alpha_h_free: bool) -> String {
    if !K_free || !alpha_h_free {
        return "inactive".to_string();
    }
    if omega_range >= 3.0 {
        "inactive".to_string()
    } else {
        "active".to_string()
    }
}

fn calculate_k_min(system: &System, delta: f64) -> Option<f64> {
    let products: Vec<f64> = system.agents.iter()
        .map(|a| a.phi * a.psi)
        .collect();
    let min_product = products.iter().cloned().fold(f64::INFINITY, f64::min);
    let max_product = products.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    if min_product <= 0.0 || delta <= 0.0 || delta >= system.parts as f64 {
        return None;
    }
    let s = system.parts as f64;
    Some(s * (max_product / min_product) / (s / delta).ln())
}
```

---

## 6.8 SIMULADOR

*(Sin cambios respecto a 1.0. Se añade validate_coherence.)*

---

## 6.9 DIAGNÓSTICO EN RUST

### `crates/ronin-core/src/diagnose.rs`

```rust
use super::ast::{DegeneracyReport, System};
use super::validator::{validate, validate_coherence};

pub fn diagnose(system: &System, bootstrap: usize) -> Result<DegeneracyReport, String> {
    validate(system, 1e-9).map_err(|e| e.to_string())?;
    validate_coherence(&system.params).map_err(|e| e.to_string())?;

    let omegas: Vec<f64> = system.agents.iter()
        .map(|a| a.frequency)
        .filter(|&x| x > 0.0)
        .collect();

    let orders = if omegas.len() < 2 {
        0.0
    } else {
        let max_o = omegas.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        let min_o = omegas.iter().cloned().fold(f64::INFINITY, f64::min);
        (max_o / min_o).log10()
    };

    let K_free = system.params.K.is_finite();
    let alpha_h_free = (system.params.alpha_h - 1.0).abs() > 1e-9;

    let degeneracy = if !K_free || !alpha_h_free {
        "inactive"
    } else if orders >= 3.0 {
        "inactive"
    } else {
        "active"
    };

    let recommendation = match degeneracy {
        "inactive" => "Identificación estructural OK. K y α_h son estimables por separado.",
        _ if orders < 1.0 => "Ω cubre < 1 orden de magnitud. K y α_h son indistinguibles. \
                              Recolectar datos con Ω en un rango mayor o fijar K externamente.",
        _ => "Ω cubre entre 1 y 3 órdenes. Degeneración K–α activa. \
              Se recomienda ampliar el rango de Ω a ≥ 3 órdenes.",
    };

    Ok(DegeneracyReport {
        omega_range_orders: orders,
        degeneracy: degeneracy.to_string(),
        lambda_identifiable: true,
        K_identifiable: degeneracy == "inactive",
        alpha_h_identifiable: degeneracy == "inactive",
        recommendation: recommendation.to_string(),
        bootstrap_ci: None,
    })
}
```

---

## 6.10 CLI CON CLAP EXTENDIDA

### `crates/ronin-cli/src/main.rs`

```rust
use clap::{Parser, Subcommand};
use std::fs;
use std::path::PathBuf;

use ronin_core::solver::solve;
use ronin_core::simulator::simulate;
use ronin_core::diagnose::diagnose;
use ronin_core::validator::validate;
use ronin_parser::parser::parse;

const TOLERANCE: f64 = 1e-9;
const DELTA: f64 = 0.05;

#[derive(Parser)]
#[command(name = "ronin")]
#[command(version = "1.1.0")]
#[command(about = "RONIN — The Language of Finite Systems")]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    Check { file: PathBuf },
    Solve { file: PathBuf, #[arg(long, default_value_t = 0.05)] delta: f64 },
    Simulate {
        file: PathBuf,
        #[arg(long, default_value_t = 100)] steps: usize,
        #[arg(long)] seed: Option<u64>,
    },
    Diagnose {
        file: PathBuf,
        #[arg(long, default_value_t = 0)] bootstrap: usize,
    },
}

fn main() -> Result<(), String> {
    let cli = Cli::parse();

    match cli.command {
        Command::Check { file } => {
            let source = fs::read_to_string(&file)
                .map_err(|e| format!("Cannot read file: {}", e))?;
            let systems = parse(&source).map_err(|e| format!("Parse error: {}", e))?;
            let system = systems.first().ok_or("No system declaration found")?;
            validate(system, TOLERANCE)
                .map_err(|e| format!("Validation error: {}", e))?;
            println!("OK");
            Ok(())
        }
        Command::Solve { file, delta } => {
            let source = fs::read_to_string(&file)
                .map_err(|e| format!("Cannot read file: {}", e))?;
            let systems = parse(&source).map_err(|e| format!("Parse error: {}", e))?;
            let system = systems.first().ok_or("No system declaration found")?;
            let solution = solve(system, delta).map_err(|e| format!("Solver error: {}", e))?;
            let json = serde_json::to_string_pretty(&solution).map_err(|e| e.to_string())?;
            println!("{}", json);
            Ok(())
        }
        Command::Simulate { file, steps, seed } => {
            let source = fs::read_to_string(&file)
                .map_err(|e| format!("Cannot read file: {}", e))?;
            let systems = parse(&source).map_err(|e| format!("Parse error: {}", e))?;
            let system = systems.first().ok_or("No system declaration found")?;
            let sim = simulate(system, steps, seed).map_err(|e| e.to_string())?;
            let json = serde_json::to_string_pretty(&sim).map_err(|e| e.to_string())?;
            println!("{}", json);
            Ok(())
        }
        Command::Diagnose { file, bootstrap } => {
            let source = fs::read_to_string(&file)
                .map_err(|e| format!("Cannot read file: {}", e))?;
            let systems = parse(&source).map_err(|e| format!("Parse error: {}", e))?;
            let system = systems.first().ok_or("No system declaration found")?;
            let report = diagnose(system, bootstrap).map_err(|e| e)?;
            let json = serde_json::to_string_pretty(&report).map_err(|e| e.to_string())?;
            println!("{}", json);
            Ok(())
        }
    }
}
```

---

## 6.11 TESTS NORMATIVOS EN RUST

*(Se mantienen los tests de 1.0 + tests de la familia.)*

```rust
#[cfg(test)]
mod family_tests {
    use ronin_core::solver::solve;
    use ronin_core::diagnose::diagnose;
    use ronin_core::validator::{validate, validate_coherence};
    use ronin_parser::parser::parse;
    use approx::assert_relative_eq;

    const TOLERANCE: f64 = 1e-9;

    #[test]
    fn test_compatibility_1_0() {
        let src = r#"
        system Maquinas = {
            parts: 2, resource: 100,
            agents: [
                { phi: 0.8, psi: 1.0, frequency: 0.6 },
                { phi: 0.5, psi: 1.0, frequency: 0.4 }
            ],
            params: { alpha: 1.0, gamma: 0.4, sigma: 0.1 }
        }
        "#;
        let systems = parse(src).unwrap();
        let s = solve(&systems[0], 0.05).unwrap();
        assert_relative_eq!(s.allocation[0], 70.58823529411765, epsilon = TOLERANCE);
        assert_eq!(s.model_used, "pusfre");
    }

    #[test]
    fn test_model_coherence_violation() {
        let src = r#"
        system M = {
            parts: 2, resource: 100,
            agents: [
                { phi: 0.8, psi: 1.0, frequency: 0.6 },
                { phi: 0.5, psi: 1.0, frequency: 0.4 }
            ],
            params: { model: "pusfre", lambda: 0.5 }
        }
        "#;
        let systems = parse(src).unwrap();
        let result = validate_coherence(&systems[0].params);
        assert!(result.is_err());
    }

    #[test]
    fn test_degeneracy_active() {
        let src = r#"
        system M = {
            parts: 3, resource: 100,
            agents: [
                { phi: 0.5, psi: 0.5, frequency: 0.3 },
                { phi: 0.5, psi: 0.5, frequency: 0.4 },
                { phi: 0.5, psi: 0.5, frequency: 0.3 }
            ],
            params: { model: "ces_hill", lambda: 0.5, K: 0.5, alpha_h: 1.5 }
        }
        "#;
        let systems = parse(src).unwrap();
        let report = diagnose(&systems[0], 0).unwrap();
        assert_eq!(report.degeneracy, "active");
    }

    #[test]
    fn test_degeneracy_inactive() {
        let src = r#"
        system M = {
            parts: 3, resource: 100,
            agents: [
                { phi: 0.5, psi: 0.5, frequency: 0.001 },
                { phi: 0.5, psi: 0.5, frequency: 0.01 },
                { phi: 0.5, psi: 0.5, frequency: 0.989 }            ],
            params: { model: "ces_hill", lambda: 0.5, K: 0.5, alpha_h: 1.5 }
        }
        "#;
        let systems = parse(src).unwrap();
        let report = diagnose(&systems[0], 0).unwrap();
        assert_eq!(report.degeneracy, "inactive");
        assert!(report.omega_range_orders >= 3.0);
    }
}
```

---

## 6.12 INTEGRACIÓN CON PYTHON (PYO3)

*(Sin cambios estructurales. Se añade `diagnose_file`.)*

```rust
#[pyfunction]
fn diagnose_file(file_path: &str) -> PyResult<String> {
    let source = std::fs::read_to_string(file_path)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let systems = parse(&source)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
    let system = systems.first()
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("No system declaration found"))?;
    let report = diagnose(system, 0)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e))?;
    Ok(serde_json::to_string(&report).unwrap_or_default())
}
```

---

## 6.13 BACKEND A WASM

*(Sin cambios estructurales. Se añade `diagnose_ronin`.)*

```rust
#[wasm_bindgen]
pub fn diagnose_ronin(source: &str) -> String {
    match parse(source) {
        Ok(systems) => {
            if let Some(system) = systems.first() {
                match diagnose(system, 0) {
                    Ok(report) => serde_json::to_string(&report).unwrap_or_default(),
                    Err(e) => format!("Error: {}", e),
                }
            } else {
                "Error: No system found".to_string()
            }
        }
        Err(e) => format!("Parse error: {}", e),
    }
}
```

---

## 6.14 BACKEND A C

*(Sin cambios estructurales. Se añade generación de código para Hill y CES.)*

```rust
pub fn generate_c(system: &System) -> String {
    let mut code = String::new();
    code.push_str("#include <stdio.h>\n");
    code.push_str("#include <math.h>\n\n");

    // ... constantes y variables

    // Saturación Hill
    if system.params.K.is_finite() {
        code.push_str(&format!(
            "double hill(double omega, double K, double alpha_h) {{\n\
                return pow(omega, alpha_h) / (pow(K, alpha_h) + pow(omega, alpha_h));\n\
            }}\n\n"
        ));
    }

    // CES combine
    code.push_str(
        "double ces_combine(double phi, double psi, double omega_eff, double lam) {\n\
            if (fabs(lam) < 1e-6) {\n\
                return pow(phi, 1.0/3.0) * pow(psi, 1.0/3.0) * pow(omega_eff, 1.0/3.0);\n\
            }\n\
            double inner = (1.0/3.0)*pow(phi, lam) + (1.0/3.0)*pow(psi, lam) + (1.0/3.0)*pow(omega_eff, lam);\n\
            return pow(inner, 1.0/lam);\n\
        }\n\n"
    );

    // ... resto del main
    code
}
```

---

# PARTE VII — RONIN OFFICE: INTERFAZ VISUAL

## 7.1 VISIÓN GENERAL

RONIN Office es una interfaz visual para diseñar, resolver y simular sistemas RONIN sin necesidad de escribir código. Es una herramienta de productividad que permite a arquitectos, diseñadores y analistas trabajar con RONIN de forma visual.

**Principios operativos:**