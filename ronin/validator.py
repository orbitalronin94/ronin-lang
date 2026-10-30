import math
from .errors import SemanticError
def validate(s,tolerance=1e-9):
    if s.parts<2 or len(s.agents)!=s.parts: raise SemanticError("parts must be >=2 and equal agent count")
    if not math.isfinite(s.resource) or s.resource<0: raise SemanticError("resource must be finite and non-negative")
    for i,a in enumerate(s.agents):
        if any(not math.isfinite(x) for x in (a.phi,a.psi,a.frequency)): raise SemanticError(f"agent {i}: values must be finite")
        if not 0<=a.phi<=1 or not 0<=a.psi<=1 or not 0<=a.frequency<=1: raise SemanticError(f"agent {i}: phi, psi and frequency must be in [0,1]")
    if abs(sum(a.frequency for a in s.agents)-1)>tolerance: raise SemanticError("frequencies must sum to 1")
    p=s.params
    if not .5<=p.alpha<=2.5 or not 0<=p.gamma<=1 or not 0<=p.sigma<=.5: raise SemanticError("alpha, gamma or sigma outside allowed range")
    return True
def validate_coherence(p):
    if p.model not in {"pusfre","ces","hill","ces_hill","full"}: raise SemanticError(f"unknown model {p.model}")
    if not -1<=p.lambda_<=2: raise SemanticError("lambda outside [-1,2]")
    if p.K<=0 or p.alpha_h<=0: raise SemanticError("K and alpha_h must be positive")
    if p.model in ("pusfre","hill") and abs(p.lambda_)>1e-9: raise SemanticError(f"{p.model} requires lambda=0")
    if p.model in ("ces","ces_hill","full") and abs(p.lambda_)<1e-9: raise SemanticError(f"{p.model} requires lambda!=0")
    if p.model in ("pusfre","ces") and not math.isinf(p.K): raise SemanticError(f"{p.model} requires K=inf")
    if p.model in ("hill","ces_hill","full") and not math.isfinite(p.K): raise SemanticError(f"{p.model} requires finite K")
    if p.model!="full" and p.memory_order!=1: raise SemanticError(f"{p.model} requires memory_order=1")
    if p.model=="full" and p.memory_order not in (1,2,3,5): raise SemanticError("full memory_order must be 1,2,3 or 5")
    return True
