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
