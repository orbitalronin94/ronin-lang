//! Rust runtime for RONIN 1.1. The parser currently implements the core
//! numeric project syntax; optional metadata and temporal-memory execution
//! remain explicit limitations.

pub mod ast;
pub mod diagnose;
pub mod ir;
pub mod parser;
pub mod simulator;
pub mod solver;

pub use ast::{Agent, DegeneracyReport, Params, Simulation, Solution, System};
