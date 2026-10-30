use crate::ast::{Simulation, System};

pub fn project_simplex(values: &[f64]) -> Vec<f64> {
    todo!("Proyectar un vector al símplex")
}

pub fn simulate(system: &System, steps: usize, seed: Option<u64>) -> Result<Simulation, String> {
    todo!("Implementar kernel R.10 con RNG reproducible")
}
