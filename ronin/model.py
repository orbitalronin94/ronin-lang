from dataclasses import dataclass, field
from math import inf
from typing import List, Optional


@dataclass(frozen=True)
class Agent:
    phi: float
    psi: float
    frequency: float


@dataclass(frozen=True)
class Params:
    # RONIN 1.0
    alpha: float = 1.0
    gamma: float = 0.4
    sigma: float = 0.0
    coexistence_delta: float = 0.05
    # RONIN 1.1 — CES-Saturada
    model: str = "pusfre"
    lambda_: float = 0.0
    K: float = inf
    alpha_h: float = 1.0
    memory_order: int = 1
    memory_weights: Optional[List[float]] = None
    degeneracy_check: bool = False
    omega_range_report: bool = False


@dataclass(frozen=True)
class System:
    name: str
    parts: int
    resource: float
    agents: List[Agent]
    params: Params = field(default_factory=Params)


@dataclass
class Solution:
    allocation: List[float]
    fitness: List[float]
    coexistence: Optional[bool] = None
    k_min: Optional[float] = None
    debt: float = 0.0
    convergence: bool = True
    steps: int = 1
    model_used: str = "pusfre"
    lambda_used: float = 0.0
    K_used: float = inf
    alpha_h_used: float = 1.0
    omega_range: float = 0.0
    degeneracy: str = "unknown"
    warnings: List[str] = field(default_factory=list)


@dataclass
class DegeneracyReport:
    omega_range_orders: float
    degeneracy: str
    lambda_identifiable: bool
    K_identifiable: bool
    alpha_h_identifiable: bool
    recommendation: str
    bootstrap_ci: Optional[dict] = None


@dataclass
class Simulation:
    history: List[List[float]]
    final_state: List[float]
    steps: int
    seed: Optional[int]
    extinction_events: List[int] = field(default_factory=list)
    survivability: float = 1.0
