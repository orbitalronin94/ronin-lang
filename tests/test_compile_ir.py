import json
from pathlib import Path

from ronin.cli import main
from ronin.errors import SemanticError
from ronin.ir import compile_program
from ronin.parser import parse


ROOT = Path(__file__).parents[1]


def test_compile_emits_versioned_json_ir(capsys):
    fixture = ROOT / "examples" / "maquinas.ronin"

    assert main(["compile", str(fixture)]) == 0
    result = json.loads(capsys.readouterr().out)

    assert result["format"] == "ronin-ir"
    assert result["ir_version"] == 1
    assert result["systems"][0]["name"] == "Maquinas"
    assert result["systems"][0]["params"]["lambda"] == 0.0
    assert result["systems"][0]["params"]["K"] == "inf"


def test_compile_writes_ir_to_requested_file(capsys, tmp_path):
    fixture = ROOT / "examples" / "maquinas.ronin"
    destination = tmp_path / "compiled.json"

    assert main(["compile", str(fixture), "--output", str(destination)]) == 0
    assert capsys.readouterr().out == ""
    result = json.loads(destination.read_text(encoding="utf-8"))
    assert result["systems"][0]["parts"] == 2


def test_compiled_ir_preserves_extended_agent_metadata():
    source = """
    system Coastal = {
      parts: 2, resource: 10,
      agents: [
        { phi: 0.6, psi: 0.7, frequency: 0.5, niche: [0.2, 0.4], tools: ["net"] },
        { phi: 0.5, psi: 0.8, frequency: 0.5 }
      ]
    }
    """
    ir = compile_program(parse(source))

    assert ir["systems"][0]["agents"][0]["metadata"] == {
        "niche": [0.2, 0.4],
        "tools": ["net"],
    }


def test_compile_rejects_semantically_invalid_systems():
    source = """
    system Invalid = {
      parts: 2, resource: 10,
      agents: [
        { phi: 0.6, psi: 0.7, frequency: 0.4 },
        { phi: 0.5, psi: 0.8, frequency: 0.5 }
      ]
    }
    """
    try:
        compile_program(parse(source))
    except SemanticError as error:
        assert "frequencies must sum to 1" in str(error)
    else:
        raise AssertionError("invalid system was compiled")
