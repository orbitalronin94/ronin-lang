use crate::ast::{Simulation, System};
use crate::solver::solve;
use std::time::{SystemTime, UNIX_EPOCH};

pub fn project_simplex(values: &[f64]) -> Vec<f64> {
    if values.is_empty() { return Vec::new(); }
    let clipped: Vec<f64> = values.iter().map(|x| x.max(0.0)).collect();
    let total: f64 = clipped.iter().sum();
    if total <= 0.0 { return vec![1.0 / values.len() as f64; values.len()]; }
    clipped.iter().map(|x| x / total).collect()
}

struct Rng { state: u64, spare: Option<f64> }
impl Rng {
    fn new(seed: u64) -> Self { Self { state: if seed == 0 { 0x9e3779b97f4a7c15 } else { seed }, spare: None } }
    fn uniform(&mut self) -> f64 {
        let mut x = self.state;
        x ^= x << 13; x ^= x >> 7; x ^= x << 17;
        self.state = x;
        ((x >> 11) as f64) / ((1u64 << 53) as f64)
    }
    fn gaussian(&mut self) -> f64 {
        if let Some(x) = self.spare.take() { return x; }
        let u1 = self.uniform().max(1e-15);
        let u2 = self.uniform();
        let radius = (-2.0 * u1.ln()).sqrt();
        let angle = std::f64::consts::TAU * u2;
        self.spare = Some(radius * angle.sin());
        radius * angle.cos()
    }
}

pub fn simulate(system: &System, steps: usize, seed: Option<u64>) -> Result<Simulation, String> {
    if steps < 1 { return Err("steps must be >= 1".into()); }
    solve(system, system.params.coexistence_delta)?;
    let actual_seed = seed.unwrap_or_else(|| SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_nanos() as u64);
    let mut rng = Rng::new(actual_seed);
    let mut state: Vec<f64> = system.agents.iter().map(|a|a.frequency).collect();
    let mut history = vec![state.clone()];
    let mut extinction_events: Vec<usize> = Vec::new();
    let alpha = system.params.alpha;
    let sigma = system.params.sigma;
    for _ in 0..steps {
        let weights: Vec<f64> = system.agents.iter().zip(state.iter()).map(|(a,x)|a.phi*a.psi*x.max(0.0).powf(alpha)).collect();
        let total: f64 = weights.iter().sum();
        let target: Vec<f64> = if total > 0.0 { weights.iter().map(|w|w/total).collect() } else { vec![1.0/state.len() as f64;state.len()] };
        let proposal: Vec<f64> = state.iter().zip(target.iter()).map(|(x,t)|x+0.5*(t-x)+rng.gaussian()*sigma/10.0).collect();
        state = project_simplex(&proposal);
        for (i,x) in state.iter().enumerate() { if *x <= 1e-12 && !extinction_events.contains(&i) { extinction_events.push(i); } }
        history.push(state.clone());
    }
    let survivors = state.iter().filter(|x|**x>1e-12).count();
    Ok(Simulation { history, final_state:state, steps, seed:Some(actual_seed), extinction_events, survivability:survivors as f64/system.agents.len() as f64 })
}


#[cfg(test)]
mod tests {
    use super::simulate;
    use crate::parser;

    const MAQUINAS: &str = include_str!("../../examples/maquinas.ronin");

    fn system() -> crate::ast::System {
        parser::parse(MAQUINAS).unwrap().remove(0)
    }

    #[test]
    fn simulation_is_reproducible_with_the_same_seed() {
        let input = system();
        let first = simulate(&input, 12, Some(42)).unwrap();
        let second = simulate(&input, 12, Some(42)).unwrap();
        assert_eq!(first, second);
    }

    #[test]
    fn every_simulated_state_stays_on_the_simplex() {
        let result = simulate(&system(), 20, Some(7)).unwrap();
        assert_eq!(result.history.len(), 21);
        for state in &result.history {
            assert!(state.iter().all(|value| value.is_finite()));
            assert!(state.iter().all(|value| *value >= 0.0));
            let total: f64 = state.iter().sum();
            assert!((total - 1.0).abs() <= 1e-12);
        }
    }

    #[test]
    fn simulation_rejects_zero_steps() {
        let error = simulate(&system(), 0, Some(1)).unwrap_err();
        assert!(error.contains("steps must be >= 1"));
    }
}
