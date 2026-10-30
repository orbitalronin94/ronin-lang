import math
from .errors import SemanticError
from .validator import validate, validate_coherence
EPS=1e-12
def hill(omega,K,alpha_h):
    """Hill: Ω^αh / (K^αh + Ω^αh); K=infinity is identity."""
    if math.isinf(K): return float(omega)
    if omega<0 or K<=0 or alpha_h<=0: raise SemanticError("invalid Hill arguments")
    if omega==0: return 0.0
    x=(omega/K)**alpha_h
    return x/(1+x)
def ces_combine(phi,psi,omega_eff,lam,w=(1/3,1/3,1/3)):
    """Weighted CES power mean; lambda->0 is weighted geometric mean."""
    vals=(max(float(phi),EPS),max(float(psi),EPS),max(float(omega_eff),EPS))
    if len(w)!=3 or any(x<0 for x in w) or not math.isclose(sum(w),1,abs_tol=1e-9): raise SemanticError("CES weights must sum to 1")
    if abs(lam)<1e-6: return math.exp(sum(a*math.log(x) for a,x in zip(w,vals)))
    return sum(a*x**lam for a,x in zip(w,vals))**(1/lam)
def fitness(s):
    validate(s); validate_coherence(s.params); p=s.params; out=[]
    for a in s.agents:
        omega=hill(a.frequency,p.K,p.alpha_h)
        if p.model in ("pusfre","hill") or abs(p.lambda_)<1e-6:
            f=a.phi*a.psi*(omega**p.alpha)
        else: f=ces_combine(a.phi,a.psi,omega,p.lambda_)
        out.append(f)
    return out
def allocation(s,fs=None):
    fs=fitness(s) if fs is None else fs; total=sum(fs)
    if total<=0:
        if s.resource==0: return [0.0]*len(fs)
        raise SemanticError("allocation undefined: zero total fitness")
    return [s.resource*f/total for f in fs]
def k_min(s,delta=.05):
    q=[a.phi*a.psi for a in s.agents]
    if min(q)<=0: return None
    return s.parts*max(q)/min(q)/math.log(s.parts/delta)
def debt(s): return 0.0
def omega_range_orders(xs):
    xs=[x for x in xs if x>0]
    return math.log10(max(xs)/min(xs)) if len(xs)>1 else 0.0
def degeneracy_state(orders,K_free,alpha_h_free):
    if not K_free or not alpha_h_free: return "inactive"
    return "inactive" if orders>=3 else "active"
