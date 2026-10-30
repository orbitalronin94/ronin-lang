import argparse
import json
import sys
from dataclasses import asdict

from . import __version__
from .diagnose import diagnose
from .errors import RoninError
from .parser import parse
from .simulator import simulate
from .solver import solve
from .validator import validate, validate_coherence


def _load_first_system(path):
    with open(path, encoding="utf-8") as source_file:
        systems = parse(source_file.read())
    if not systems:
        raise RoninError("no system declarations found")
    return next(iter(systems.values()))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ronin")
    parser.add_argument(
        "--version", action="version", version=f"RONIN {__version__}"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    for name in ("check", "solve"):
        command = commands.add_parser(name)
        command.add_argument("file")
        if name == "solve":
            command.add_argument("--delta", type=float, default=None)

    command = commands.add_parser("simulate")
    command.add_argument("file")
    command.add_argument("--steps", type=int, default=100)
    command.add_argument("--seed", type=int)

    command = commands.add_parser("diagnose")
    command.add_argument("file")
    command.add_argument("--bootstrap", type=int, default=0)

    args = parser.parse_args(argv)
    try:
        system = _load_first_system(args.file)
        if args.command == "check":
            validate(system)
            validate_coherence(system.params)
            print("OK")
            return 0
        if args.command == "solve":
            result = solve(system, delta=args.delta)
        elif args.command == "simulate":
            result = simulate(system, steps=args.steps, seed=args.seed)
        else:
            result = diagnose(system, bootstrap=args.bootstrap)
        print(json.dumps(asdict(result), indent=2, default=str))
        return 0
    except RoninError as error:
        print(f"RONIN ERROR: {error}", file=sys.stderr)
        return getattr(error, "code", 3)
    except (OSError, ValueError) as error:
        print(f"RONIN ERROR: {error}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
