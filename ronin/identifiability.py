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
    max_omega_over_k: float
    singular_values: tuple
    fim_condition_number: float
    local_rank: int
    local_rank_status: str
    weak_direction: tuple
    typical_parameters: tuple
    relative_tolerance: float
    saturation_ratio: float
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
        max_omega_over_k=max_ratio,
        singular_values=singular_values,
        fim_condition_number=condition,
        local_rank=rank,
        local_rank_status="full_rank" if rank == 2 else "rank_deficient",
        weak_direction=weak_direction,
        typical_parameters=(K, alpha_h),
        relative_tolerance=float(relative_tolerance),
        saturation_ratio=float(saturation_ratio),
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


@dataclass(frozen=True)
class LocalInformationDiagnostic:
    observations: int
    parameters: int
    parameter_names: tuple
    parameter_scales: tuple
    singular_values: tuple
    fim_condition_number: float
    local_rank: int
    local_rank_status: str
    weak_directions: tuple
    relative_tolerance: float
    structural_status: str
    practical_status: str
    estimability_status: str
    noise_model: str
    assumptions: tuple


@dataclass(frozen=True)
class SIREarlyPhaseDiagnostic:
    local_information: LocalInformationDiagnostic
    growth_rate: float
    observed_amplitude: float
    structural_status: str
    assumptions: tuple


def _symmetric_eigen(matrix):
    """Jacobi eigensolver for a small real symmetric matrix."""
    size = len(matrix)
    values = [row[:] for row in matrix]
    vectors = [[1.0 if row == col else 0.0 for col in range(size)] for row in range(size)]
    max_iterations = max(1, 100 * size * size)

    for _ in range(max_iterations):
        p, q = 0, 0
        largest = 0.0
        for row in range(size):
            for col in range(row + 1, size):
                candidate = abs(values[row][col])
                if candidate > largest:
                    largest, p, q = candidate, row, col
        scale = max(1.0, max(abs(values[index][index]) for index in range(size)))
        if largest <= 1e-15 * scale:
            break

        off_diagonal = values[p][q]
        tau = (values[q][q] - values[p][p]) / (2.0 * off_diagonal)
        if tau == 0.0:
            tangent = 1.0
        else:
            tangent = math.copysign(1.0, tau) / (abs(tau) + math.sqrt(1.0 + tau * tau))
        cosine = 1.0 / math.sqrt(1.0 + tangent * tangent)
        sine = tangent * cosine

        pp = values[p][p]
        qq = values[q][q]
        values[p][p] = pp - tangent * off_diagonal
        values[q][q] = qq + tangent * off_diagonal
        values[p][q] = values[q][p] = 0.0

        for index in range(size):
            if index in (p, q):
                continue
            ip = values[index][p]
            iq = values[index][q]
            values[index][p] = values[p][index] = cosine * ip - sine * iq
            values[index][q] = values[q][index] = sine * ip + cosine * iq

        for index in range(size):
            vp = vectors[index][p]
            vq = vectors[index][q]
            vectors[index][p] = cosine * vp - sine * vq
            vectors[index][q] = sine * vp + cosine * vq

    pairs = sorted(
        ((values[index][index], tuple(vectors[row][index] for row in range(size)))
         for index in range(size)),
        key=lambda item: item[0],
        reverse=True,
    )
    return [item[0] for item in pairs], [item[1] for item in pairs]


def diagnose_jacobian(
    jacobian,
    *,
    weights=None,
    parameter_names=None,
    parameter_scales=None,
    relative_tolerance=1e-12,
):
    """Diagnose local information from an observation-by-parameter Jacobian.

    The supplied Jacobian must already be evaluated at documented typical
    parameters. Weights are diagonal observation precisions. Parameter scales
    convert derivatives to dimensionless coordinates before forming J'WJ.
    """
    if (
        isinstance(relative_tolerance, bool)
        or not isinstance(relative_tolerance, (int, float))
        or not math.isfinite(relative_tolerance)
        or not 0 < relative_tolerance < 1
    ):
        raise ValueError("relative_tolerance must be finite and in (0,1)")

    try:
        rows = [list(row) for row in jacobian]
    except TypeError as error:
        raise ValueError("jacobian must be a non-empty rectangular matrix") from error
    if not rows or not rows[0]:
        raise ValueError("jacobian must be a non-empty rectangular matrix")
    columns = len(rows[0])
    if any(len(row) != columns for row in rows):
        raise ValueError("jacobian rows must have equal length")

    numeric_rows = []
    for row in rows:
        numeric_row = []
        for value in row:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("jacobian values must be finite numbers")
            value = float(value)
            if not math.isfinite(value):
                raise ValueError("jacobian values must be finite numbers")
            numeric_row.append(value)
        numeric_rows.append(numeric_row)

    if weights is None:
        observation_weights = [1.0] * len(numeric_rows)
    else:
        try:
            observation_weights = list(weights)
        except TypeError as error:
            raise ValueError("weights must contain one finite positive value per row") from error
        if len(observation_weights) != len(numeric_rows):
            raise ValueError("weights length must equal the number of Jacobian rows")
        for index, value in enumerate(observation_weights):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("weights must be finite positive numbers")
            value = float(value)
            if not math.isfinite(value) or value <= 0:
                raise ValueError("weights must be finite positive numbers")
            observation_weights[index] = value

    if parameter_scales is None:
        scales = [1.0] * columns
    else:
        try:
            scales = list(parameter_scales)
        except TypeError as error:
            raise ValueError("parameter_scales must contain one positive value per parameter") from error
        if len(scales) != columns:
            raise ValueError("parameter_scales length must equal the number of Jacobian columns")
        for index, value in enumerate(scales):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("parameter_scales must be finite positive numbers")
            value = float(value)
            if not math.isfinite(value) or value <= 0:
                raise ValueError("parameter_scales must be finite positive numbers")
            scales[index] = value

    if parameter_names is None:
        names = tuple(f"parameter_{index + 1}" for index in range(columns))
    else:
        names = tuple(parameter_names)
        if len(names) != columns or any(not isinstance(name, str) or not name for name in names):
            raise ValueError("parameter_names must contain one non-empty string per column")
        if len(set(names)) != len(names):
            raise ValueError("parameter_names must be unique")

    information = [[0.0] * columns for _ in range(columns)]
    for row, weight in zip(numeric_rows, observation_weights):
        scaled = [value * scale for value, scale in zip(row, scales)]
        for left in range(columns):
            for right in range(left, columns):
                information[left][right] += weight * scaled[left] * scaled[right]

    for left in range(columns):
        for right in range(left):
            information[left][right] = information[right][left]

    if any(not math.isfinite(value) for row in information for value in row):
        raise ValueError("Fisher information overflow; rescale the Jacobian or weights")

    eigenvalues, eigenvectors = _symmetric_eigen(information)
    largest = max(0.0, eigenvalues[0])
    negative_tolerance = relative_tolerance * max(1.0, largest)
    if any(value < -negative_tolerance for value in eigenvalues):
        raise ValueError("computed information matrix is not positive semidefinite")
    eigenvalues = [max(0.0, value) for value in eigenvalues]

    if largest == 0.0:
        rank = 0
        condition = math.inf
    else:
        rank = sum(value > relative_tolerance * largest for value in eigenvalues)
        condition = math.inf if rank < columns else largest / eigenvalues[-1]

    singular_values = tuple(math.sqrt(value) for value in eigenvalues)
    weak_directions = tuple(
        eigenvectors[index]
        for index, value in enumerate(eigenvalues)
        if largest == 0.0 or value <= relative_tolerance * largest
    )

    return LocalInformationDiagnostic(
        observations=len(numeric_rows),
        parameters=columns,
        parameter_names=names,
        parameter_scales=tuple(scales),
        singular_values=singular_values,
        fim_condition_number=condition,
        local_rank=rank,
        local_rank_status="full_rank" if rank == columns else "rank_deficient",
        weak_directions=weak_directions,
        relative_tolerance=float(relative_tolerance),
        structural_status="not_assessed",
        practical_status="not_calibrated",
        estimability_status="not_assessed",
        noise_model="caller-supplied independent observation precisions (diagonal W)",
        assumptions=(
            "Jacobian evaluated at documented typical parameters",
            "local linearization and supplied diagonal observation weights",
            "parameter scales define dimensionless local coordinates",
            "local FIM rank is not a global structural-identifiability proof",
        ),
    )


def diagnose_sir_early_phase(times, beta, gamma, rho, I0, sigma):
    """Diagnose the exact early-phase SIR-with-underreporting approximation.

    The observation model is log C(t) = log(rho*beta*I0) + (beta-gamma)*t.
    Consequently, the data identify at most the combinations beta-gamma and
    rho*beta*I0 in this reduced regime, not the four individual parameters.
    """
    parameters = (("beta", beta), ("gamma", gamma), ("rho", rho), ("I0", I0), ("sigma", sigma))
    for name, value in parameters:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a finite positive number")
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be a finite positive number")

    try:
        observation_times = list(times)
    except TypeError as error:
        raise ValueError("times must contain at least two finite non-negative values") from error
    if len(observation_times) < 2:
        raise ValueError("times must contain at least two finite non-negative values")
    numeric_times = []
    for value in observation_times:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("times must contain finite non-negative numbers")
        value = float(value)
        if not math.isfinite(value) or value < 0:
            raise ValueError("times must contain finite non-negative numbers")
        numeric_times.append(value)
    if len(set(numeric_times)) < 2:
        raise ValueError("times must contain at least two distinct values")

    beta = float(beta)
    gamma = float(gamma)
    rho = float(rho)
    I0 = float(I0)
    sigma = float(sigma)
    sigma_squared = sigma * sigma
    if sigma_squared == 0.0 or not math.isfinite(sigma_squared):
        raise ValueError("sigma is outside the stable Fisher information range")
    precision = 1.0 / sigma_squared
    if not math.isfinite(precision):
        raise ValueError("sigma is outside the stable Fisher information range")

    jacobian = [
        [1.0 + beta * time, -gamma * time, 1.0, 1.0]
        for time in numeric_times
    ]
    local = diagnose_jacobian(
        jacobian,
        weights=[precision] * len(jacobian),
        parameter_names=("beta", "gamma", "rho", "I0"),
        relative_tolerance=1e-12,
    )
    return SIREarlyPhaseDiagnostic(
        local_information=local,
        growth_rate=beta - gamma,
        observed_amplitude=rho * beta * I0,
        structural_status="non_identifiable_under_early_phase_approximation",
        assumptions=(
            "S(t)/N approximately 1 and I(t) much smaller than N",
            "observed cases C(t) approximately rho*beta*I0*exp((beta-gamma)*t)",
            "independent Gaussian errors on log observed cases with standard deviation sigma",
            "the conclusion applies to the early-phase reduced observation model, not every SIR regime",
        ),
    )
