from .model import DegeneracyReport
from .semantics import degeneracy_state, omega_range_orders
from .validator import validate, validate_coherence


def diagnose(system, bootstrap=0):
    validate(system)
    validate_coherence(system.params)
    if bootstrap < 0:
        raise ValueError("bootstrap must be >= 0")

    params = system.params
    omegas = [agent.frequency for agent in system.agents if agent.frequency > 0]
    orders = omega_range_orders(omegas)
    K_free = params.K != float("inf")
    alpha_h_free = params.alpha_h != 1.0
    state = (
        "unknown" if len(omegas) < 2
        else degeneracy_state(orders, K_free, alpha_h_free)
    )

    if state == "unknown":
        recommendation = "Insufficient positive Omega observations to estimate the range or Hill identifiability."
    elif state == "inactive":
        recommendation = "Structural degeneracy inactive under the configured parameter constraints."
    elif orders < 1.0:
        recommendation = (
            "Omega spans less than one order of magnitude. K and alpha_h are "
            "indistinguishable; expand the Omega range or fix K externally."
        )
    else:
        recommendation = (
            "Omega spans between one and three orders of magnitude. Expand "
            "the observed Omega range to at least three orders."
        )

    # K=inf disables the Hill component; its parameters are not estimable.
    # With finite K and fixed alpha_h, K can be identified independently.
    # If both are free, the Omega range must span at least three orders.
    lambda_identifiable = not K_free
    K_identifiable = state != "unknown" and K_free and (not alpha_h_free or orders >= 3.0)
    alpha_h_identifiable = state != "unknown" and K_free and alpha_h_free and orders >= 3.0
    return DegeneracyReport(
        omega_range_orders=orders,
        degeneracy=state,
        lambda_identifiable=lambda_identifiable,
        K_identifiable=K_identifiable,
        alpha_h_identifiable=alpha_h_identifiable,
        recommendation=recommendation,
        # Bootstrap parameter fitting is specified but not implemented.
        bootstrap_ci=None,
    )
