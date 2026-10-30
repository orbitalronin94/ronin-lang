from .model import DegeneracyReport
from .semantics import omega_range_orders,degeneracy_state
from .validator import validate,validate_coherence
def diagnose(system,bootstrap=0):
    validate(system); validate_coherence(system.params); p=system.params
    orders=omega_range_orders([a.frequency for a in system.agents])
    state=degeneracy_state(orders,p.K!=float("inf"),p.alpha_h!=1.0)
    msg=("K-alpha_h degeneracy active; expand Omega coverage to at least 3 orders." if state=="active"
         else "Structural degeneracy inactive under the configured parameter constraints.")
    return DegeneracyReport(orders,state,True,state=="inactive",state=="inactive",msg,None)
