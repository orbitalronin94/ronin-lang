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
    Ok(())
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
