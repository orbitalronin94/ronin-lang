from pathlib import Path

from ronin.parser import parse


ROOT = Path(__file__).parents[1]
EXAMPLES = sorted((ROOT / "examples").glob("*.ronin"))


def test_every_repository_example_is_accepted_by_the_python_parser():
    assert len(EXAMPLES) >= 30
    failures = []
    for path in EXAMPLES:
        try:
            systems = parse(path.read_text(encoding="utf-8"))
            if not systems:
                failures.append(f"{path.name}: no system declarations")
        except Exception as error:  # report every broken fixture in one test run
            failures.append(f"{path.name}: {type(error).__name__}: {error}")
    assert not failures, "\n".join(failures)
