import math

from .errors import SemanticError


def validate(system, tolerance=1e-9):
    if system.parts < 2:
        raise SemanticError("parts must be >= 2")
    if len(system.agents) != system.parts:
        raise SemanticError("parts must equal the number of agents")
    if not math.isfinite(system.resource) or system.resource < 0:
        raise SemanticError("resource must be finite and non-negative")

    for index, agent in enumerate(system.agents):
        for name, value in (
            ("phi", agent.phi),
            ("psi", agent.psi),
            ("frequency", agent.frequency),
        ):
            if not math.isfinite(value):
                raise SemanticError(f"agent {index}: {name} must be finite")
        if not 0 <= agent.phi <= 1:
            raise SemanticError(f"agent {index}: phi outside [0,1]")
        if not 0 <= agent.psi <= 1:
            raise SemanticError(f"agent {index}: psi outside [0,1]")
        if not 0 <= agent.frequency <= 1:
            raise SemanticError(f"agent {index}: frequency outside [0,1]")

    if abs(sum(agent.frequency for agent in system.agents) - 1.0) > tolerance:
        raise SemanticError("frequencies must sum to 1 within tolerance")

    params = system.params
    bounded = (
        ("alpha", params.alpha, 0.5, 2.5),
        ("gamma", params.gamma, 0.0, 1.0),
        ("sigma", params.sigma, 0.0, 0.5),
        ("coexistence_delta", params.coexistence_delta, 0.0, 0.1),
    )
    for name, value, lower, upper in bounded:
        if not math.isfinite(value) or not lower <= value <= upper:
            raise SemanticError(f"{name} outside [{lower},{upper}]")
    if params.coexistence_delta == 0:
        raise SemanticError("coexistence_delta must be greater than 0")
    return True


def validate_coherence(params):
    model = params.model
    lam = params.lambda_
    K = params.K
    alpha_h = params.alpha_h
    memory_order = params.memory_order

    if model not in {"pusfre", "ces", "hill", "ces_hill", "full"}:
        raise SemanticError(f"unknown model: {model}")
    if not math.isfinite(lam) or not -1.0 <= lam <= 2.0:
        raise SemanticError("lambda outside [-1,2]")
    if not (K > 0 and (math.isfinite(K) or K == float("inf"))):
        raise SemanticError("K must be positive or inf")
    if not math.isfinite(alpha_h) or alpha_h <= 0:
        raise SemanticError("alpha_h must be finite and positive")
    if memory_order not in (1, 2, 3, 5):
        raise SemanticError("memory_order must be one of 1, 2, 3 or 5")

    if model in ("pusfre", "hill") and abs(lam) > 1e-9:
        raise SemanticError(f'model "{model}" requires lambda = 0')
    if model in ("ces", "ces_hill", "full") and abs(lam) < 1e-9:
        raise SemanticError(f'model "{model}" requires lambda != 0')
    if model in ("pusfre", "ces") and K != float("inf"):
        raise SemanticError(f'model "{model}" requires K = inf')
    if model in ("hill", "ces_hill", "full") and not math.isfinite(K):
        raise SemanticError(f'model "{model}" requires finite K')
    if model != "full" and memory_order != 1:
        raise SemanticError(f'model "{model}" requires memory_order = 1')

    if params.memory_weights is not None:
        weights = params.memory_weights
        if not isinstance(weights, list) or len(weights) != memory_order:
            raise SemanticError("memory_weights length must equal memory_order")
        if any(not isinstance(x, (int, float)) or not math.isfinite(x) or x < 0 for x in weights):
            raise SemanticError("memory_weights must be finite and non-negative numbers")
        if not math.isclose(sum(weights), 1.0, abs_tol=1e-9):
            raise SemanticError("memory_weights must sum to 1")
    return True
