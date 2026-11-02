"""RONIN 1.1 reference runtime."""

__version__ = "1.1.0"

from .diagnose import diagnose
from .identifiability import (
    HillDesignDiagnostic,
    LocalInformationDiagnostic,
    SIREarlyPhaseDiagnostic,
    diagnose_hill_design,
    diagnose_jacobian,
    diagnose_sir_early_phase,
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
    "HillDesignDiagnostic",
    "diagnose_hill_design",
    "LocalInformationDiagnostic",
    "SIREarlyPhaseDiagnostic",
    "diagnose_jacobian",
    "diagnose_sir_early_phase",
    "__version__",
]
