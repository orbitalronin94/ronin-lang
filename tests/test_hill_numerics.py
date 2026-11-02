import pytest

from ronin.semantics import hill


@pytest.mark.parametrize(
    ("omega", "K", "alpha_h", "expected"),
    [
        (1.0, 1e-300, 2.0, 1.0),
        (1e-300, 1.0, 2.0, 0.0),
        (0.5, 0.5, 1.0, 0.5),
        (0.25, 0.5, 2.0, 0.2),
    ],
)
def test_hill_is_stable_for_extreme_ratios(omega, K, alpha_h, expected):
    assert hill(omega, K, alpha_h) == pytest.approx(expected, abs=1e-15)


def test_hill_remains_bounded_for_extreme_valid_inputs():
    assert 0.0 <= hill(1.0, 1e-300, 2.0) <= 1.0
    assert 0.0 <= hill(1e-300, 1.0, 2.0) <= 1.0
