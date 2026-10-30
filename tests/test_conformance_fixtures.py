from pathlib import Path

import pytest

from ronin.diagnose import diagnose
from ronin.errors import SemanticError
from ronin.parser import parse
from ronin.solver import solve

FIXTURES = Path(__file__).parent / "fixtures" / "conformance"


@pytest.mark.parametrize(
    "filename",
    ["pusfre.ronin", "ces.ronin", "hill.ronin", "ces_hill.ronin", "full_order1.ronin"],
)
def test_shared_positive_fixtures_validate_and_solve(filename):
    systems = parse((FIXTURES / filename).read_text(encoding="utf-8"))
    assert len(systems) == 1
    system = next(iter(systems.values()))
    result = solve(system)
    assert len(result.fitness) == system.parts
    assert len(result.allocation) == system.parts
    assert sum(result.allocation) == pytest.approx(system.resource, abs=1e-9)


@pytest.mark.parametrize(
    "filename",
    [
        "invalid_frequency_sum.ronin",
        "invalid_pusfre_lambda.ronin",
        "invalid_alpha.ronin",
        "full_order3_unsupported.ronin",
    ],
)
def test_shared_negative_fixtures_are_rejected(filename):
    systems = parse((FIXTURES / filename).read_text(encoding="utf-8"))
    with pytest.raises(SemanticError):
        solve(next(iter(systems.values())))


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("degeneracy_active.ronin", "active"),
        ("degeneracy_inactive.ronin", "inactive"),
        ("degeneracy_unknown.ronin", "unknown"),
    ],
)
def test_shared_diagnostic_fixtures(filename, expected):
    systems = parse((FIXTURES / filename).read_text(encoding="utf-8"))
    report = diagnose(next(iter(systems.values())))
    assert report.degeneracy == expected
