from .model import DegeneracyReport
from .semantics import degeneracy_state, omega_range_orders
from .validator import validate, validate_coherence


def diagnose(system, bootstrap=0):
    validate(system)
    validate_coherence(system.params)
    if bootstrap < 0:
        raise ValueError("bootstrap must be >= 0")

    params = system.params
    orders = omega_range_orders([agent.frequency for agent in system.agents])
    state = degeneracy_state(
        orders,
        params.K != float("inf"),
        params.alpha_h != 1.0,
    )

    if state == "inactive":
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

    return DegeneracyReport(
        omega_range_orders=orders,
        degeneracy=state,
        lambda_identifiable=True,
        K_identifiable=(state == "inactive"),
        alpha_h_identifiable=(state == "inactive"),
        recommendation=recommendation,
        # Bootstrap parameter fitting is only specified, not implemented.
        bootstrap_ci=None,
    )
