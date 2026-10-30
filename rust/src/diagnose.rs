use crate::ast::{DegeneracyReport, System};
use crate::solver::solve;

pub fn omega_range_orders(system: &System) -> f64 {
    let values: Vec<f64> = system.agents.iter().map(|a|a.frequency).filter(|x|*x>0.0).collect();
    if values.len() < 2 { return 0.0; }
    let min = values.iter().cloned().fold(f64::INFINITY,f64::min);
    let max = values.iter().cloned().fold(f64::NEG_INFINITY,f64::max);
    (max/min).log10()
}

pub fn diagnose(system: &System, _bootstrap: usize) -> Result<DegeneracyReport, String> {
    solve(system, system.params.coexistence_delta)?;
    let p = &system.params;
    let positive = system.agents.iter().filter(|a|a.frequency>0.0).count();
    let orders = omega_range_orders(system);
    let k_free = !p.k.is_infinite();
    let alpha_h_free = p.alpha_h != 1.0;
    let state = if positive < 2 { "unknown" } else if k_free && alpha_h_free && orders < 3.0 { "active" } else { "inactive" };
    let recommendation = match state {
        "unknown" => "Insufficient positive Omega observations to estimate the range or Hill identifiability.",
        "inactive" => "Structural degeneracy inactive under the configured parameter constraints.",
        _ if orders < 1.0 => "Omega spans less than one order of magnitude. K and alpha_h are indistinguishable; expand the range or fix K externally.",
        _ => "Omega spans between one and three orders of magnitude. Expand the observed Omega range to at least three orders.",
    };
    Ok(DegeneracyReport {
        omega_range_orders:orders, degeneracy:state.to_string(), lambda_identifiable:!k_free,
        k_identifiable:positive>=2 && k_free && (!alpha_h_free || orders>=3.0),
        alpha_h_identifiable:positive>=2 && k_free && alpha_h_free && orders>=3.0,
        recommendation:recommendation.to_string(),
    })
}


#[cfg(test)]
mod tests {
    use super::diagnose;
    use crate::parser;

    const MAQUINAS: &str = include_str!("../../examples/maquinas.ronin");

    fn hill_system() -> crate::ast::System {
        let mut system = parser::parse(MAQUINAS).unwrap().remove(0);
        system.params.model = "ces_hill".into();
        system.params.lambda = 0.5;
        system.params.k = 0.5;
        system.params.alpha_h = 1.5;
        system
    }

    #[test]
    fn reports_active_degeneracy_for_narrow_omega_range() {
        let system = hill_system();
        let report = diagnose(&system, 0).unwrap();
        assert_eq!(report.degeneracy, "active");
        assert!(report.omega_range_orders < 3.0);
        assert!(!report.k_identifiable);
        assert!(!report.alpha_h_identifiable);
    }

    #[test]
    fn reports_inactive_degeneracy_for_three_orders() {
        let mut system = hill_system();
        let mut third = system.agents[0].clone();
        system.agents[0].frequency = 0.0009;
        system.agents[1].frequency = 0.0090;
        third.frequency = 0.9901;
        system.agents.push(third);
        system.parts = 3;

        let report = diagnose(&system, 0).unwrap();
        assert_eq!(report.degeneracy, "inactive");
        assert!(report.omega_range_orders >= 3.0);
        assert!(report.k_identifiable);
        assert!(report.alpha_h_identifiable);
    }

    #[test]
    fn reports_unknown_when_fewer_than_two_omegas_are_positive() {
        let mut system = hill_system();
        system.agents[0].frequency = 1.0;
        system.agents[1].frequency = 0.0;

        let report = diagnose(&system, 0).unwrap();
        assert_eq!(report.degeneracy, "unknown");
        assert!(!report.k_identifiable);
        assert!(!report.alpha_h_identifiable);
    }
}
