import pytest

from ronin.errors import SyntaxError
from ronin.parser import parse


def test_extended_agent_metadata_is_preserved_without_changing_core_fields():
    source = """
    system Fishery = {
      parts: 2,
      resource: 100,
      agents: [
        {
          phi: 0.6,
          psi: 0.9,
          frequency: 0.5,
          niche: [0.1, 0.3, 0.5],
          tools: ["longline", "hook"],
          protocol: "artisanal"
        },
        { phi: 0.5, psi: 0.8, frequency: 0.5 }
      ]
    }
    """
    system = parse(source)["Fishery"]

    assert system.agents[0].phi == 0.6
    assert system.agents[0].psi == 0.9
    assert system.agents[0].frequency == 0.5
    assert system.agents[0].metadata == {
        "niche": [0.1, 0.3, 0.5],
        "tools": ["longline", "hook"],
        "protocol": "artisanal",
    }
    assert system.agents[1].metadata == {}


def test_agent_metadata_does_not_change_solver_results():
    from ronin.solver import solve

    source = """
    system Plain = {
      parts: 2, resource: 100,
      agents: [
        { phi: 0.8, psi: 1.0, frequency: 0.6 },
        { phi: 0.5, psi: 1.0, frequency: 0.4 }
      ]
    }
    """
    extended = source.replace(
        "frequency: 0.6",
        'frequency: 0.6, niche: [0.2, 0.4], protocol: "test"',
    )
    plain_result = solve(parse(source)["Plain"])
    extended_result = solve(parse(extended)["Plain"])

    assert extended_result.fitness == plain_result.fitness
    assert extended_result.allocation == plain_result.allocation


def test_agent_metadata_preserves_nested_objects_and_mixed_values():
    source = r'''
    system Nested = {
      parts: 2, resource: 10,
      agents: [
        {
          phi: 0.6, psi: 0.7, frequency: 0.5,
          profile: {
            enabled: true,
            region: "north",
            empty: null,
            values: [1, "two", false],
            nested: {"quoted-key": "value"}
          }
        },
        { phi: 0.5, psi: 0.8, frequency: 0.5 }
      ]
    }
    '''
    systems = parse(source)
    profile = systems["Nested"].agents[0].metadata["profile"]
    assert profile == {
        "enabled": True,
        "region": "north",
        "empty": None,
        "values": [1.0, "two", False],
        "nested": {"quoted-key": "value"},
    }


def test_agent_metadata_rejects_duplicate_nested_object_keys():
    source = r'''
    system Duplicate = {
      parts: 2, resource: 10,
      agents: [
        { phi: 0.6, psi: 0.7, frequency: 0.5, profile: { key: 1, "key": 2 } },
        { phi: 0.5, psi: 0.8, frequency: 0.5 }
      ]
    }
    '''
    with pytest.raises(SyntaxError, match="Duplicate object field: key"):
        parse(source)
