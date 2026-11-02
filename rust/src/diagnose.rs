use crate::ast::{DegeneracyReport, System};
use crate::solver::validate_system;

pub fn omega_range_orders(system: &System) -> f64 {
    let values: Vec<f64> = system.agents.iter().map(|a| a.frequency).filter(|x| *x > 0.0).collect();
    if values.len() < 2 { return 0.0; }
    let min = values.iter().cloned().fold(f64::INFINITY, f64::min);
    let max = values.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    (max / min).log10()
}

pub fn diagnose(system: &System, bootstrap: usize) -> Result<DegeneracyReport, String> {
    validate_system(system)?;
    if bootstrap > 0 {
        return Err("bootstrap is not implemented; use bootstrap=0".into());
    }
    let p = &system.params;
    let positive = system.agents.iter().filter(|a| a.frequency > 0.0).count();
    let orders = omega_range_orders(system);
    let k_free = !p.k.is_infinite();
    let alpha_h_free = p.alpha_h != 1.0;
    let state = if positive < 2 { "unknown" } else if k_free && alpha_h_free && orders < 3.0 { "active" } else { "inactive" };
    let recommendation = match state {
        "unknown" => "Insufficient positive Omega observations to estimate the range or Hill identifiability.",
        "inactive" => "Structural degeneracy inactive under the configured parameter constraints.",
        _ if orders < 1.0 => "Omega spans less than one order of magnitude. K and alpha_h are weakly separated by this range heuristic; expand the Omega range or fix K externally.",
        _ => "Omega spans between one and three orders of magnitude. Expand the observed Omega range to at least three orders.",
    };
    Ok(DegeneracyReport {
        omega_range_orders: orders,
        degeneracy: state.to_string(),
        lambda_identifiable: !k_free,
        k_identifiable: positive >= 2 && k_free && (!alpha_h_free || orders >= 3.0),
        alpha_h_identifiable: positive >= 2 && k_free && alpha_h_free && orders >= 3.0,
        recommendation: recommendation.to_string(),
        structural_status: "not_assessed".into(),
        practical_status: "not_calibrated".into(),
        estimability_status: "not_assessed".into(),
        diagnostic_method: "omega_range_heuristic".into(),
        parameter_freedom_basis: "legacy_value_heuristic".into(),
    })
}

#[cfg(test)]
mod tests {
    use super::diagnose;
    use crate::parser;

    #[test]
    fn shared_diagnostic_fixtures_match_expected_states() {
        let cases = [
            (include_str!("../../tests/fixtures/conformance/degeneracy_active.ronin"), "active"),
            (include_str!("../../tests/fixtures/conformance/degeneracy_inactive.ronin"), "inactive"),
            (include_str!("../../tests/fixtures/conformance/degeneracy_unknown.ronin"), "unknown"),
        ];
        for (source, expected) in cases {
            let system = parser::parse(source).unwrap().remove(0);
            let report = diagnose(&system, 0).unwrap();
            assert_eq!(report.degeneracy, expected);
            assert_eq!(report.structural_status, "not_assessed");
            assert_eq!(report.practical_status, "not_calibrated");
            assert_eq!(report.estimability_status, "not_assessed");
            assert_eq!(report.diagnostic_method, "omega_range_heuristic");
            assert_eq!(report.parameter_freedom_basis, "legacy_value_heuristic");
        }
    }
    #[test]
    fn recommendations_do_not_overclaim_global_structural_identifiability() {
        let active_source = include_str!("../../tests/fixtures/conformance/degeneracy_active.ronin");
        let inactive_source = include_str!("../../tests/fixtures/conformance/degeneracy_inactive.ronin");
        let active = parser::parse(active_source).unwrap().remove(0);
        let inactive = parser::parse(inactive_source).unwrap().remove(0);
        let active_report = diagnose(&active, 0).unwrap();
        let inactive_report = diagnose(&inactive, 0).unwrap();
        assert!(active_report.recommendation.contains("weakly separated"));
        assert!(inactive_report.recommendation.contains("global structural identifiability"));
        assert_eq!(active_report.structural_status, "not_assessed");
        assert_eq!(inactive_report.structural_status, "not_assessed");
    }

    #[test]
    fn unsupported_bootstrap_is_rejected_explicitly() {
        let source = include_str!("../../examples/maquinas.ronin");
        let system = parser::parse(source).unwrap().remove(0);
        let error = diagnose(&system, 50).unwrap_err();
        assert!(error.contains("bootstrap is not implemented"));
    }

    #[test]
    fn diagnosis_does_not_require_positive_total_fitness() {
        let source = include_str!("../../tests/fixtures/conformance/valid_zero_fitness_check_only.ronin");
        let system = parser::parse(source).unwrap().remove(0);
        let report = diagnose(&system, 0).unwrap();
        assert_eq!(report.degeneracy, "inactive");
        assert!(report.lambda_identifiable);
    }

}
