import math

import pytest

from ronin.identifiability import diagnose_hill_design


def test_hill_design_reports_local_information_without_global_claims():
    omega = [10 ** (-2 + index * 4 / 40) for index in range(41)]
    report = diagnose_hill_design(omega, K=1.0, alpha_h=1.5, sigma=0.05)

    assert report.observations == 41
    assert report.local_rank == 2
    assert report.local_rank_status == "full_rank"
    assert report.fim_condition_number < math.inf
    assert report.structural_status == "not_assessed"
    assert report.practical_status == "not_calibrated"
    assert report.estimability_status == "not_assessed"
    assert report.parameterization == "log(K), log(alpha_h)"


def test_hill_design_flags_sub_saturated_design_without_overclaiming():
    report = diagnose_hill_design(
        [0.001, 0.002, 0.004, 0.008], K=1.0, alpha_h=1.5, sigma=0.05
    )

    assert report.max_omega_over_k < 0.1
    assert report.saturation_fraction == 0.0
    assert any("below the configured saturation ratio" in item for item in report.warnings)
    assert report.structural_status == "not_assessed"


def test_hill_design_is_invariant_to_common_omega_and_k_scale():
    first = diagnose_hill_design(
        [0.01, 0.1, 1.0, 10.0], K=1.0, alpha_h=1.5, sigma=0.05
    )
    scaled = diagnose_hill_design(
        [10.0, 100.0, 1000.0, 10000.0], K=1000.0, alpha_h=1.5, sigma=0.05
    )

    assert scaled.singular_values == pytest.approx(first.singular_values)
    assert scaled.fim_condition_number == pytest.approx(first.fim_condition_number)
    assert scaled.saturation_fraction == first.saturation_fraction


def test_hill_design_one_observation_has_rank_at_most_one():
    report = diagnose_hill_design([0.5], K=1.0, alpha_h=1.5, sigma=0.05)
    assert report.local_rank == 1
    assert report.fim_condition_number == math.inf


@pytest.mark.parametrize(
    "kwargs",
    [
        {"omega": [0.1, 1.0], "K": 0.0, "alpha_h": 1.5, "sigma": 0.05},
        {"omega": [0.1, 1.0], "K": 1.0, "alpha_h": 0.0, "sigma": 0.05},
        {"omega": [0.1, 1.0], "K": 1.0, "alpha_h": 1.5, "sigma": 0.0},
        {"omega": [0.1, True], "K": 1.0, "alpha_h": 1.5, "sigma": 0.05},
        {"omega": [0.1, math.inf], "K": 1.0, "alpha_h": 1.5, "sigma": 0.05},
    ],
)
def test_hill_design_rejects_invalid_inputs(kwargs):
    with pytest.raises(ValueError):
        diagnose_hill_design(**kwargs)


def test_hill_design_accepts_one_shot_iterables():
    report = diagnose_hill_design(
        (value for value in [0.01, 0.1, 1.0, 10.0]),
        K=1.0,
        alpha_h=1.5,
        sigma=0.05,
    )
    assert report.observations == 4
    assert report.omega_range_orders == pytest.approx(3.0)


from ronin.identifiability import d_optimal_design, diagnose_jacobian, diagnose_sir_early_phase


def test_generic_jacobian_diagnostic_detects_rank_and_weak_direction():
    report = diagnose_jacobian(
        [[1.0, 2.0], [2.0, 4.0], [3.0, 6.0]],
        parameter_names=("K", "alpha_h"),
    )
    assert report.local_rank == 1
    assert report.local_rank_status == "rank_deficient"
    assert len(report.weak_directions) == 1
    assert report.structural_status == "not_assessed"


def test_generic_jacobian_uses_parameter_scales_and_weights():
    report = diagnose_jacobian(
        [[1.0, 0.0], [0.0, 1.0]],
        weights=[4.0, 1.0],
        parameter_scales=[2.0, 1.0],
        parameter_names=("x", "y"),
    )
    assert report.local_rank == 2
    assert report.singular_values == pytest.approx((4.0, 1.0))
    assert report.fim_condition_number == pytest.approx(16.0)


def test_sir_early_phase_reports_identifiable_combinations_not_individuals():
    report = diagnose_sir_early_phase(
        range(0, 31), beta=0.4, gamma=0.15, rho=0.1, I0=100.0, sigma=0.1
    )
    assert report.local_information.local_rank == 2
    assert report.local_information.parameters == 4
    assert report.structural_status == "non_identifiable_under_early_phase_approximation"
    assert report.growth_rate == pytest.approx(0.25)
    assert report.observed_amplitude == pytest.approx(4.0)
    assert len(report.local_information.weak_directions) == 2


def test_sir_early_phase_requires_distinct_times_and_positive_parameters():
    with pytest.raises(ValueError, match="distinct"):
        diagnose_sir_early_phase([1.0, 1.0], 0.4, 0.15, 0.1, 100.0, 0.1)
    with pytest.raises(ValueError, match="beta"):
        diagnose_sir_early_phase([1.0, 2.0], 0.0, 0.15, 0.1, 100.0, 0.1)


@pytest.mark.parametrize(
    "jacobian",
    [[], [[]], [[1.0, 2.0], [1.0]], [[True]], [[math.inf]]],
)
def test_generic_jacobian_rejects_invalid_matrices(jacobian):
    with pytest.raises(ValueError):
        diagnose_jacobian(jacobian)

@pytest.mark.parametrize("factor", [1e-200, 1e200])
def test_generic_jacobian_is_stable_under_extreme_common_scales(factor):
    report = diagnose_jacobian(
        [[factor, 0.0], [0.0, factor]],
        weights=[4.0, 1.0],
        parameter_scales=[2.0, 1.0],
    )

    assert report.local_rank == 2
    assert report.fim_condition_number == pytest.approx(16.0)
    assert report.singular_values[0] / factor == pytest.approx(4.0)
    assert report.singular_values[1] / factor == pytest.approx(1.0)


def test_d_optimal_design_selects_complementary_observations():
    report = d_optimal_design(
        [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, -1.0]],
        n_samples=2,
        parameter_names=("x", "y"),
    )

    assert report.selected_indices == (2, 3)
    assert report.local_information.local_rank == 2
    assert report.local_information.fim_condition_number == pytest.approx(1.0)
    assert report.log_determinant == pytest.approx(math.log(4.0))
    assert report.jacobian_scale == pytest.approx(1.0)


def test_d_optimal_design_does_not_hide_rank_deficiency():
    report = d_optimal_design(
        [[1.0, 2.0], [2.0, 4.0], [3.0, 6.0]],
        n_samples=2,
    )

    assert report.local_information.local_rank == 1
    assert report.local_information.fim_condition_number == math.inf
    assert len(set(report.selected_indices)) == 2
    assert math.isfinite(report.log_determinant)


@pytest.mark.parametrize(
    ("jacobian", "n_samples", "ridge"),
    [
        ([[1.0, 0.0]], 0, 1e-12),
        ([[1.0, 0.0]], 2, 1e-12),
        ([[1.0, 0.0]], 1, 0.0),
    ],
)
def test_d_optimal_design_rejects_invalid_selection_contract(jacobian, n_samples, ridge):
    with pytest.raises(ValueError):
        d_optimal_design(jacobian, n_samples, ridge=ridge)
