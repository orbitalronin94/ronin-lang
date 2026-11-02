from pathlib import Path

from ronin.parser import parse


ROOT = Path(__file__).parents[1]
RUNTIME_EXAMPLES = [
    ROOT / "examples" / "maquinas.ronin",
    ROOT / "examples" / "maquinas_ces.ronin",
    ROOT / "examples" / "pesca.ronin",
    ROOT / "examples" / "degeneracy_active.ronin",
    ROOT / "examples" / "degeneracy_inactive.ronin",
]


def test_every_executable_repository_example_is_accepted_by_the_python_parser():
    for path in RUNTIME_EXAMPLES:
        systems = parse(path.read_text(encoding="utf-8"))
        assert systems, f"{path.name}: no system declarations"
