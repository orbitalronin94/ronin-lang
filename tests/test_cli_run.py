import json

from ronin.cli import main


def test_run_solves_every_system_and_emits_one_json_document(capsys, tmp_path):
    source = """
    system First = {
      parts: 2, resource: 100,
      agents: [
        { phi: 0.8, psi: 1.0, frequency: 0.6 },
        { phi: 0.5, psi: 1.0, frequency: 0.4 }
      ]
    }
    system Second = {
      parts: 2, resource: 200,
      agents: [
        { phi: 0.6, psi: 1.0, frequency: 0.5 },
        { phi: 0.4, psi: 1.0, frequency: 0.5 }
      ]
    }
    """
    path = tmp_path / "project.ronin"
    path.write_text(source, encoding="utf-8")

    assert main(["run", str(path)]) == 0
    output = json.loads(capsys.readouterr().out)

    assert list(output) == ["First", "Second"]
    assert len(output["First"]["allocation"]) == 2
    assert len(output["Second"]["allocation"]) == 2
    assert abs(sum(output["First"]["allocation"]) - 100.0) < 1e-9
    assert abs(sum(output["Second"]["allocation"]) - 200.0) < 1e-9


def test_run_empty_file_returns_a_runtime_error(capsys, tmp_path):
    path = tmp_path / "empty.ronin"
    path.write_text("// no systems\n", encoding="utf-8")

    assert main(["run", str(path)]) == 3
    assert "no system declarations found" in capsys.readouterr().err


def test_run_applies_delta_override_to_every_system(capsys, tmp_path):
    source = """
    system One = {
      parts: 2, resource: 100,
      agents: [
        { phi: 0.8, psi: 1.0, frequency: 0.6 },
        { phi: 0.5, psi: 1.0, frequency: 0.4 }
      ]
    }
    """
    path = tmp_path / "one.ronin"
    path.write_text(source, encoding="utf-8")

    assert main(["run", str(path), "--delta", "0.02"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["One"]["k_min"] is not None
