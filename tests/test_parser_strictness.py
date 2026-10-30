import pytest

from ronin.errors import SyntaxError
from ronin.parser import parse


@pytest.mark.parametrize(
    ("source", "message"),
    [
        (
            'system S = { parts: 2, parts: 3, resource: 10, agents: '
            '[{phi: 0.5, psi: 0.5, frequency: 1.0}] }',
            "Duplicate system S field: parts",
        ),
        (
            'system S = { parts: 2, resource: 10, agents: '
            '[{phi: 0.5, phi: 0.6, psi: 0.5, frequency: 1.0}] }',
            "Duplicate agent field: phi",
        ),
        (
            'system S = { parts: 2, resource: 10, agents: '
            '[{phi: 0.5, psi: 0.5, frequency: 1.0}], '
            'params: { alpha: 1.0, alpha: 2.0 } }',
            "Duplicate params field: alpha",
        ),
        (
            'system S = { parts: 2, resource: 10, agents: '
            '[{phi: 0.5, psi: 0.5, frequency: 1.0}], '
            'params: {}, params: {} }',
            "Duplicate system S field: params",
        ),
    ],
)
def test_parser_rejects_duplicate_fields(source, message):
    with pytest.raises(SyntaxError, match=message):
        parse(source)


def test_parser_keeps_distinct_agent_metadata_fields():
    parsed = parse(
        'system S = { parts: 1, resource: 10, agents: '
        '[{phi: 0.5, psi: 0.5, frequency: 1.0, role: "worker", tools: ["net"]}] }'
    )
    assert parsed["S"].agents[0].metadata == {
        "role": "worker",
        "tools": ["net"],
    }
