use crate::ast::{Solution, System};

const EPS: f64 = 1e-12;
const TOL: f64 = 1e-9;

pub fn hill(omega: f64, k: f64, alpha_h: f64) -> f64 {
    if k.is_infinite() { return omega; }
    if omega < 0.0 || k <= 0.0 || alpha_h <= 0.0 || !omega.is_finite() || !k.is_finite() || !alpha_h.is_finite() {
        return f64::NAN;
    }
    if omega == 0.0 { return 0.0; }
    let x = (omega / k).powf(alpha_h);
    x / (1.0 + x)
}

pub fn ces_combine(phi: f64, psi: f64, omega_eff: f64, lambda: f64, weights: [f64; 3]) -> f64 {
    let sum: f64 = weights.iter().sum();
    if weights.iter().any(|w| !w.is_finite() || *w < 0.0) || (sum - 1.0).abs() > TOL {
        return f64::NAN;
    }
    let values = [phi.max(EPS), psi.max(EPS), omega_eff.max(EPS)];
    if lambda.abs() < 1e-6 {
        return weights.iter().zip(values).map(|(w, x)| w * x.ln()).sum::<f64>().exp();
    }
    weights.iter().zip(values).map(|(w, x)| w * x.powf(lambda)).sum::<f64>().powf(1.0 / lambda)
}

fn validate(system: &System, delta: f64) -> Result<(), String> {
    if system.parts < 2 { return Err("parts must be >= 2".into()); }
    if system.parts != system.agents.len() { return Err("parts must equal the number of agents".into()); }
    if !system.resource.is_finite() || system.resource < 0.0 { return Err("resource must be finite and non-negative".into()); }
    for (i, a) in system.agents.iter().enumerate() {
        for (name, x) in [("phi", a.phi), ("psi", a.psi), ("frequency", a.frequency)] {
            if !x.is_finite() { return Err(format!("agent {i}: {name} must be finite")); }
            if !(0.0..=1.0).contains(&x) { return Err(format!("agent {i}: {name} outside [0,1]")); }
        }
    }
    let frequency_sum: f64 = system.agents.iter().map(|a| a.frequency).sum();
    if (frequency_sum - 1.0).abs() > TOL { return Err("frequencies must sum to 1 within tolerance".into()); }
    let p = &system.params;
    for (name, x, lo, hi) in [("alpha",p.alpha,0.5,2.5),("gamma",p.gamma,0.0,1.0),("sigma",p.sigma,0.0,0.5),("coexistence_delta",p.coexistence_delta,0.0,0.1)] {
        if !x.is_finite() || x < lo || x > hi { return Err(format!("{name} outside [{lo},{hi}]")); }
    }
    if p.coexistence_delta <= 0.0 { return Err("coexistence_delta must be greater than 0".into()); }
    if !delta.is_finite() || delta <= 0.0 || delta > 0.1 { return Err("delta must be in (0,0.1]".into()); }
    if !["pusfre","ces","hill","ces_hill","full"].contains(&p.model.as_str()) { return Err(format!("unknown model: {}",p.model)); }
    if !p.lambda.is_finite() || !(-1.0..=2.0).contains(&p.lambda) { return Err("lambda outside [-1,2]".into()); }
    if !(p.k > 0.0 && (p.k.is_finite() || p.k == f64::INFINITY)) { return Err("K must be positive or inf".into()); }
    if !p.alpha_h.is_finite() || p.alpha_h <= 0.0 { return Err("alpha_h must be finite and positive".into()); }
    if ![1,2,3,5].contains(&p.memory_order) { return Err("memory_order must be one of 1, 2, 3 or 5".into()); }
    if ["pusfre","hill"].contains(&p.model.as_str()) && p.lambda.abs() > 1e-9 { return Err(format!("model \"{}\" requires lambda = 0",p.model)); }
    if ["ces","ces_hill","full"].contains(&p.model.as_str()) && p.lambda.abs() < 1e-9 { return Err(format!("model \"{}\" requires lambda != 0",p.model)); }
    if ["pusfre","ces"].contains(&p.model.as_str()) && !p.k.is_infinite() { return Err(format!("model \"{}\" requires K = inf",p.model)); }
    if ["hill","ces_hill","full"].contains(&p.model.as_str()) && !p.k.is_finite() { return Err(format!("model \"{}\" requires finite K",p.model)); }
    if p.model != "full" && p.memory_order != 1 { return Err(format!("model \"{}\" requires memory_order = 1",p.model)); }
    if p.model == "full" && p.memory_order > 1 { return Err("full temporal-memory execution is not implemented".into()); }
    if let Some(weights) = &p.memory_weights {
        if weights.len() != p.memory_order {
            return Err("memory_weights length must equal memory_order".into());
        }
        if weights.iter().any(|weight| !weight.is_finite() || *weight < 0.0) {
            return Err("memory_weights must be finite and non-negative numbers".into());
        }
        let total: f64 = weights.iter().sum();
        if (total - 1.0).abs() > TOL {
            return Err("memory_weights must sum to 1".into());
        }
    }
    Ok(())
}

pub fn validate_system(system: &System) -> Result<(), String> {
    validate(system, system.params.coexistence_delta)
}

pub fn solve(system: &System, delta: f64) -> Result<Solution, String> {
    validate(system, delta)?;
    let p = &system.params;
    let fitness: Vec<f64> = system.agents.iter().map(|a| {
        let omega = hill(a.frequency, p.k, p.alpha_h);
        if p.model == "pusfre" || p.model == "hill" {
            a.phi * a.psi * omega.powf(p.alpha)
        } else {
            ces_combine(a.phi, a.psi, omega, p.lambda, [1.0/3.0;3])
        }
    }).collect();
    if fitness.iter().any(|x| !x.is_finite() || *x < 0.0) { return Err("invalid or non-finite fitness".into()); }
    let total: f64 = fitness.iter().sum();
    let allocation = if total <= 0.0 {
        if system.resource == 0.0 { vec![0.0; fitness.len()] } else { return Err("allocation undefined: zero total fitness".into()); }
    } else { fitness.iter().map(|f| system.resource * f / total).collect() };
    let positive: Vec<f64> = system.agents.iter().map(|a|a.frequency).filter(|x|*x>0.0).collect();
    let orders = if positive.len() > 1 { (positive.iter().cloned().fold(f64::NEG_INFINITY,f64::max) / positive.iter().cloned().fold(f64::INFINITY,f64::min)).log10() } else { 0.0 };
    let k_free = !p.k.is_infinite();
    let alpha_h_free = p.alpha_h != 1.0;
    let degeneracy = if k_free && alpha_h_free && orders < 3.0 { "active" } else { "inactive" }.to_string();
    let q: Vec<f64> = system.agents.iter().map(|a|a.phi*a.psi).collect();
    let min_q = q.iter().cloned().fold(f64::INFINITY,f64::min);
    let k_min = if min_q <= 0.0 { None } else { Some(system.parts as f64 * q.iter().cloned().fold(0.0,f64::max) / min_q / ((system.parts as f64 / delta).ln())) };
    Ok(Solution {
        allocation, fitness, coexistence: k_min.map(|v|system.resource>=v), k_min,
        model_used:p.model.clone(), lambda_used:p.lambda, k_used:p.k, alpha_h_used:p.alpha_h,
        omega_range_orders:orders, degeneracy,
    })
}


#[cfg(test)]
mod tests {
    use super::{ces_combine, hill, solve};
    use crate::parser;

    const MAQUINAS: &str = include_str!("../../examples/maquinas.ronin");

    fn maquinas() -> crate::ast::System {
        parser::parse(MAQUINAS).unwrap().remove(0)
    }

    fn close(actual: f64, expected: f64, tolerance: f64) {
        assert!(
            (actual - expected).abs() <= tolerance,
            "expected {expected:.15}, got {actual:.15}"
        );
    }

    #[test]
    fn hill_identity_midpoint_and_zero_match_reference() {
        close(hill(0.5, f64::INFINITY, 1.5), 0.5, 1e-12);
        close(hill(0.5, 0.5, 1.0), 0.5, 1e-12);
        close(hill(0.0, 0.5, 1.0), 0.0, 1e-12);
    }

    #[test]
    fn ces_at_lambda_one_is_the_weighted_arithmetic_mean() {
        close(
            ces_combine(0.8, 1.0, 0.6, 1.0, [1.0 / 3.0; 3]),
            0.8,
            1e-12,
        );
    }

    #[test]
    fn maquinas_matches_normative_pusfre_fitness_and_allocation() {
        let result = solve(&maquinas(), 0.05).unwrap();
        close(result.fitness[0], 0.48, 1e-12);
        close(result.fitness[1], 0.20, 1e-12);
        close(result.allocation[0], 70.58823529411765, 1e-9);
        close(result.allocation[1], 29.411764705882355, 1e-9);
        close(result.allocation.iter().sum(), 100.0, 1e-9);
        assert_eq!(result.model_used, "pusfre");
    }

    #[test]
    fn ces_near_zero_uses_geometric_mean() {
        let mut system = maquinas();
        system.params.model = "ces".into();
        system.params.lambda = 1e-7;
        let result = solve(&system, 0.05).unwrap();

        for (index, agent) in system.agents.iter().enumerate() {
            let expected = (agent.phi * agent.psi * agent.frequency).powf(1.0 / 3.0);
            close(result.fitness[index], expected, 1e-9);
        }
        assert!((result.fitness[0] - 0.48).abs() > 1e-3);
    }

    #[test]
    fn rejects_model_parameter_incoherence() {
        let mut system = maquinas();
        system.params.lambda = 0.5;
        let error = solve(&system, 0.05).unwrap_err();
        assert!(error.contains("requires lambda = 0"));
    }

    #[test]
    fn rejects_frequency_sum_outside_tolerance() {
        let mut system = maquinas();
        system.agents[0].frequency = 0.3;
        let error = solve(&system, 0.05).unwrap_err();
        assert!(error.contains("frequencies must sum to 1"));
    }

    #[test]
    fn shared_positive_fixtures_solve_in_rust() {
        let fixtures = [
            include_str!("../../tests/fixtures/conformance/pusfre.ronin"),
            include_str!("../../tests/fixtures/conformance/ces.ronin"),
            include_str!("../../tests/fixtures/conformance/hill.ronin"),
            include_str!("../../tests/fixtures/conformance/ces_hill.ronin"),
            include_str!("../../tests/fixtures/conformance/full_order1.ronin"),
        ];
        for source in fixtures {
            let systems = parser::parse(source).unwrap();
            assert_eq!(systems.len(), 1);
            let result = solve(&systems[0], 0.05).unwrap();
            let total: f64 = result.allocation.iter().sum();
            assert!((total - systems[0].resource).abs() <= 1e-9);
            assert_eq!(result.fitness.len(), systems[0].parts);
        }
    }

    #[test]
    fn shared_negative_fixtures_are_rejected_in_rust() {
        let fixtures = [
            include_str!("../../tests/fixtures/conformance/invalid_frequency_sum.ronin"),
            include_str!("../../tests/fixtures/conformance/invalid_pusfre_lambda.ronin"),
            include_str!("../../tests/fixtures/conformance/invalid_alpha.ronin"),
            include_str!("../../tests/fixtures/conformance/full_order3_unsupported.ronin"),
        ];
        for source in fixtures {
            let systems = parser::parse(source).unwrap();
            assert!(solve(&systems[0], 0.05).is_err());
        }
    }

    #[test]
    fn rejects_invalid_memory_weight_length_and_sum() {
        let mut system = maquinas();
        system.params.memory_weights = Some(vec![0.5, 0.5]);
        let length_error = solve(&system, 0.05).unwrap_err();
        assert!(length_error.contains("memory_weights length"));

        system.params.memory_weights = Some(vec![0.5]);
        let sum_error = solve(&system, 0.05).unwrap_err();
        assert!(sum_error.contains("memory_weights must sum to 1"));
    }

    #[test]
    fn rejects_unimplemented_higher_order_temporal_memory() {
        let mut system = maquinas();
        system.params.model = "full".into();
        system.params.lambda = 0.5;
        system.params.k = 0.5;
        system.params.memory_order = 3;
        let error = solve(&system, 0.05).unwrap_err();
        assert!(error.contains("temporal-memory execution is not implemented"));
    }
}
