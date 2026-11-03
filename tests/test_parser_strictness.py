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
        'system S = { parts: true, resource: 10, agents: [{phi: 0.5, psi: 0.5, frequency: 1.0}] }',
        'system S = { parts: 2, resource: true, agents: [{phi: 0.5, psi: 0.5, frequency: 1.0}] }',
        'system S = { parts: 2, resource: 10, agents: [{phi: true, psi: 0.5, frequency: 1.0}] }',
        'system S = { parts: 2, resource: 10, agents: [{phi: 0.5, psi: 0.5, frequency: 1.0}], params: {alpha: true} }',
        'system S = { parts: 2, resource: 10, agents: [{phi: 0.5, psi: 0.5, frequency: 1.0}], params: {memory_order: true} }',
    ],
)
def test_parser_rejects_booleans_where_numbers_are_required(source):
    with pytest.raises(SyntaxError):
        parse(source)


def test_parser_rejects_unknown_parameter_names():
    source = (
        'system S = { parts: 2, resource: 10, agents: '
        '[{phi: 0.5, psi: 0.5, frequency: 1.0}], params: {alhpa: 1.0} }'
    )
    with pytest.raises(SyntaxError, match="Unknown params field: alhpa"):
        parse(source)



def test_parser_rejects_unknown_system_fields():
    source = (
        'system S = { parts: 2, resource: 10, agents: '
        '[{phi: 0.5, psi: 0.5, frequency: 1.0}], resorce: 12 }'
    )
    with pytest.raises(SyntaxError, match="Unknown system field: resorce"):
        parse(source)



@pytest.mark.parametrize(
    "params",
    [
        "{degeneracy_check: 1}",
        "{omega_range_report: \"false\"}",
        "{memory_weights: \"not-an-array\"}",
        "{memory_weights: [1, true]}",
    ],
)
def test_parser_rejects_invalid_extended_parameter_types(params):
    source = (
        'system S = { parts: 2, resource: 10, agents: '
        '[{phi: 0.5, psi: 0.5, frequency: 1.0}], params: ' + params + ' }'
    )
    with pytest.raises(SyntaxError):
        parse(source)

def test_parser_reports_line_and_column_for_missing_separator():
    source = (
        "system S = {\n"
        "  parts 2,\n"
        "  resource: 1,\n"
        "  agents: [{phi: 1, psi: 1, frequency: 1}]\n"
        "}"
    )
    with pytest.raises(SyntaxError, match=r"at 2:9"):
        parse(source)

def test_parser_rejects_isolated_unicode_surrogate_escape():
    source = r'system S = { parts: 1, resource: 1, agents: [{phi: 1, psi: 1, frequency: 1, note: "\uD800"}] }'
    with pytest.raises(SyntaxError, match="Invalid Unicode surrogate sequence"):
        parse(source)

@pytest.mark.parametrize(
    "raw_value",
    ["line one\nline two", "before\tafter", "carriage\rreturn"],
)
def test_parser_rejects_unescaped_control_characters_in_strings(raw_value):
    source = (
        'system S = { parts: 1, resource: 1, agents: '
        '[{phi: 1, psi: 1, frequency: 1, note: "' + raw_value + '"}] }'
    )
    with pytest.raises((SyntaxError, ValueError)):
        parse(source)

def test_parser_rejects_isolated_unicode_surrogate_in_object_key():
    source = r'system S = { parts: 1, resource: 1, agents: [{phi: 1, psi: 1, frequency: 1, meta: {"\uD800": 1}}] }'
    with pytest.raises(SyntaxError, match="Invalid Unicode surrogate sequence"):
        parse(source)

@pytest.mark.parametrize("separator", ["\\u00a0", "\\u000b", "\\u000c"])
def test_parser_rejects_whitespace_outside_ascii_space_tab_cr_lf(separator):
    source = (
        "system" + separator
        + "S = { parts: 1, resource: 1, agents: "
        + "[{phi: 1, psi: 1, frequency: 1}] }"
    )
    with pytest.raises(SyntaxError, match="Unexpected"):
        parse(source)
