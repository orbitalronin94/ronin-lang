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

fn logdet_positive_definite(matrix: &[Vec<f64>]) -> Result<f64, String> {
    let size = matrix.len();
    let mut lower = vec![vec![0.0; size]; size];
    for row in 0..size {
        for column in 0..=row {
            let mut value = matrix[row][column];
            for index in 0..column {
                value -= lower[row][index] * lower[column][index];
            }
            if row == column {
                if !value.is_finite() || value <= 0.0 {
                    return Err("regularized information matrix is not positive definite".into());
                }
                lower[row][column] = value.sqrt();
            } else {
                lower[row][column] = value / lower[column][column];
            }
        }
    }
    let log_determinant = 2.0 * (0..size).map(|index| lower[index][index].ln()).sum::<f64>();
    if !log_determinant.is_finite() {
        return Err("D-optimal log determinant is outside the supported numeric range".into());
    }
    Ok(log_determinant)
}

/// Greedily select candidate observation rows by normalized D-optimality.
///
/// The ridge is dimensionless and the returned score is only comparable
/// under the same parameterization, scales, weights and ridge. This is not
/// a structural-identifiability certificate.
pub fn d_optimal_design(
    jacobian: &[Vec<f64>],
    n_samples: usize,
    weights: Option<&[f64]>,
    parameter_names: Option<&[String]>,
    parameter_scales: Option<&[f64]>,
    relative_tolerance: f64,
    ridge: f64,
) -> Result<DOptimalDesign, String> {
    if n_samples == 0 || n_samples > jacobian.len() {
        return Err("n_samples must be between 1 and the number of candidates".into());
    }
    if !ridge.is_finite() || ridge <= 0.0 {
        return Err("ridge must be finite and positive".into());
    }
    // Reuse the public diagnostic to enforce the same matrix, weight, name,
    // scale and tolerance contract.
    diagnose_jacobian(
        jacobian, weights, parameter_names, parameter_scales, relative_tolerance,
    )?;

    let rows = jacobian.len();
    let columns = jacobian[0].len();
    let observation_weights = weights.map_or_else(|| vec![1.0; rows], |values| values.to_vec());
    let scales = parameter_scales.map_or_else(|| vec![1.0; columns], |values| values.to_vec());

    let mut weighted_rows = Vec::with_capacity(rows);
    let mut jacobian_scale = 0.0f64;
    for (row, weight) in jacobian.iter().zip(observation_weights.iter()) {
        let root_weight = weight.sqrt();
        let weighted: Vec<f64> = row.iter().zip(scales.iter())
            .map(|(value, scale)| value * root_weight * scale)
            .collect();
        if weighted.iter().any(|value| !value.is_finite()) {
            return Err("weighted/scaled Jacobian overflow; rescale inputs".into());
        }
        jacobian_scale = weighted.iter().fold(jacobian_scale, |largest, value| largest.max(value.abs()));
        weighted_rows.push(weighted);
    }

    let normalized_rows: Vec<Vec<f64>> = weighted_rows.iter().map(|row| {
        if jacobian_scale > 0.0 {
            row.iter().map(|value| value / jacobian_scale).collect()
        } else {
            vec![0.0; columns]
        }
    }).collect();

    let mut information = vec![vec![0.0; columns]; columns];
    let mut selected = Vec::with_capacity(n_samples);
    for _ in 0..n_samples {
        let mut best_index = None;
        let mut best_score = f64::NEG_INFINITY;
        for candidate in 0..rows {
            if selected.contains(&candidate) {
                continue;
            }
            let mut trial = information.clone();
            for left in 0..columns {
                for right in 0..columns {
                    trial[left][right] += normalized_rows[candidate][left] * normalized_rows[candidate][right];
                }
                trial[left][left] += ridge;
            }
            let score = logdet_positive_definite(&trial)?;
            if score > best_score {
                best_score = score;
                best_index = Some(candidate);
            }
        }
        let chosen = best_index.ok_or_else(|| "no remaining design candidates".to_string())?;
        selected.push(chosen);
        for left in 0..columns {
            for right in 0..columns {
                information[left][right] += normalized_rows[chosen][left] * normalized_rows[chosen][right];
            }
        }
    }

    let mut final_regularized = information.clone();
    for index in 0..columns {
        final_regularized[index][index] += ridge;
    }
    let log_determinant = logdet_positive_definite(&final_regularized)?;
    let selected_rows: Vec<Vec<f64>> = selected.iter().map(|index| jacobian[*index].clone()).collect();
    let selected_weights: Vec<f64> = selected.iter().map(|index| observation_weights[*index]).collect();
    let local_information = diagnose_jacobian(
        &selected_rows,
        Some(&selected_weights),
        parameter_names,
        Some(&scales),
        relative_tolerance,
    )?;

    Ok(DOptimalDesign {
        selected_indices: selected,
        log_determinant,
        normalized_information_matrix: information,
        jacobian_scale,
        ridge,
        local_information,
    })
}

/// Compute first-order Saltelli indices from precomputed A, B and A_B^i outputs.
///
/// This computes first-order effects only. It does not generate parameter
/// samples and does not estimate second-order interactions.
pub fn sobol_first_order(
    f_a: &[f64],
    f_b: &[f64],
    f_ab: &[Vec<f64>],
) -> Result<SobolFirstOrderDiagnostic, String> {
    if f_a.len() < 2 || f_b.len() != f_a.len() {
        return Err("f_a and f_b must have the same length of at least two".into());
    }
    if f_ab.is_empty() {
        return Err("f_ab must contain at least one parameter row".into());
    }
    if f_a.iter().chain(f_b.iter()).any(|value| !value.is_finite())
        || f_ab.iter().flatten().any(|value| !value.is_finite())
    {
        return Err("Sobol outputs must contain only finite numbers".into());
    }
    if f_ab.iter().any(|row| row.len() != f_a.len()) {
        return Err("each f_ab row must match the sample count".into());
    }

    let output_scale = f_a.iter()
        .chain(f_b.iter())
        .chain(f_ab.iter().flatten())
        .fold(0.0f64, |largest, value| largest.max(value.abs()));
    if output_scale == 0.0 {
        return Err("Sobol output variance is zero".into());
    }

    let normalized_a: Vec<f64> = f_a.iter().map(|value| value / output_scale).collect();
    let normalized_b: Vec<f64> = f_b.iter().map(|value| value / output_scale).collect();
    let normalized_ab: Vec<Vec<f64>> = f_ab.iter().map(|row| {
        row.iter().map(|value| value / output_scale).collect()
    }).collect();
    let sample_count = f_a.len();
    let pooled_mean = normalized_a.iter().chain(normalized_b.iter()).sum::<f64>()
        / (2 * sample_count) as f64;
    let variance = normalized_a.iter().chain(normalized_b.iter())
        .map(|value| (value - pooled_mean) * (value - pooled_mean))
        .sum::<f64>() / (2 * sample_count) as f64;
    if !variance.is_finite() || variance <= 0.0 {
        return Err("Sobol output variance is zero or numerically unresolved".into());
    }

    let first_order_indices: Vec<f64> = normalized_ab.iter().map(|hybrid| {
        normalized_a.iter()
            .zip(normalized_b.iter())
            .zip(hybrid.iter())
            .map(|((a, b), ab)| b * (ab - a))
            .sum::<f64>() / (sample_count as f64 * variance)
    }).collect();
    if first_order_indices.iter().any(|value| !value.is_finite()) {
        return Err("Sobol estimator exceeded the supported numeric range".into());
    }

    Ok(SobolFirstOrderDiagnostic {
        sample_count,
        parameter_count: normalized_ab.len(),
        first_order_indices,
        output_scale,
        output_variance_normalized: variance,
        estimator: "Saltelli first-order estimator with pooled A/B population variance".into(),
        assumptions: vec![
            "A and B are independent samples from the declared parameter distributions".into(),
            "each f_ab row is evaluated on the matching A_B^i hybrid sample matrix".into(),
            "indices are first-order estimates and do not include interaction effects".into(),
            "finite-sample estimates are not clipped to [0,1]".into(),
        ],
    })
}

/// Select Hill observation levels for local information on log(K), log(alpha_h).
///
/// The observation model assumes additive homoscedastic Gaussian noise. Since
/// sigma is common to all candidates, it does not affect the selected subset;
/// the underlying D-optimal score is normalized and dimensionless.
pub fn d_optimal_hill_design(
    omega_candidates: &[f64],
    n_samples: usize,
    k: f64,
    alpha_h: f64,
    sigma: f64,
    relative_tolerance: f64,
    ridge: f64,
) -> Result<HillDOptimalDesign, String> {
    if omega_candidates.is_empty() {
        return Err("omega_candidates must be a non-empty numeric sequence".into());
    }
    for (name, value) in [("K", k), ("alpha_h", alpha_h), ("sigma", sigma)] {
        if !value.is_finite() || value <= 0.0 {
            return Err(format!("{name} must be finite and positive"));
        }
    }
    if omega_candidates.iter().any(|value| !value.is_finite() || *value <= 0.0) {
        return Err("all omega_candidates must be finite and positive".into());
    }

    let mut jacobian = Vec::with_capacity(omega_candidates.len());
    for omega in omega_candidates {
        let log_ratio = omega.ln() - k.ln();
        let z = alpha_h * log_ratio;
        let (derivative_log_k, derivative_log_alpha) = if !z.is_finite() || z.abs() > 745.0 {
            (0.0, 0.0)
        } else {
            let tail = (-z.abs()).exp();
            let slope = tail / ((1.0 + tail) * (1.0 + tail));
            (-alpha_h * slope, z * slope)
        };
        if !derivative_log_k.is_finite() || !derivative_log_alpha.is_finite() {
            return Err("Hill sensitivity exceeds the supported numeric range".into());
        }
        jacobian.push(vec![derivative_log_k, derivative_log_alpha]);
    }

    let names = vec!["log_K".to_string(), "log_alpha_h".to_string()];
    let design = d_optimal_design(
        &jacobian, n_samples, None, Some(&names), None, relative_tolerance, ridge,
    )?;
    let selected_omega: Vec<f64> = design.selected_indices.iter()
        .map(|index| omega_candidates[*index])
        .collect();
    let warnings = if design.local_information.local_rank < 2 {
        vec!["selected Hill observations do not provide full local rank for log(K) and log(alpha_h)".into()]
    } else {
        Vec::new()
    };

    Ok(HillDOptimalDesign {
        selected_indices: design.selected_indices.clone(),
        selected_omega,
        candidate_count: omega_candidates.len(),
        k,
        alpha_h,
        sigma,
        design,
        warnings,
    })
}

#[cfg(test)]
mod tests {
    use super::{d_optimal_design, d_optimal_hill_design, diagnose_hill_design, sobol_first_order};

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


#[derive(Clone, Debug, PartialEq)]
pub struct LocalInformationDiagnostic {
    pub observations: usize,
    pub parameters: usize,
    pub parameter_names: Vec<String>,
    pub parameter_scales: Vec<f64>,
    pub singular_values: Vec<f64>,
    pub fim_condition_number: f64,
    pub local_rank: usize,
    pub local_rank_status: String,
    pub weak_directions: Vec<Vec<f64>>,
    pub relative_tolerance: f64,
    pub structural_status: String,
    pub practical_status: String,
    pub estimability_status: String,
    pub noise_model: String,
    pub assumptions: Vec<String>,
}

#[derive(Clone, Debug, PartialEq)]
pub struct SIREarlyPhaseDiagnostic {
    pub local_information: LocalInformationDiagnostic,
    pub growth_rate: f64,
    pub observed_amplitude: f64,
    pub structural_status: String,
    pub assumptions: Vec<String>,
}

#[derive(Clone, Debug, PartialEq)]
pub struct DOptimalDesign {
    pub selected_indices: Vec<usize>,
    pub log_determinant: f64,
    pub normalized_information_matrix: Vec<Vec<f64>>,
    pub jacobian_scale: f64,
    pub ridge: f64,
    pub local_information: LocalInformationDiagnostic,
}

#[derive(Clone, Debug, PartialEq)]
pub struct SobolFirstOrderDiagnostic {
    pub sample_count: usize,
    pub parameter_count: usize,
    pub first_order_indices: Vec<f64>,
    pub output_scale: f64,
    pub output_variance_normalized: f64,
    pub estimator: String,
    pub assumptions: Vec<String>,
}

#[derive(Clone, Debug, PartialEq)]
pub struct HillDOptimalDesign {
    pub selected_indices: Vec<usize>,
    pub selected_omega: Vec<f64>,
    pub candidate_count: usize,
    pub k: f64,
    pub alpha_h: f64,
    pub sigma: f64,
    pub design: DOptimalDesign,
    pub warnings: Vec<String>,
}

fn symmetric_eigen(mut matrix: Vec<Vec<f64>>) -> (Vec<f64>, Vec<Vec<f64>>) {
    let size = matrix.len();
    let mut vectors = vec![vec![0.0; size]; size];
    for index in 0..size {
        vectors[index][index] = 1.0;
    }

    for _ in 0..(100 * size * size).max(1) {
        let mut p = 0usize;
        let mut q = 0usize;
        let mut largest = 0.0f64;
        for row in 0..size {
            for col in (row + 1)..size {
                let candidate = matrix[row][col].abs();
                if candidate > largest {
                    largest = candidate;
                    p = row;
                    q = col;
                }
            }
        }
        let scale = matrix
            .iter()
            .flatten()
            .map(|value| value.abs())
            .fold(0.0f64, f64::max);
        if scale == 0.0 || largest <= 1e-15 * scale {
            break;
        }

        let off_diagonal = matrix[p][q];
        let tau = (matrix[q][q] - matrix[p][p]) / (2.0 * off_diagonal);
        let tangent = if tau == 0.0 {
            1.0
        } else {
            tau.signum() / (tau.abs() + (1.0 + tau * tau).sqrt())
        };
        let cosine = 1.0 / (1.0 + tangent * tangent).sqrt();
        let sine = tangent * cosine;

        let pp = matrix[p][p];
        let qq = matrix[q][q];
        matrix[p][p] = pp - tangent * off_diagonal;
        matrix[q][q] = qq + tangent * off_diagonal;
        matrix[p][q] = 0.0;
        matrix[q][p] = 0.0;

        for index in 0..size {
            if index == p || index == q {
                continue;
            }
            let ip = matrix[index][p];
            let iq = matrix[index][q];
            matrix[index][p] = cosine * ip - sine * iq;
            matrix[p][index] = matrix[index][p];
            matrix[index][q] = sine * ip + cosine * iq;
            matrix[q][index] = matrix[index][q];
        }

        for index in 0..size {
            let vp = vectors[index][p];
            let vq = vectors[index][q];
            vectors[index][p] = cosine * vp - sine * vq;
            vectors[index][q] = sine * vp + cosine * vq;
        }
    }

    let mut pairs: Vec<(f64, Vec<f64>)> = (0..size)
        .map(|index| {
            (
                matrix[index][index],
                (0..size).map(|row| vectors[row][index]).collect(),
            )
        })
        .collect();
    pairs.sort_by(|left, right| right.0.partial_cmp(&left.0).unwrap());
    let eigenvalues = pairs.iter().map(|item| item.0).collect();
    let eigenvectors = pairs.into_iter().map(|item| item.1).collect();
    (eigenvalues, eigenvectors)
}

/// Diagnose local information from an observation-by-parameter Jacobian.
pub fn diagnose_jacobian(
    jacobian: &[Vec<f64>],
    weights: Option<&[f64]>,
    parameter_names: Option<&[String]>,
    parameter_scales: Option<&[f64]>,
    relative_tolerance: f64,
) -> Result<LocalInformationDiagnostic, String> {
    if !relative_tolerance.is_finite()
        || relative_tolerance <= 0.0
        || relative_tolerance >= 1.0
    {
        return Err("relative_tolerance must be finite and in (0,1)".into());
    }
    if jacobian.is_empty() || jacobian[0].is_empty() {
        return Err("jacobian must be a non-empty rectangular matrix".into());
    }
    let columns = jacobian[0].len();
    if jacobian.iter().any(|row| row.len() != columns) {
        return Err("jacobian rows must have equal length".into());
    }
    if jacobian.iter().flatten().any(|value| !value.is_finite()) {
        return Err("jacobian values must be finite numbers".into());
    }

    let observation_weights = match weights {
        None => vec![1.0; jacobian.len()],
        Some(values) => {
            if values.len() != jacobian.len()
                || values.iter().any(|value| !value.is_finite() || *value <= 0.0)
            {
                return Err("weights must be finite positive values, one per row".into());
            }
            values.to_vec()
        }
    };
    let scales = match parameter_scales {
        None => vec![1.0; columns],
        Some(values) => {
            if values.len() != columns
                || values.iter().any(|value| !value.is_finite() || *value <= 0.0)
            {
                return Err("parameter_scales must be finite positive values, one per column".into());
            }
            values.to_vec()
        }
    };
    let names = match parameter_names {
        None => (0..columns).map(|index| format!("parameter_{}", index + 1)).collect(),
        Some(values) => {
            if values.len() != columns
                || values.iter().any(|name| name.is_empty())
            {
                return Err("parameter_names must contain one non-empty name per column".into());
            }
            let mut unique = std::collections::HashSet::new();
            if values.iter().any(|name| !unique.insert(name.clone())) {
                return Err("parameter_names must be unique".into());
            }
            values.to_vec()
        }
    };

    // Normalize the weighted, scaled Jacobian before forming J'WJ.
    // This avoids squaring very small/large entries before the eigensolve.
    let mut weighted_rows = Vec::with_capacity(jacobian.len());
    let mut jacobian_scale = 0.0f64;
    for (row, weight) in jacobian.iter().zip(observation_weights.iter()) {
        let root_weight = weight.sqrt();
        let weighted: Vec<f64> = row
            .iter()
            .zip(scales.iter())
            .map(|(value, scale)| value * root_weight * scale)
            .collect();
        if weighted.iter().any(|value| !value.is_finite()) {
            return Err("weighted/scaled Jacobian overflow; rescale inputs".into());
        }
        jacobian_scale = weighted.iter().fold(jacobian_scale, |largest, value| largest.max(value.abs()));
        weighted_rows.push(weighted);
    }

    let mut information = vec![vec![0.0; columns]; columns];
    if jacobian_scale > 0.0 {
        for row in &weighted_rows {
            let normalized: Vec<f64> = row.iter().map(|value| value / jacobian_scale).collect();
            for left in 0..columns {
                for right in left..columns {
                    information[left][right] += normalized[left] * normalized[right];
                }
            }
        }
    }
    for left in 0..columns {
        for right in 0..left {
            information[left][right] = information[right][left];
        }
    }
    if information.iter().flatten().any(|value| !value.is_finite()) {
        return Err("Fisher information overflow after normalization".into());
    }

    let (mut eigenvalues, eigenvectors) = symmetric_eigen(information);
    let largest = eigenvalues.first().copied().unwrap_or(0.0).max(0.0);
    let negative_tolerance = relative_tolerance * largest;
    if eigenvalues.iter().any(|value| *value < -negative_tolerance) {
        return Err("computed information matrix is not positive semidefinite".into());
    }
    for value in eigenvalues.iter_mut() {
        *value = value.max(0.0);
    }

    let rank = if largest == 0.0 {
        0
    } else {
        eigenvalues.iter().filter(|value| **value > relative_tolerance * largest).count()
    };
    let condition = if rank < columns || largest == 0.0 {
        f64::INFINITY
    } else {
        largest / eigenvalues[columns - 1]
    };
    let singular_values: Vec<f64> = eigenvalues
        .iter()
        .map(|value| value.sqrt() * jacobian_scale)
        .collect();
    if singular_values.iter().any(|value| !value.is_finite()) {
        return Err("singular values exceed the supported numeric range".into());
    }
    let weak_directions: Vec<Vec<f64>> = eigenvalues
        .iter()
        .zip(eigenvectors.iter())
        .filter(|(value, _)| largest == 0.0 || **value <= relative_tolerance * largest)
        .map(|(_, vector)| vector.clone())
        .collect();

    Ok(LocalInformationDiagnostic {
        observations: jacobian.len(),
        parameters: columns,
        parameter_names: names,
        parameter_scales: scales,
        singular_values,
        fim_condition_number: condition,
        local_rank: rank,
        local_rank_status: if rank == columns { "full_rank" } else { "rank_deficient" }.into(),
        weak_directions,
        relative_tolerance,
        structural_status: "not_assessed".into(),
        practical_status: "not_calibrated".into(),
        estimability_status: "not_assessed".into(),
        noise_model: "caller-supplied independent observation precisions (diagonal W)".into(),
        assumptions: vec![
            "Jacobian evaluated at documented typical parameters".into(),
            "local linearization and supplied diagonal observation weights".into(),
            "parameter scales define dimensionless local coordinates".into(),
            "local FIM rank is not a global structural-identifiability proof".into(),
        ],
    })
}

/// Diagnose the early-phase SIR-with-underreporting reduced observation model.
pub fn diagnose_sir_early_phase(
    times: &[f64],
    beta: f64,
    gamma: f64,
    rho: f64,
    i0: f64,
    sigma: f64,
) -> Result<SIREarlyPhaseDiagnostic, String> {
    for (name, value) in [
        ("beta", beta), ("gamma", gamma), ("rho", rho), ("I0", i0), ("sigma", sigma),
    ] {
        if !value.is_finite() || value <= 0.0 {
            return Err(format!("{name} must be a finite positive number"));
        }
    }
    if times.len() < 2
        || times.iter().any(|time| !time.is_finite() || *time < 0.0)
    {
        return Err("times must contain at least two finite non-negative values".into());
    }
    let mut distinct = times.to_vec();
    distinct.sort_by(|left, right| left.partial_cmp(right).unwrap());
    distinct.dedup();
    if distinct.len() < 2 {
        return Err("times must contain at least two distinct values".into());
    }
    let sigma_squared = sigma * sigma;
    if sigma_squared == 0.0 || !sigma_squared.is_finite() {
        return Err("sigma is outside the stable Fisher information range".into());
    }
    let precision = 1.0 / sigma_squared;
    if !precision.is_finite() {
        return Err("sigma is outside the stable Fisher information range".into());
    }

    let jacobian: Vec<Vec<f64>> = times
        .iter()
        .map(|time| vec![1.0 + beta * time, -gamma * time, 1.0, 1.0])
        .collect();
    let weights = vec![precision; times.len()];
    let names = vec!["beta".into(), "gamma".into(), "rho".into(), "I0".into()];
    let local_information = diagnose_jacobian(
        &jacobian, Some(&weights), Some(&names), None, 1e-12,
    )?;
    let observed_amplitude = rho * beta * i0;
    if !observed_amplitude.is_finite() {
        return Err("rho*beta*I0 overflows the supported numeric range".into());
    }

    Ok(SIREarlyPhaseDiagnostic {
        local_information,
        growth_rate: beta - gamma,
        observed_amplitude,
        structural_status: "non_identifiable_under_early_phase_approximation".into(),
        assumptions: vec![
            "S(t)/N approximately 1 and I(t) much smaller than N".into(),
            "observed cases C(t) approximately rho*beta*I0*exp((beta-gamma)*t)".into(),
            "independent Gaussian errors on log observed cases with standard deviation sigma".into(),
            "the conclusion applies to the early-phase reduced observation model, not every SIR regime".into(),
        ],
    })
}


#[cfg(test)]
mod generic_tests {
    use super::{diagnose_jacobian, diagnose_sir_early_phase};

    #[test]
    fn sobol_first_order_matches_saltelli_estimator() {
        let f_a = [0.2, 1.3, -0.4, 2.1, 0.9];
        let f_b = [1.2, -0.2, 0.7, 1.9, -1.0];
        let f_ab = vec![
            vec![0.5, 1.0, 0.3, 2.5, 0.4],
            vec![1.4, -0.1, 0.8, 1.2, -0.6],
        ];
        let report = sobol_first_order(&f_a, &f_b, &f_ab).unwrap();
        assert_eq!(report.sample_count, 5);
        assert_eq!(report.parameter_count, 2);
        assert!((report.first_order_indices[0] - 0.4716878600152157).abs() < 1e-12);
        assert!((report.first_order_indices[1] - 0.5108140419519617).abs() < 1e-12);
    }

    #[test]
    fn sobol_first_order_is_stable_under_common_output_scale() {
        let f_a = [0.2, 1.3, -0.4, 2.1, 0.9];
        let f_b = [1.2, -0.2, 0.7, 1.9, -1.0];
        let f_ab = vec![
            vec![0.5, 1.0, 0.3, 2.5, 0.4],
            vec![1.4, -0.1, 0.8, 1.2, -0.6],
        ];
        let base = sobol_first_order(&f_a, &f_b, &f_ab).unwrap();
        for factor in [1e-200, 1e200] {
            let scaled_a: Vec<f64> = f_a.iter().map(|value| value * factor).collect();
            let scaled_b: Vec<f64> = f_b.iter().map(|value| value * factor).collect();
            let scaled_ab: Vec<Vec<f64>> = f_ab.iter().map(|row| {
                row.iter().map(|value| value * factor).collect()
            }).collect();
            let scaled = sobol_first_order(&scaled_a, &scaled_b, &scaled_ab).unwrap();
            for (left, right) in scaled.first_order_indices.iter().zip(base.first_order_indices.iter()) {
                assert!((left - right).abs() < 1e-12);
            }
            assert!((scaled.output_scale / factor - base.output_scale).abs() < 1e-12);
        }
    }

    #[test]
    fn sobol_first_order_rejects_invalid_or_unresolved_outputs() {
        assert!(sobol_first_order(&[1.0], &[1.0], &[vec![1.0]]).is_err());
        assert!(sobol_first_order(&[1.0, 2.0], &[1.0], &[vec![1.0, 2.0]]).is_err());
        assert!(sobol_first_order(&[1.0, 2.0], &[2.0, 3.0], &[]).is_err());
        assert!(sobol_first_order(&[1.0, 2.0], &[2.0, 3.0], &[vec![1.0]]).is_err());
        assert!(sobol_first_order(&[1.0, f64::INFINITY], &[2.0, 3.0], &[vec![1.0, 2.0]]).is_err());
        assert!(sobol_first_order(&[1.0, 1.0], &[1.0, 1.0], &[vec![1.0, 1.0]]).is_err());
    }

    #[test]
    fn d_optimal_hill_design_selects_informative_omega_levels() {
        let omega = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0];
        let report = d_optimal_hill_design(&omega, 3, 1.0, 1.5, 0.05, 1e-12, 1e-12).unwrap();
        assert_eq!(report.selected_indices.len(), 3);
        assert_eq!(report.selected_omega.len(), 3);
        assert_eq!(report.design.local_information.local_rank, 2);
        assert!(report.warnings.is_empty());
    }

    #[test]
    fn d_optimal_hill_design_is_invariant_to_common_omega_and_k_scale() {
        let omega = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0];
        let base = d_optimal_hill_design(&omega, 3, 1.0, 1.5, 0.05, 1e-12, 1e-12).unwrap();
        let scaled_omega: Vec<f64> = omega.iter().map(|value| value * 1e200).collect();
        let scaled = d_optimal_hill_design(&scaled_omega, 3, 1e200, 1.5, 0.05, 1e-12, 1e-12).unwrap();
        assert_eq!(scaled.selected_indices, base.selected_indices);
        assert!((scaled.design.log_determinant - base.design.log_determinant).abs() < 1e-10);
    }

    #[test]
    fn d_optimal_hill_design_reports_rank_deficiency_at_single_omega_level() {
        let report = d_optimal_hill_design(&[1.0, 1.0, 1.0], 2, 1.0, 1.5, 0.05, 1e-12, 1e-12).unwrap();
        assert_eq!(report.design.local_information.local_rank, 1);
        assert!(!report.warnings.is_empty());
    }

    #[test]
    fn d_optimal_hill_design_rejects_invalid_contract() {
        assert!(d_optimal_hill_design(&[], 1, 1.0, 1.5, 0.05, 1e-12, 1e-12).is_err());
        assert!(d_optimal_hill_design(&[0.0, 1.0], 1, 1.0, 1.5, 0.05, 1e-12, 1e-12).is_err());
        assert!(d_optimal_hill_design(&[1.0, 2.0], 1, 0.0, 1.5, 0.05, 1e-12, 1e-12).is_err());
        assert!(d_optimal_hill_design(&[1.0, 2.0], 1, 1.0, 0.0, 0.05, 1e-12, 1e-12).is_err());
        assert!(d_optimal_hill_design(&[1.0, 2.0], 1, 1.0, 1.5, 0.0, 1e-12, 1e-12).is_err());
    }

    #[test]
    fn d_optimal_design_selects_complementary_observations() {
        let jacobian = vec![
            vec![1.0, 0.0],
            vec![0.0, 1.0],
            vec![1.0, 1.0],
            vec![1.0, -1.0],
        ];
        let names = vec!["x".into(), "y".into()];
        let report = d_optimal_design(
            &jacobian, 2, None, Some(&names), None, 1e-12, 1e-12,
        ).unwrap();
        assert_eq!(report.selected_indices, vec![2, 3]);
        assert_eq!(report.local_information.local_rank, 2);
        assert!((report.local_information.fim_condition_number - 1.0).abs() < 1e-10);
        assert!((report.log_determinant - 4.0f64.ln()).abs() < 1e-10);
    }

    #[test]
    fn d_optimal_design_is_stable_under_common_jacobian_scale() {
        let base_jacobian = vec![
            vec![1.0, 0.0],
            vec![0.0, 1.0],
            vec![1.0, 1.0],
            vec![1.0, -1.0],
        ];
        let base = d_optimal_design(&base_jacobian, 2, None, None, None, 1e-12, 1e-12).unwrap();
        for factor in [1e-200, 1e200] {
            let scaled_jacobian: Vec<Vec<f64>> = base_jacobian.iter()
                .map(|row| row.iter().map(|value| value * factor).collect())
                .collect();
            let scaled = d_optimal_design(&scaled_jacobian, 2, None, None, None, 1e-12, 1e-12).unwrap();
            assert_eq!(scaled.selected_indices, base.selected_indices);
            assert!((scaled.log_determinant - base.log_determinant).abs() < 1e-10);
            assert!((scaled.jacobian_scale / factor - base.jacobian_scale).abs() < 1e-10);
            for (left, right) in scaled.normalized_information_matrix.iter()
                .flatten().zip(base.normalized_information_matrix.iter().flatten()) {
                assert!((left - right).abs() < 1e-12);
            }
        }
    }

    #[test]
    fn d_optimal_design_preserves_rank_deficiency() {
        let jacobian = vec![vec![1.0, 2.0], vec![2.0, 4.0], vec![3.0, 6.0]];
        let report = d_optimal_design(&jacobian, 2, None, None, None, 1e-12, 1e-12).unwrap();
        assert_eq!(report.local_information.local_rank, 1);
        assert!(report.local_information.fim_condition_number.is_infinite());
        assert_eq!(report.selected_indices.len(), 2);
        assert_ne!(report.selected_indices[0], report.selected_indices[1]);
        assert!(report.log_determinant.is_finite());
    }

    #[test]
    fn d_optimal_design_rejects_invalid_selection_contract() {
        let jacobian = vec![vec![1.0, 0.0]];
        assert!(d_optimal_design(&jacobian, 0, None, None, None, 1e-12, 1e-12).is_err());
        assert!(d_optimal_design(&jacobian, 2, None, None, None, 1e-12, 1e-12).is_err());
        assert!(d_optimal_design(&jacobian, 1, None, None, None, 1e-12, 0.0).is_err());
    }

    #[test]
    fn generic_jacobian_detects_rank_deficiency() {
        let jacobian = vec![vec![1.0, 2.0], vec![2.0, 4.0], vec![3.0, 6.0]];
        let report = diagnose_jacobian(&jacobian, None, None, None, 1e-12).unwrap();
        assert_eq!(report.local_rank, 1);
        assert_eq!(report.weak_directions.len(), 1);
    }

    #[test]
    fn generic_jacobian_applies_weights_and_parameter_scales() {
        let jacobian = vec![vec![1.0, 0.0], vec![0.0, 1.0]];
        let weights = [4.0, 1.0];
        let scales = [2.0, 1.0];
        let report = diagnose_jacobian(
            &jacobian, Some(&weights), None, Some(&scales), 1e-12,
        ).unwrap();
        assert_eq!(report.local_rank, 2);
        assert!((report.singular_values[0] - 4.0).abs() < 1e-12);
        assert!((report.singular_values[1] - 1.0).abs() < 1e-12);
    }

    #[test]
    fn generic_jacobian_is_stable_under_extreme_common_scales() {
        for factor in [1e-200, 1e200] {
            let jacobian = vec![vec![factor, 0.0], vec![0.0, factor]];
            let weights = [4.0, 1.0];
            let scales = [2.0, 1.0];
            let report = diagnose_jacobian(
                &jacobian, Some(&weights), None, Some(&scales), 1e-12,
            ).unwrap();
            assert_eq!(report.local_rank, 2);
            assert!((report.fim_condition_number - 16.0).abs() < 1e-10);
            assert!((report.singular_values[0] / factor - 4.0).abs() < 1e-10);
            assert!((report.singular_values[1] / factor - 1.0).abs() < 1e-10);
        }
    }

    #[test]
    fn sir_early_phase_identifies_combinations_not_four_parameters() {
        let times: Vec<f64> = (0..=30).map(|value| value as f64).collect();
        let report = diagnose_sir_early_phase(&times, 0.4, 0.15, 0.1, 100.0, 0.1).unwrap();
        assert_eq!(report.local_information.local_rank, 2);
        assert_eq!(report.local_information.parameters, 4);
        assert_eq!(report.structural_status, "non_identifiable_under_early_phase_approximation");
        assert!((report.growth_rate - 0.25).abs() < 1e-12);
        assert!((report.observed_amplitude - 4.0).abs() < 1e-12);
        assert_eq!(report.local_information.weak_directions.len(), 2);
    }

    #[test]
    fn sir_early_phase_rejects_duplicate_times() {
        assert!(diagnose_sir_early_phase(&[1.0, 1.0], 0.4, 0.15, 0.1, 100.0, 0.1).is_err());
    }
}
