import random
from .model import Simulation
from .validator import validate,validate_coherence
def simulate(system,steps=100,seed=None):
    validate(system); validate_coherence(system.params)
    if steps<1: raise ValueError("steps must be >=1")
    rng=random.Random(seed); state=[a.frequency for a in system.agents]; history=[state.copy()]; extinct=[]
    for _ in range(steps):
        w=[a.phi*a.psi*x**system.params.alpha for a,x in zip(system.agents,state)]; total=sum(w)
        target=[x/total for x in w] if total else [1/len(w)]*len(w)
        nxt=[max(0,x+.5*(t-x)+rng.gauss(0,system.params.sigma/10)) for x,t in zip(state,target)]
        z=sum(nxt); state=[x/z for x in nxt] if z else [1/len(nxt)]*len(nxt)
        history.append(state.copy())
        extinct.extend(i for i,x in enumerate(state) if x<=1e-12 and i not in extinct)
    return Simulation(history,state,steps,seed,extinct,sum(x>1e-12 for x in state)/len(state))
