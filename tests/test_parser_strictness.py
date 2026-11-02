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


@pytest.mark.parametrize(
    "source",
    [
        'system S = { parts: 2, resource: 1, agents: [{phi: true, psi: 0.5, frequency: 0.5}, {phi: 0.5, psi: 0.5, frequency: 0.5}] }',
        'system S = { parts: 2, resource: true, agents: [{phi: 0.5, psi: 0.5, frequency: 0.5}, {phi: 0.5, psi: 0.5, frequency: 0.5}] }',
        'system S = { parts: 2, resource: 1, agents: [{phi: 0.5, psi: 0.5, frequency: 0.5}, {phi: 0.5, psi: 0.5, frequency: 0.5}], params: { alpha: true } }',
        'system S = { parts: 2, resource: 1, agents: [{phi: 0.5, psi: 0.5, frequency: 0.5}, {phi: 0.5, psi: 0.5, frequency: 0.5}], params: { degeneracy_check: "false" } }',
        'system S = { parts: 2, resource: 1, agents: [{phi: 0.5, psi: 0.5, frequency: 0.5}, {phi: 0.5, psi: 0.5, frequency: 0.5}], params: { model: 1 } }',
    ],
)
def test_parser_rejects_boolean_and_wrongly_typed_numeric_or_parameter_values(source):
    with pytest.raises(SyntaxError):
        parse(source)


def test_parser_rejects_unknown_params_fields():
    source = (
        'system S = { parts: 2, resource: 1, agents: '
        '[{phi: 0.5, psi: 0.5, frequency: 0.5}, '
        '{phi: 0.5, psi: 0.5, frequency: 0.5}], params: { typo: 1 } }'
    )
    with pytest.raises(SyntaxError, match="Unknown params field: typo"):
        parse(source)


def test_parser_accepts_lowercase_k_alias_like_rust():
    source = (
        'system S = { parts: 2, resource: 1, agents: '
        '[{phi: 0.5, psi: 0.5, frequency: 0.5}, '
        '{phi: 0.5, psi: 0.5, frequency: 0.5}], '
        'params: { model: "hill", k: 0.5 } }'
    )
    assert parse(source)["S"].params.K == pytest.approx(0.5)


def test_parser_rejects_boolean_memory_weights_and_string_numbers():
    sources = [
        'system S = { parts: 2, resource: 1, agents: [{phi: 0.5, psi: 0.5, frequency: 0.5}, {phi: 0.5, psi: 0.5, frequency: 0.5}], params: { memory_weights: [true] } }',
        'system S = { parts: "2", resource: 1, agents: [{phi: 0.5, psi: 0.5, frequency: 0.5}, {phi: 0.5, psi: 0.5, frequency: 0.5}] }',
        'system S = { parts: 2, resource: 1, agents: [{phi: 0.5, psi: 0.5, frequency: 0.5}, {phi: 0.5, psi: 0.5, frequency: 0.5}], params: { K: "inf" } }',
    ]
    for source in sources:
        with pytest.raises(SyntaxError):
            parse(source)
