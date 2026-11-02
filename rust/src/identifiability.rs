//! Local pre-fit Fisher-information diagnostics for Hill experimental designs.
//!
//! A local FIM is not a proof of global structural identifiability.

#[derive(Clone, Debug, PartialEq)]
pub struct HillDesignDiagnostic {
    pub observations: usize,
    pub omega_range_orders: f64,
    pub saturation_fraction: f64,
    pub max_omega_over_k: f64,
    pub singular_values: [f64; 2],
    pub fim_condition_number: f64,
    pub local_rank: usize,
    pub local_rank_status: String,
    pub weak_direction: [f64; 2],
    pub typical_parameters: [f64; 2],
    pub relative_tolerance: f64,
    pub saturation_ratio: f64,
    pub structural_status: String,
    pub practical_status: String,
    pub estimability_status: String,
    pub parameterization: String,
    pub noise_model: String,
    pub assumptions: Vec<String>,
    pub warnings: Vec<String>,
}

/// Evaluate the local Hill design information in dimensionless coordinates
/// (log(K), log(alpha_h)) under independent homoscedastic additive Gaussian
/// noise on the Hill response.
pub fn diagnose_hill_design(
    omega: &[f64],
    k: f64,
    alpha_h: f64,
    sigma: f64,
    relative_tolerance: f64,
    saturation_ratio: f64,
) -> Result<HillDesignDiagnostic, String> {
    if !k.is_finite() || k <= 0.0 {
        return Err("K must be a finite positive number".into());
    }
    if !alpha_h.is_finite() || alpha_h <= 0.0 {
        return Err("alpha_h must be a finite positive number".into());
    }
    if !sigma.is_finite() || sigma <= 0.0 {
        return Err("sigma must be a finite positive number".into());
    }
    if !relative_tolerance.is_finite()
        || relative_tolerance <= 0.0
        || relative_tolerance >= 1.0
    {
        return Err("relative_tolerance must be finite and in (0,1)".into());
    }
    if !saturation_ratio.is_finite() || saturation_ratio <= 0.0 {
        return Err("saturation_ratio must be finite and positive".into());
    }
    if omega.is_empty() {
        return Err("omega must contain at least one observation".into());
    }
    if omega.iter().any(|value| !value.is_finite() || *value <= 0.0) {
        return Err("omega values must be finite positive numbers".into());
    }

    let sigma_squared = sigma * sigma;
    if sigma_squared == 0.0 || !sigma_squared.is_finite() {
        return Err("sigma is outside the stable Fisher information range".into());
    }
    let inv_sigma_squared = 1.0 / sigma_squared;
    if !inv_sigma_squared.is_finite() {
        return Err("sigma is outside the stable Fisher information range".into());
    }

    let log_k = k.ln();
    let log_saturation_ratio = saturation_ratio.ln();
    let mut fim_kk = 0.0;
    let mut fim_ka = 0.0;
    let mut fim_aa = 0.0;
    let mut saturated = 0usize;
    let mut max_log_ratio = f64::NEG_INFINITY;

    for value in omega {
        let log_ratio = value.ln() - log_k;
        let z = alpha_h * log_ratio;
        let hill_value = if z >= 0.0 {
            let exp_neg = if z < 746.0 { (-z).exp() } else { 0.0 };
            1.0 / (1.0 + exp_neg)
        } else {
            let exp_pos = if z > -746.0 { z.exp() } else { 0.0 };
            exp_pos / (1.0 + exp_pos)
        };

        let slope_factor = alpha_h * hill_value * (1.0 - hill_value);
        let derivative_log_k = -slope_factor;
        let derivative_log_alpha = slope_factor * log_ratio;
        fim_kk += derivative_log_k * derivative_log_k * inv_sigma_squared;
        fim_ka += derivative_log_k * derivative_log_alpha * inv_sigma_squared;
        fim_aa += derivative_log_alpha * derivative_log_alpha * inv_sigma_squared;

        max_log_ratio = max_log_ratio.max(log_ratio);
        if log_ratio >= log_saturation_ratio {
            saturated += 1;
        }
    }

    if !fim_kk.is_finite() || !fim_ka.is_finite() || !fim_aa.is_finite() {
        return Err("Fisher information overflow; increase sigma or rescale the design".into());
    }

    let trace = fim_kk + fim_aa;
    let discriminant = (fim_kk - fim_aa).hypot(2.0 * fim_ka);
    let eigen_max = (0.5 * (trace + discriminant)).max(0.0);
    let eigen_min = (0.5 * (trace - discriminant)).max(0.0);

    let (rank, condition, singular_values, weak_direction) = if eigen_max == 0.0 {
        (0, f64::INFINITY, [0.0, 0.0], [0.0, 1.0])
    } else {
        let rank = if eigen_min <= relative_tolerance * eigen_max { 1 } else { 2 };
        let condition = if rank < 2 { f64::INFINITY } else { eigen_max / eigen_min };
        let angle = 0.5 * (2.0 * fim_ka).atan2(fim_kk - fim_aa);
        (
            rank,
            condition,
            [eigen_max.sqrt(), eigen_min.sqrt()],
            [-angle.sin(), angle.cos()],
        )
    };

    let min_omega = omega.iter().cloned().fold(f64::INFINITY, f64::min);
    let max_omega = omega.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let omega_range_orders = max_omega.log10() - min_omega.log10();
    let max_omega_over_k = if max_log_ratio < 709.0 {
        max_log_ratio.exp()
    } else {
        f64::INFINITY
    };

    let mut warnings = Vec::new();
    if max_omega_over_k < saturation_ratio {
        warnings.push(
            "All design points are below the configured saturation ratio Ω/K; K and alpha_h may be strongly confounded.".into(),
        );
    }
    if rank < 2 {
        warnings.push(
            "The local information matrix is numerically rank deficient at the supplied typical parameter values.".into(),
        );
    }

    Ok(HillDesignDiagnostic {
        observations: omega.len(),
        omega_range_orders,
        saturation_fraction: saturated as f64 / omega.len() as f64,
        max_omega_over_k,
        singular_values,
        fim_condition_number: condition,
        local_rank: rank,
        local_rank_status: if rank == 2 { "full_rank" } else { "rank_deficient" }.into(),
        weak_direction,
        typical_parameters: [k, alpha_h],
        relative_tolerance,
        saturation_ratio,
        structural_status: "not_assessed".into(),
        practical_status: "not_calibrated".into(),
        estimability_status: "not_assessed".into(),
        parameterization: "log(K), log(alpha_h)".into(),
        noise_model: "independent homoscedastic additive Gaussian noise on Hill response".into(),
        assumptions: vec![
            "local linearization at supplied typical parameters".into(),
            "Hill response is the observation mean".into(),
            "independent observations with constant variance sigma^2".into(),
            "local FIM rank is not a global structural-identifiability proof".into(),
        ],
        warnings,
    })
}

#[cfg(test)]
mod tests {
    use super::diagnose_hill_design;

    #[test]
    fn broad_hill_design_has_full_local_rank() {
        let omega: Vec<f64> = (0..=40)
            .map(|index| 10f64.powf(-2.0 + index as f64 * 0.1))
            .collect();
        let report = diagnose_hill_design(&omega, 1.0, 1.5, 0.05, 1e-12, 0.1).unwrap();
        assert_eq!(report.local_rank, 2);
        assert!(report.fim_condition_number.is_finite());
        assert_eq!(report.structural_status, "not_assessed");
        assert_eq!(report.practical_status, "not_calibrated");
    }

    #[test]
    fn one_observation_has_rank_at_most_one() {
        let report = diagnose_hill_design(&[0.5], 1.0, 1.5, 0.05, 1e-12, 0.1).unwrap();
        assert_eq!(report.local_rank, 1);
        assert!(report.fim_condition_number.is_infinite());
    }

    #[test]
    fn sub_saturated_design_is_reported_without_global_claim() {
        let report = diagnose_hill_design(
            &[0.001, 0.002, 0.004, 0.008],
            1.0,
            1.5,
            0.05,
            1e-12,
            0.1,
        )
        .unwrap();
        assert!(report.max_omega_over_k < 0.1);
        assert_eq!(report.saturation_fraction, 0.0);
        assert_eq!(report.structural_status, "not_assessed");
        assert!(!report.warnings.is_empty());
    }

    #[test]
    fn common_omega_and_k_scaling_preserves_information() {
        let first =
            diagnose_hill_design(&[0.01, 0.1, 1.0, 10.0], 1.0, 1.5, 0.05, 1e-12, 0.1)
                .unwrap();
        let scaled =
            diagnose_hill_design(&[10.0, 100.0, 1000.0, 10000.0], 1000.0, 1.5, 0.05, 1e-12, 0.1)
                .unwrap();
        for index in 0..2 {
            assert!((first.singular_values[index] - scaled.singular_values[index]).abs() < 1e-10);
        }
        assert!((first.fim_condition_number - scaled.fim_condition_number).abs() < 1e-8);
    }

    #[test]
    fn rejects_invalid_design_inputs() {
        assert!(diagnose_hill_design(&[0.1, 1.0], 0.0, 1.5, 0.05, 1e-12, 0.1).is_err());
        assert!(diagnose_hill_design(&[0.1, 1.0], 1.0, 0.0, 0.05, 1e-12, 0.1).is_err());
        assert!(diagnose_hill_design(&[0.1, 1.0], 1.0, 1.5, 0.0, 1e-12, 0.1).is_err());
        assert!(diagnose_hill_design(&[0.1, f64::NAN], 1.0, 1.5, 0.05, 1e-12, 0.1).is_err());
    }
}
