use crate::ast::{Simulation, System};
use crate::solver::validate_system;
use std::time::{SystemTime, UNIX_EPOCH};

pub fn project_simplex(values: &[f64]) -> Vec<f64> {
    if values.is_empty() { return Vec::new(); }
    let clipped: Vec<f64> = values.iter().map(|x| x.max(0.0)).collect();
    let total: f64 = clipped.iter().sum();
    if total <= 0.0 { return vec![1.0 / values.len() as f64; values.len()]; }
    clipped.iter().map(|x| x / total).collect()
}

struct Rng {
    state: [u32; 624],
    index: usize,
    spare: Option<f64>,
}

impl Rng {
    fn new(seed: u64) -> Self {
        // CPython random.Random(int) feeds the absolute integer as little-endian
        // 32-bit words into MT19937's init_by_array routine.
        let low = seed as u32;
        let high = (seed >> 32) as u32;
        let key = if high == 0 { vec![low] } else { vec![low, high] };
        let mut state = [0u32; 624];
        state[0] = 19650218;
        for i in 1..624 {
            state[i] = 1812433253u32
                .wrapping_mul(state[i - 1] ^ (state[i - 1] >> 30))
                .wrapping_add(i as u32);
        }

        let mut i = 1usize;
        let mut j = 0usize;
        for _ in 0..624.max(key.len()) {
            state[i] = (state[i]
                ^ ((state[i - 1] ^ (state[i - 1] >> 30)).wrapping_mul(1664525)))
                .wrapping_add(key[j])
                .wrapping_add(j as u32);
            i += 1;
            j += 1;
            if i >= 624 {
                state[0] = state[623];
                i = 1;
            }
            if j >= key.len() {
                j = 0;
            }
        }

        for _ in 0..623 {
            state[i] = (state[i]
                ^ ((state[i - 1] ^ (state[i - 1] >> 30)).wrapping_mul(1566083941)))
                .wrapping_sub(i as u32);
            i += 1;
            if i >= 624 {
                state[0] = state[623];
                i = 1;
            }
        }
        state[0] = 0x80000000;

        Self {
            state,
            index: 624,
            spare: None,
        }
    }

    fn next_u32(&mut self) -> u32 {
        const UPPER_MASK: u32 = 0x80000000;
        const LOWER_MASK: u32 = 0x7fffffff;
        const MATRIX_A: u32 = 0x9908b0df;
        const N: usize = 624;
        const M: usize = 397;

        if self.index >= N {
            for i in 0..N {
                let y = (self.state[i] & UPPER_MASK)
                    | (self.state[(i + 1) % N] & LOWER_MASK);
                self.state[i] = self.state[(i + M) % N]
                    ^ (y >> 1)
                    ^ if y & 1 == 0 { 0 } else { MATRIX_A };
            }
            self.index = 0;
        }

        let mut y = self.state[self.index];
        self.index += 1;
        y ^= y >> 11;
        y ^= (y << 7) & 0x9d2c5680;
        y ^= (y << 15) & 0xefc60000;
        y ^= y >> 18;
        y
    }

    fn uniform(&mut self) -> f64 {
        let a = (self.next_u32() >> 5) as u64;
        let b = (self.next_u32() >> 6) as u64;
        ((a << 26) + b) as f64 / 9007199254740992.0
    }

    fn gaussian(&mut self) -> f64 {
        if let Some(value) = self.spare.take() {
            return value;
        }
        // Same polar-free Box-Muller sequence and cache as random.Random.gauss.
        let angle = self.uniform() * std::f64::consts::TAU;
        let radius = (-2.0 * (1.0 - self.uniform()).ln()).sqrt();
        self.spare = Some(angle.sin() * radius);
        angle.cos() * radius
    }
}

pub fn simulate(system: &System, steps: usize, seed: Option<u64>) -> Result<Simulation, String> {
    if steps < 1 { return Err("steps must be >= 1".into()); }
    validate_system(system)?;
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
        let proposal: Vec<f64> = state.iter().zip(target.iter()).map(|(x,t)|x+0.5*(t-x)+rng.gaussian()*(sigma/10.0)).collect();
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
    #[test]
    fn simulation_handles_valid_zero_fitness_with_uniform_fallback() {
        let source = include_str!("../../tests/fixtures/conformance/valid_zero_fitness_check_only.ronin");
        let system = parser::parse(source).unwrap().remove(0);
        let result = simulate(&system, 4, Some(11)).unwrap();
        assert_eq!(result.history.len(), 5);
        for state in result.history {
            assert!((state[0] - 0.5).abs() <= 1e-12);
            assert!((state[1] - 0.5).abs() <= 1e-12);
        }
    }

    #[test]
    fn rng_matches_cpython_random_and_gauss_reference_vectors() {
        let mut random = super::Rng::new(42);
        assert!((random.uniform() - 0.6394267984578837).abs() <= 1e-16);

        let mut gaussian = super::Rng::new(42);
        assert!((gaussian.gaussian() - -0.14409032957792836).abs() <= 1e-15);
    }

}
