use crate::ast::{DegeneracyReport, System};
use crate::solver::solve;

pub fn omega_range_orders(system: &System) -> f64 {
    let values: Vec<f64> = system.agents.iter().map(|a| a.frequency).filter(|x| *x > 0.0).collect();
    if values.len() < 2 { return 0.0; }
    let min = values.iter().cloned().fold(f64::INFINITY, f64::min);
    let max = values.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    (max / min).log10()
}

pub fn diagnose(system: &System, _bootstrap: usize) -> Result<DegeneracyReport, String> {
    solve(system, system.params.coexistence_delta)?;
    let p = &system.params;
    let positive = system.agents.iter().filter(|a| a.frequency > 0.0).count();
    let orders = omega_range_orders(system);
    let k_free = !p.k.is_infinite();
    let alpha_h_free = p.alpha_h != 1.0;
    let state = if positive < 2 { "unknown" } else if k_free && alpha_h_free && orders < 3.0 { "active" } else { "inactive" };
    let recommendation = match state {
        "unknown" => "Insufficient positive Omega observations to estimate the range or Hill identifiability.",
        "inactive" => "Structural degeneracy inactive under the configured parameter constraints.",
        _ if orders < 1.0 => "Omega spans less than one order of magnitude. K and alpha_h are indistinguishable; expand the Omega range or fix K externally.",
        _ => "Omega spans between one and three orders of magnitude. Expand the observed Omega range to at least three orders.",
    };
    Ok(DegeneracyReport {
        omega_range_orders: orders,
        degeneracy: state.to_string(),
        lambda_identifiable: !k_free,
        k_identifiable: positive >= 2 && k_free && (!alpha_h_free || orders >= 3.0),
        alpha_h_identifiable: positive >= 2 && k_free && alpha_h_free && orders >= 3.0,
        recommendation: recommendation.to_string(),
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
            assert_eq!(diagnose(&system, 0).unwrap().degeneracy, expected);
        }
    }
}
