//! Esqueleto Rust de RONIN 1.1.
//! Las funciones marcadas con todo!() son puntos de extensión, no runtime terminado.

pub mod ast;
pub mod diagnose;
pub mod ir;
pub mod simulator;
pub mod solver;

pub use ast::{Agent, DegeneracyReport, Params, Simulation, Solution, System};
