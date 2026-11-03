import csv
import io

from ronin.cli import main


def test_run_csv_exports_one_row_per_agent(capsys, tmp_path):
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

    assert main(["run", str(path), "--format", "csv"]) == 0
    rows = list(csv.DictReader(io.StringIO(capsys.readouterr().out)))

    assert len(rows) == 4
    assert rows[0].keys() == {
        "system", "agent_index", "model", "fitness", "allocation"
    }
    assert [row["system"] for row in rows] == [
        "First", "First", "Second", "Second"
    ]
    assert [row["agent_index"] for row in rows] == ["1", "2", "1", "2"]
    assert abs(sum(float(row["allocation"]) for row in rows[:2]) - 100) < 1e-9
    assert abs(sum(float(row["allocation"]) for row in rows[2:]) - 200) < 1e-9


def test_run_json_remains_the_default_format(capsys):
    from pathlib import Path
    import json

    fixture = Path(__file__).parents[1] / "examples" / "maquinas.ronin"
    assert main(["run", str(fixture)]) == 0
    assert "Maquinas" in json.loads(capsys.readouterr().out)


def test_csv_writer_round_trips_comma_quote_and_newline_fields():
    from types import SimpleNamespace

    from ronin.cli import _write_run_csv

    name = 'System, "quoted"\\nsecond line\\r\\nthird line'
    model = 'model, "quoted"\\nvariant'
    system = SimpleNamespace(params=SimpleNamespace(model=model))
    output = io.StringIO(newline="")

    _write_run_csv(
        {name: system},
        {name: {"fitness": [0.5], "allocation": [10.0]}},
        output,
    )

    rows = list(csv.DictReader(io.StringIO(output.getvalue())))
    assert len(rows) == 1
    assert rows[0]["system"] == name
    assert rows[0]["model"] == model
    assert rows[0]["fitness"] == "0.5"
    assert rows[0]["allocation"] == "10"
