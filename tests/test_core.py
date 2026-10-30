from dataclasses import replace
from pathlib import Path

import pytest

from ronin.diagnose import diagnose
from ronin.errors import SemanticError
from ronin.parser import parse
from ronin.lexer import PATTERN, lex
from ronin.semantics import ces_combine, hill, k_min
from ronin.simulator import simulate
from ronin.solver import solve
from ronin.validator import validate, validate_coherence

ROOT = Path(__file__).parents[1]
MAQ = (ROOT / "examples" / "maquinas.ronin").read_text(encoding="utf-8")
PES = (ROOT / "examples" / "pesca.ronin").read_text(encoding="utf-8")


def test_maquinas_normative_result():
    result = solve(parse(MAQ)["Maquinas"])
    assert result.fitness == pytest.approx([0.48, 0.20], abs=1e-12)
    assert result.allocation == pytest.approx(
        [70.58823529411765, 29.411764705882355], abs=1e-9
    )
    assert sum(result.allocation) == pytest.approx(100.0, abs=1e-9)
    assert result.model_used == "pusfre"
    assert result.coexistence is True


def test_parser_and_pesca_validation():
    system = parse(PES)["Pesca"]
    assert system.parts == 5
    assert validate(system)


def test_parser_supports_strings_signed_values_and_memory_arrays():
    source = '''
    system Extended = {
      parts: 2, resource: 10,
      agents: [
        { phi: 0.5, psi: 0.6, frequency: 0.4, name: "A" },
        { phi: 0.7, psi: 0.8, frequency: 0.6 }
      ],
      params: {
        model: "ces", lambda: -0.25, memory_order: 1,
        memory_weights: [1.0], degeneracy_check: true
      }
    }
    '''
    system = parse(source)["Extended"]
    assert system.params.model == "ces"
    assert system.params.lambda_ == pytest.approx(-0.25)
    assert system.params.memory_weights == [1.0]
    assert system.params.degeneracy_check is True
    assert validate_coherence(system.params)
    assert parse('system Default = { parts: 2, resource: 1, agents: [{phi:0.5,psi:0.5,frequency:0.5},{phi:0.5,psi:0.5,frequency:0.5}], params: { memory_weights: null } }')["Default"].params.memory_weights is None


def test_invalid_frequency_sum():
    source = MAQ.replace("frequency: 0.4", "frequency: 0.3")
    with pytest.raises(SemanticError):
        validate(parse(source)["Maquinas"])


def test_hill_identity_midpoint_and_zero():
    assert hill(0.5, float("inf"), 1.5) == 0.5
    assert hill(0.5, 0.5, 1.0) == pytest.approx(0.5)
    assert hill(0.0, 0.5, 1.0) == 0.0


def test_ces_arithmetic_mean_at_lambda_one():
    assert ces_combine(0.8, 1.0, 0.6, 1.0) == pytest.approx(0.8)


def test_ces_near_zero_uses_geometric_mean_not_pusfre():
    source = MAQ.replace("params: {", 'params: { model: "ces", lambda: 1e-7,')
    system = parse(source)["Maquinas"]
    result = solve(system)
    expected = [
        (agent.phi * agent.psi * agent.frequency) ** (1 / 3)
        for agent in system.agents
    ]
    assert result.fitness == pytest.approx(expected, abs=1e-9)
    assert result.fitness != pytest.approx([0.48, 0.20], abs=1e-9)


def test_ces_combine_clamps_nonpositive_log_inputs():
    assert ces_combine(0.0, -1.0, 0.5, 1e-7) > 0


def test_lexer_has_all_named_groups_and_tokenizes_comments():
    assert set(PATTERN.groupindex) == {
        "SPACE", "NEWLINE", "COMMENT", "STRING", "NUMBER", "IDENT", "SYMBOL", "OTHER"
    }
    tokens = lex('name: "ronin" // comentario\nvalue: 1.2')
    assert [token.kind for token in tokens[:-1]] == [
        "IDENT", "SYMBOL", "STRING", "NEWLINE", "IDENT", "SYMBOL", "NUMBER"
    ]


def test_model_coherence_is_enforced():
    source = MAQ.replace("params: {", 'params: { model: "pusfre", lambda: 0.5,')
    with pytest.raises(SemanticError):
        solve(parse(source)["Maquinas"])


def test_ces_rejects_finite_hill_threshold():
    source = MAQ.replace(
        "params: {", 'params: { model: "ces", lambda: 0.5, K: 0.5,'
    )
    with pytest.raises(SemanticError):
        solve(parse(source)["Maquinas"])


def test_k_min_uses_configured_delta():
    system = parse(MAQ)["Maquinas"]
    assert k_min(system) > 0
    changed = replace(system, params=replace(system.params, coexistence_delta=0.01))
    assert k_min(changed) < k_min(system)


def test_degeneracy_active_for_narrow_omega_range():
    source = '''
    system Narrow = {
      parts: 3, resource: 100,
      agents: [
        { phi: 0.5, psi: 0.5, frequency: 0.3 },
        { phi: 0.5, psi: 0.5, frequency: 0.4 },
        { phi: 0.5, psi: 0.5, frequency: 0.3 }
      ],
      params: { model: "ces_hill", lambda: 0.5, K: 0.5, alpha_h: 1.5,
                degeneracy_check: true }
    }
    '''
    report = diagnose(parse(source)["Narrow"])
    assert report.degeneracy == "active"
    assert not report.lambda_identifiable
    assert not report.K_identifiable
    assert not report.alpha_h_identifiable


def test_degeneracy_inactive_requires_three_full_orders():
    source = '''
    system Wide = {
      parts: 3, resource: 100,
      agents: [
        { phi: 0.5, psi: 0.5, frequency: 0.0009 },
        { phi: 0.5, psi: 0.5, frequency: 0.0090 },
        { phi: 0.5, psi: 0.5, frequency: 0.9901 }
      ],
      params: { model: "ces_hill", lambda: 0.5, K: 0.5, alpha_h: 1.5 }
    }
    '''
    report = diagnose(parse(source)["Wide"])
    assert report.degeneracy == "inactive"
    assert report.omega_range_orders >= 3.0


def test_source_degeneracy_example_is_below_threshold():
    source = '''
    system Borderline = {
      parts: 3, resource: 1,
      agents: [
        { phi: 0.5, psi: 0.5, frequency: 0.001 },
        { phi: 0.5, psi: 0.5, frequency: 0.01 },
        { phi: 0.5, psi: 0.5, frequency: 0.989 }
      ],
      params: { model: "ces_hill", lambda: 0.5, K: 0.5, alpha_h: 1.5 }
    }
    '''
    report = diagnose(parse(source)["Borderline"])
    assert report.omega_range_orders == pytest.approx(2.9952, abs=1e-3)
    assert report.degeneracy == "active"


def test_simulation_is_seed_reproducible_and_normalized():
    system = parse(MAQ)["Maquinas"]
    first = simulate(system, steps=10, seed=42)
    second = simulate(system, steps=10, seed=42)
    assert first.history == second.history
    assert first.final_state == second.final_state
    assert sum(first.final_state) == pytest.approx(1.0)


def test_full_memory_is_not_silently_approximated():
    source = MAQ.replace(
        "params: {",
        'params: { model: "full", lambda: 0.5, K: 0.5, memory_order: 3,'
    )
    with pytest.raises(SemanticError, match="not implemented"):
        solve(parse(source)["Maquinas"])
