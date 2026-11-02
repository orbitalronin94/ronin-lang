"""Local pre-fit identifiability diagnostics for experimental designs.

This module deliberately does not infer global structural identifiability or
post-fit estimability from a local Fisher information matrix.
"""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class HillDesignDiagnostic:
    observations: int
    omega_range_orders: float
    saturation_fraction: float
    max_omega_over_K: float
    singular_values: tuple
    fim_condition_number: float
    local_rank: int
    local_rank_status: str
    weak_direction: tuple
    structural_status: str
    practical_status: str
    estimability_status: str
    parameterization: str
    noise_model: str
    assumptions: tuple
    warnings: tuple


def diagnose_hill_design(
    omega,
    K,
    alpha_h,
    sigma,
    *,
    relative_tolerance=1e-12,
    saturation_ratio=0.1,
):
    """Diagnose local Hill-parameter information before fitting.

    Parameters are evaluated in the dimensionless coordinates
    (log(K), log(alpha_h)). The assumed observation model is independent,
    homoscedastic additive Gaussian noise on the Hill response.
    """
    if isinstance(K, bool) or not isinstance(K, (int, float)):
        raise ValueError("K must be a finite positive number")
    if isinstance(alpha_h, bool) or not isinstance(alpha_h, (int, float)):
        raise ValueError("alpha_h must be a finite positive number")
    if isinstance(sigma, bool) or not isinstance(sigma, (int, float)):
        raise ValueError("sigma must be a finite positive number")
    K = float(K)
    alpha_h = float(alpha_h)
    sigma = float(sigma)
    if not math.isfinite(K) or K <= 0:
        raise ValueError("K must be a finite positive number")
    if not math.isfinite(alpha_h) or alpha_h <= 0:
        raise ValueError("alpha_h must be a finite positive number")
    if not math.isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma must be a finite positive number")
    if (
        isinstance(relative_tolerance, bool)
        or not isinstance(relative_tolerance, (int, float))
        or not math.isfinite(relative_tolerance)
        or not 0 < relative_tolerance < 1
    ):
        raise ValueError("relative_tolerance must be finite and in (0,1)")
    if (
        isinstance(saturation_ratio, bool)
        or not isinstance(saturation_ratio, (int, float))
        or not math.isfinite(saturation_ratio)
        or saturation_ratio <= 0
    ):
        raise ValueError("saturation_ratio must be finite and positive")

    try:
        raw_values = list(omega)
    except TypeError as error:
        raise ValueError("omega must be a non-empty iterable of positive numbers") from error
    if not raw_values:
        raise ValueError("omega must contain at least one observation")

    values = []
    for value in raw_values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("omega values must be finite positive numbers")
        value = float(value)
        if not math.isfinite(value) or value <= 0:
            raise ValueError("omega values must be finite positive numbers")
        values.append(value)

    log_k = math.log(K)
    try:
        inv_sigma2 = 1.0 / (sigma * sigma)
    except ZeroDivisionError as error:
        raise ValueError("sigma is too small for stable Fisher information") from error
    if not math.isfinite(inv_sigma2):
        raise ValueError("sigma is too small for stable Fisher information")
    fim_kk = 0.0
    fim_ka = 0.0
    fim_aa = 0.0
    saturated = 0
    max_log_ratio = -math.inf

    for value in values:
        log_ratio = math.log(value) - log_k
        z = alpha_h * log_ratio
        if z >= 0:
            exp_neg = math.exp(-z) if z < 746 else 0.0
            hill_value = 1.0 / (1.0 + exp_neg)
        else:
            exp_pos = math.exp(z) if z > -746 else 0.0
            hill_value = exp_pos / (1.0 + exp_pos)

        slope_factor = alpha_h * hill_value * (1.0 - hill_value)
        derivative_log_k = -slope_factor
        derivative_log_alpha = slope_factor * log_ratio
        fim_kk += derivative_log_k * derivative_log_k * inv_sigma2
        fim_ka += derivative_log_k * derivative_log_alpha * inv_sigma2
        fim_aa += derivative_log_alpha * derivative_log_alpha * inv_sigma2

        max_log_ratio = max(max_log_ratio, log_ratio)
        if log_ratio >= math.log(saturation_ratio):
            saturated += 1

    if not all(math.isfinite(value) for value in (fim_kk, fim_ka, fim_aa)):
        raise ValueError("Fisher information overflow; increase sigma or rescale the design")

    trace = fim_kk + fim_aa
    discriminant = math.hypot(fim_kk - fim_aa, 2.0 * fim_ka)
    eigen_max = max(0.0, 0.5 * (trace + discriminant))
    eigen_min = max(0.0, 0.5 * (trace - discriminant))

    if eigen_max == 0.0:
        rank = 0
        condition = math.inf
        singular_values = (0.0, 0.0)
        weak_direction = (0.0, 1.0)
    else:
        rank = 1 if eigen_min <= relative_tolerance * eigen_max else 2
        condition = math.inf if rank < 2 else eigen_max / eigen_min
        singular_values = (math.sqrt(eigen_max), math.sqrt(eigen_min))

        angle = 0.5 * math.atan2(2.0 * fim_ka, fim_kk - fim_aa)
        weak_direction = (-math.sin(angle), math.cos(angle))

    minimum = min(values)
    maximum = max(values)
    omega_range = (math.log10(maximum) - math.log10(minimum)) if len(values) > 1 else 0.0
    max_ratio = math.exp(max_log_ratio) if max_log_ratio < 709 else math.inf
    warnings = []
    if max_ratio < saturation_ratio:
        warnings.append(
            "All design points are below the configured saturation ratio Ω/K; "
            "K and alpha_h may be strongly confounded."
        )
    if rank < 2:
        warnings.append(
            "The local information matrix is numerically rank deficient at the "
            "supplied typical parameter values."
        )

    return HillDesignDiagnostic(
        observations=len(values),
        omega_range_orders=omega_range,
        saturation_fraction=saturated / len(values),
        max_omega_over_K=max_ratio,
        singular_values=singular_values,
        fim_condition_number=condition,
        local_rank=rank,
        local_rank_status="full_rank" if rank == 2 else "rank_deficient",
        weak_direction=weak_direction,
        structural_status="not_assessed",
        practical_status="not_calibrated",
        estimability_status="not_assessed",
        parameterization="log(K), log(alpha_h)",
        noise_model="independent homoscedastic additive Gaussian noise on Hill response",
        assumptions=(
            "local linearization at supplied typical parameters",
            "Hill response is the observation mean",
            "independent observations with constant variance sigma^2",
            "local FIM rank is not a global structural-identifiability proof",
        ),
        warnings=tuple(warnings),
    )
