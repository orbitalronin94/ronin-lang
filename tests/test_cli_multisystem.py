from pathlib import Path

from ronin.cli import main


def test_list_prints_every_declared_system(capsys):
    fixture = Path(__file__).parents[1] / "examples" / "maquinas.ronin"
    assert main(["list", str(fixture)]) == 0
    assert capsys.readouterr().out.splitlines() == ["Maquinas"]


def test_check_validates_all_systems_when_no_name_is_given(capsys, tmp_path):
    source = """
    system First = {
      parts: 2, resource: 100,
      agents: [
        { phi: 0.5, psi: 0.5, frequency: 0.5 },
        { phi: 0.5, psi: 0.5, frequency: 0.5 }
      ]
    }
    system Second = {
      parts: 2, resource: 100,
      agents: [
        { phi: 0.6, psi: 0.5, frequency: 0.5 },
        { phi: 0.5, psi: 0.6, frequency: 0.5 }
      ]
    }
    """
    path = tmp_path / "multiple.ronin"
    path.write_text(source, encoding="utf-8")
    assert main(["check", str(path)]) == 0
    assert capsys.readouterr().out.strip() == "OK (2 systems)"


def test_solve_can_select_a_named_system(capsys, tmp_path):
    source = """
    system First = {
      parts: 2, resource: 100,
      agents: [
        { phi: 0.5, psi: 0.5, frequency: 0.5 },
        { phi: 0.5, psi: 0.5, frequency: 0.5 }
      ]
    }
    system Second = {
      parts: 2, resource: 100,
      agents: [
        { phi: 0.6, psi: 0.5, frequency: 0.5 },
        { phi: 0.5, psi: 0.6, frequency: 0.5 }
      ]
    }
    """
    path = tmp_path / "multiple.ronin"
    path.write_text(source, encoding="utf-8")
    assert main(["solve", str(path), "--system", "Second"]) == 0
    assert '"allocation"' in capsys.readouterr().out


def test_unknown_system_reports_available_names(capsys):
    fixture = Path(__file__).parents[1] / "examples" / "maquinas.ronin"
    assert main(["solve", str(fixture), "--system", "Missing"]) == 1
    assert "available systems: Maquinas" in capsys.readouterr().err


def test_existing_solve_invocation_remains_compatible(capsys):
    fixture = Path(__file__).parents[1] / "examples" / "maquinas.ronin"
    assert main(["solve", str(fixture)]) == 0
    assert '"allocation"' in capsys.readouterr().out
