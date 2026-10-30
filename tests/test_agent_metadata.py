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
