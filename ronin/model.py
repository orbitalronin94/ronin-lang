from dataclasses import dataclass, field
from math import inf
@dataclass
class Agent:
    phi: float
    psi: float
    frequency: float
@dataclass
class Params:
    alpha: float = 1.0
    gamma: float = 0.4
    sigma: float = 0.0
    coexistence_delta: float = 0.05
    model: str = "pusfre"
    lambda_: float = 0.0
    K: float = inf
    alpha_h: float = 1.0
    memory_order: int = 1
    memory_weights: object = None
    degeneracy_check: bool = False
    omega_range_report: bool = False
@dataclass
class System:
    name: str
    parts: int
    resource: float
    agents: list
    params: Params = field(default_factory=Params)
@dataclass
class Solution:
    allocation: list
    fitness: list
    coexistence: object = None
    k_min: object = None
    debt: float = 0.0
    convergence: bool = True
    steps: int = 1
    model_used: str = "pusfre"
    lambda_used: float = 0.0
    K_used: float = inf
    alpha_h_used: float = 1.0
    omega_range: float = 0.0
    degeneracy: str = "unknown"
    warnings: list = field(default_factory=list)
@dataclass
class DegeneracyReport:
    omega_range_orders: float
    degeneracy: str
    lambda_identifiable: bool
    K_identifiable: bool
    alpha_h_identifiable: bool
    recommendation: str
    bootstrap_ci: object = None
@dataclass
class Simulation:
    history: list
    final_state: list
    steps: int
    seed: object
    extinction_events: list = field(default_factory=list)
    survivability: float = 1.0
