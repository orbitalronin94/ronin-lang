from .errors import SemanticError
from .model import Solution
from .semantics import (
    allocation,
    debt,
    degeneracy_state,
    fitness,
    k_min,
    omega_range_orders,
)
from .validator import validate, validate_coherence


def solve(system, delta=None):
    validate(system)
    validate_coherence(system.params)

    fs = fitness(system)
    alloc = allocation(system, fs)
    threshold = k_min(system, delta)
    coexistence = None if threshold is None else system.resource >= threshold

    orders = omega_range_orders([agent.frequency for agent in system.agents])
    params = system.params
    state = degeneracy_state(
        orders,
        params.K != float("inf"),
        params.alpha_h != 1.0,
    )

    warnings = []
    if coexistence is False:
        warnings.append(
            f"k_min ({threshold:.6g}) exceeds available resource ({system.resource:.6g}); "
            "coexistence is not supported by this threshold."
        )
    if params.degeneracy_check and state == "active":
        warnings.append(
            f"K-alpha_h degeneracy active (Omega range={orders:.2f} orders); "
            "K and alpha_h are not independently identifiable."
        )
    if params.model == "full" and params.memory_order > 1:
        raise SemanticError("full temporal-memory evaluation is not implemented")
    warnings.append("debt=0.0 is a placeholder; the source does not define an executable debt estimator.")

    return Solution(
        allocation=alloc,
        fitness=fs,
        coexistence=coexistence,
        k_min=threshold,
        debt=debt(system),
        convergence=True,
        steps=1,
        model_used=params.model,
        lambda_used=params.lambda_,
        K_used=params.K,
        alpha_h_used=params.alpha_h,
        omega_range=orders,
        degeneracy=state,
        warnings=warnings,
    )
