use crate::ast::{DegeneracyReport, System};

pub fn omega_range_orders(system: &System) -> f64 {
    todo!("Calcular log10(max(Omega)/min(Omega))")
}

pub fn diagnose(system: &System, bootstrap: usize) -> Result<DegeneracyReport, String> {
    todo!("Validar e informar degeneración e identificabilidad por parámetro")
}
