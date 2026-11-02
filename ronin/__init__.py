"""RONIN 1.1 reference runtime."""

__version__ = "1.1.0"

from .diagnose import diagnose
from .identifiability import (
    DOptimalDesign,
    HillDOptimalDesign,
    HillDesignDiagnostic,
    LocalInformationDiagnostic,
    SIREarlyPhaseDiagnostic,
    SobolFirstOrderDiagnostic,
    d_optimal_design,
    d_optimal_hill_design,
    diagnose_hill_design,
    diagnose_jacobian,
    diagnose_sir_early_phase,
    sobol_first_order,
)
from .model import Agent, DegeneracyReport, Params, Simulation, Solution, System
from .parser import parse
from .simulator import simulate
from .solver import solve

__all__ = [
    "Agent",
    "Params",
    "System",
    "Solution",
    "Simulation",
    "DegeneracyReport",
    "parse",
    "solve",
    "simulate",
    "diagnose",
    "HillDOptimalDesign",
    "d_optimal_hill_design",
    "DOptimalDesign",
    "d_optimal_design",
    "HillDesignDiagnostic",
    "diagnose_hill_design",
    "LocalInformationDiagnostic",
    "SIREarlyPhaseDiagnostic",
    "SobolFirstOrderDiagnostic",
    "sobol_first_order",
    "diagnose_jacobian",
    "diagnose_sir_early_phase",
    "__version__",
]
