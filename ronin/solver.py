from .model import Solution
from .semantics import fitness, allocation, k_min, debt, omega_range_orders, degeneracy_state
from .validator import validate, validate_coherence


def solve(system, delta=0.05):
    validate(system)
    validate_coherence(system.params)
    fs = fitness(system)
    alloc = allocation(system, fs)
    orders = omega_range_orders([a.frequency for a in system.agents])
    kfree = system.params.K != float("inf")
    afree = system.params.alpha_h != 1.0
    deg = degeneracy_state(orders, kfree, afree)
    warnings = []
    if deg == "active":
        warnings.append(f"K-alpha_h degeneracy active (Omega range={orders:.2f} orders)")
    p = system.params
    minimum = k_min(system, delta)
    return Solution(
        allocation=alloc,
        fitness=fs,
        coexistence=(system.resource >= minimum) if minimum is not None else None,
        k_min=minimum,
        debt=debt(system),
        convergence=True,
        steps=1,
        model_used=p.model,
        lambda_used=p.lambda_,
        K_used=p.K,
        alpha_h_used=p.alpha_h,
        omega_range=orders,
        degeneracy=deg,
        warnings=warnings,
    )
