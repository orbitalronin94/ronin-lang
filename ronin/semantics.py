import math

from .errors import SemanticError
from .validator import validate, validate_coherence

EPS = 1e-12


def hill(omega, K, alpha_h):
    """Hill saturation; K=inf is the identity."""
    omega = float(omega)
    K = float(K)
    alpha_h = float(alpha_h)
    if omega < 0 or math.isnan(omega):
        raise SemanticError("omega must be finite and non-negative")
    if K == float("inf"):
        return omega
    if not math.isfinite(K) or K <= 0 or not math.isfinite(alpha_h) or alpha_h <= 0:
        raise SemanticError("invalid Hill parameters")
    if omega == 0:
        return 0.0
    log_ratio = alpha_h * (math.log(omega) - math.log(K))
    if log_ratio >= 0:
        return 1.0 / (1.0 + math.exp(-log_ratio))
    exp_ratio = math.exp(log_ratio)
    return exp_ratio / (1.0 + exp_ratio)


def ces_combine(phi, psi, omega_eff, lam, w=(1 / 3, 1 / 3, 1 / 3)):
    """Weighted CES power mean; its lambda->0 limit is geometric."""
    values = tuple(max(float(value), EPS) for value in (phi, psi, omega_eff))
    if len(w) != 3 or any(not math.isfinite(x) or x < 0 for x in w):
        raise SemanticError("CES requires three finite non-negative weights")
    if not math.isclose(sum(w), 1.0, abs_tol=1e-9):
        raise SemanticError("CES weights must sum to 1")
    if abs(lam) < 1e-6:
        return math.exp(sum(weight * math.log(value) for weight, value in zip(w, values)))
    inner = sum(weight * value**lam for weight, value in zip(w, values))
    if inner <= 0:
        raise SemanticError("CES aggregate is not positive")
    return inner ** (1.0 / lam)


def fitness(system):
    validate(system)
    validate_coherence(system.params)
    params = system.params
    if params.model == "full" and params.memory_order > 1:
        raise SemanticError(
            "full temporal-memory evaluation is specified but not implemented in this Python runtime"
        )

    results = []
    for agent in system.agents:
        omega_eff = hill(agent.frequency, params.K, params.alpha_h)
        if params.model in ("pusfre", "hill") or abs(params.lambda_) < 1e-6:
            value = agent.phi * agent.psi * (omega_eff ** params.alpha)
        else:
            value = ces_combine(agent.phi, agent.psi, omega_eff, params.lambda_)
        results.append(value)
    return results


def allocation(system, fs=None):
    fs = fitness(system) if fs is None else list(fs)
    if len(fs) != len(system.agents):
        raise SemanticError("fitness vector length must equal the number of agents")
    if any(not math.isfinite(value) or value < 0 for value in fs):
        raise SemanticError("fitness values must be finite and non-negative")
    total = sum(fs)
    if total <= 0:
        if system.resource == 0:
            return [0.0] * len(fs)
        raise SemanticError("allocation undefined: sum of fitness is zero")
    return [system.resource * value / total for value in fs]


def k_min(system, delta=None):
    delta = system.params.coexistence_delta if delta is None else float(delta)
    if not 0 < delta < system.parts:
        raise SemanticError("coexistence delta must satisfy 0 < delta < parts")
    products = [agent.phi * agent.psi for agent in system.agents]
    if min(products) <= 0:
        return None
    return (
        system.parts
        * (max(products) / min(products))
        / math.log(system.parts / delta)
    )


def debt(system):
    """Placeholder required by the data model; no normative estimator is supplied."""
    return 0.0


def omega_range_orders(omegas):
    positive = [float(value) for value in omegas if value > 0]
    if len(positive) < 2:
        return 0.0
    return math.log10(max(positive) / min(positive))


def degeneracy_state(omega_range, K_free, alpha_h_free):
    if not K_free or not alpha_h_free:
        return "inactive"
    return "inactive" if omega_range >= 3.0 else "active"
