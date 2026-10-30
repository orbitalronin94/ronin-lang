import random

from .model import Simulation
from .validator import validate, validate_coherence


def _project_simplex(values):
    projected = [max(0.0, value) for value in values]
    total = sum(projected)
    if total == 0:
        return [1.0 / len(projected)] * len(projected)
    return [value / total for value in projected]


def simulate(system, steps=100, seed=None):
    validate(system)
    validate_coherence(system.params)
    if steps < 1:
        raise ValueError("steps must be >= 1")
    if system.params.model == "full" and system.params.memory_order > 1:
        raise ValueError("full temporal-memory simulation is not implemented")

    rng = random.Random(seed)
    state = [agent.frequency for agent in system.agents]
    history = [state.copy()]
    extinction_events = []
    alpha = system.params.alpha
    sigma = system.params.sigma

    for _ in range(steps):
        weights = [
            agent.phi * agent.psi * (max(value, 0.0) ** alpha)
            for agent, value in zip(system.agents, state)
        ]
        total = sum(weights)
        target = (
            [weight / total for weight in weights]
            if total
            else [1.0 / len(state)] * len(state)
        )
        proposal = [
            value + 0.5 * (target_value - value) + rng.gauss(0.0, sigma / 10.0)
            for value, target_value in zip(state, target)
        ]
        state = _project_simplex(proposal)
        extinction_events.extend(
            index
            for index, value in enumerate(state)
            if value <= 1e-12 and index not in extinction_events
        )
        history.append(state.copy())

    survivability = sum(value > 1e-12 for value in state) / len(state)
    return Simulation(
        history=history,
        final_state=state,
        steps=steps,
        seed=seed,
        extinction_events=extinction_events,
        survivability=survivability,
    )
