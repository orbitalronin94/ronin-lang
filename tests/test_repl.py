from pathlib import Path

from ronin.repl import run_repl


def test_repl_loads_lists_checks_and_solves_systems(tmp_path):
    fixture = Path(__file__).parents[1] / "examples" / "maquinas.ronin"
    commands = iter([
        f":load {fixture}",
        ":list",
        ":check Maquinas",
        ":solve Maquinas",
        ":quit",
    ])
    output = []
    run_repl(input_fn=lambda _prompt: next(commands), output_fn=output.append)
    transcript = "\n".join(output)
    assert "Loaded: Maquinas" in transcript
    assert "Maquinas" in transcript
    assert "OK" in transcript
    assert '"allocation"' in transcript
    assert "Bye." in transcript


def test_repl_reports_unknown_system_and_continues(tmp_path):
    commands = iter([":solve Missing", ":quit"])
    output = []
    run_repl(input_fn=lambda _prompt: next(commands), output_fn=output.append)
    assert any("unknown system: Missing" in line for line in output)
    assert output[-1] == "Bye."
