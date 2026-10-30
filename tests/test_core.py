from pathlib import Path
import pytest
from ronin.parser import parse
from ronin.solver import solve
from ronin.semantics import hill,ces_combine
from ronin.validator import validate
from ronin.simulator import simulate
from ronin.diagnose import diagnose
from ronin.errors import SemanticError
ROOT=Path(__file__).parents[1]
def test_maquinas_reference():
    s=solve(parse((ROOT/"examples/maquinas.ronin").read_text())["Maquinas"])
    assert s.fitness==pytest.approx([.48,.20])
    assert s.allocation==pytest.approx([70.5882352941,29.4117647059])
def test_parser_and_validation():
    s=parse((ROOT/"examples/pesca.ronin").read_text())["Pesca"]
    assert validate(s)
def test_invalid_frequency_sum():
    with pytest.raises(SemanticError):
        validate(parse('system X = { parts: 2, resource: 10, agents: [{phi:.5,psi:.5,frequency:.4},{phi:.5,psi:.5,frequency:.4}] }')["X"])
def test_hill_identity_and_midpoint():
    assert hill(.5,float("inf"),1.5)==.5
    assert hill(.5,.5,1)==pytest.approx(.5)
def test_ces_arithmetic_mean_at_lambda_one():
    assert ces_combine(.8,1,.6,1)==pytest.approx(.8)
def test_simulation_reproducible():
    s=parse((ROOT/"examples/maquinas.ronin").read_text())["Maquinas"]
    assert simulate(s,10,42).history==simulate(s,10,42).history
def test_diagnose_result_shape():
    s=parse((ROOT/"examples/maquinas.ronin").read_text())["Maquinas"]
    assert diagnose(s).degeneracy in ("active","inactive")
