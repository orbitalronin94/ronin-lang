"""Validated JSON intermediate representation for RONIN programs."""

import math

from .validator import validate, validate_coherence


def _json_value(value):
    if isinstance(value, float) and not math.isfinite(value):
        return "inf" if value > 0 else "-inf" if value < 0 else "nan"
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    return value


def system_to_ir(system):
    """Convert a validated System into a stable, JSON-compatible mapping."""
    params = {
        "alpha": system.params.alpha,
        "gamma": system.params.gamma,
        "sigma": system.params.sigma,
        "coexistence_delta": system.params.coexistence_delta,
        "model": system.params.model,
        "lambda": system.params.lambda_,
        "K": system.params.K,
        "alpha_h": system.params.alpha_h,
        "memory_order": system.params.memory_order,
        "memory_weights": system.params.memory_weights,
        "degeneracy_check": system.params.degeneracy_check,
        "omega_range_report": system.params.omega_range_report,
    }
    agents = [
        {
            "phi": agent.phi,
            "psi": agent.psi,
            "frequency": agent.frequency,
            "metadata": agent.metadata,
        }
        for agent in system.agents
    ]
    return _json_value({
        "name": system.name,
        "parts": system.parts,
        "resource": system.resource,
        "agents": agents,
        "params": params,
    })


def compile_program(systems):
    """Validate all declarations and return the versioned RONIN JSON IR."""
    compiled = []
    for system in systems.values():
        validate(system)
        validate_coherence(system.params)
        compiled.append(system_to_ir(system))
    return {
        "format": "ronin-ir",
        "ir_version": 1,
        "systems": compiled,
    }
