from .model import Solution
from .semantics import fitness,allocation,k_min,debt,omega_range_orders,degeneracy_state
from .validator import validate,validate_coherence
def solve(system,delta=.05):
    validate(system); validate_coherence(system.params)
    fs=fitness(system); alloc=allocation(system,fs); orders=omega_range_orders([a.frequency for a in system.agents])
    kfree=system.params.K!=float("inf"); afree=system.params.alpha_h!=1.0
    deg=degeneracy_state(orders,kfree,afree); warnings=[]
    if deg=="active": warnings.append(f"K-alpha_h degeneracy active (Omega range={orders:.2f} orders)")
    p=system.params
    return Solution(alloc,fs,None,k_min(system,delta),debt(system),True,1,p.model,p.lambda_,p.K,p.alpha_h,orders,deg,warnings)
