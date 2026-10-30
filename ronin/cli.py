import argparse
import csv
import json
import sys
from dataclasses import asdict

from . import __version__
from .diagnose import diagnose
from .errors import RoninError
from .ir import compile_program
from .parser import parse
from .simulator import simulate
from .solver import solve
from .validator import validate, validate_coherence


def _load_systems(path):
    with open(path, encoding="utf-8") as source_file:
        systems = parse(source_file.read())
    if not systems:
        raise RoninError("no system declarations found")
    return systems


def _select_system(systems, name=None):
    if name is None:
        return next(iter(systems.values()))
    try:
        return systems[name]
    except KeyError as error:
        available = ", ".join(systems)
        raise RoninError(
            f"unknown system {name!r}; available systems: {available}"
        ) from error


def _write_run_csv(systems, results, stream):
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("system", "agent_index", "model", "fitness", "allocation"))
    for name, system in systems.items():
        result = results[name]
        for index, (fitness, allocation) in enumerate(
            zip(result["fitness"], result["allocation"]), start=1
        ):
            writer.writerow((
                name,
                index,
                system.params.model,
                format(fitness, ".17g"),
                format(allocation, ".17g"),
            ))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ronin")
    parser.add_argument(
        "--version", action="version", version=f"RONIN {__version__}"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    command = commands.add_parser("list", help="list systems declared in a file")
    command.add_argument("file")

    command = commands.add_parser(
        "compile", help="validate a RONIN file and emit normalized JSON IR"
    )
    command.add_argument("file")
    command.add_argument(
        "-o", "--output", help="write JSON IR to this path instead of stdout"
    )

    command = commands.add_parser(
        "run", help="solve every system declared in a RONIN file"
    )
    command.add_argument("file")
    command.add_argument(
        "--delta", type=float, default=None,
        help="coexistence threshold override applied to every system",
    )
    command.add_argument(
        "--format", choices=("json", "csv"), default="json",
        help="result format (default: json)",
    )

    for name in ("check", "solve"):
        command = commands.add_parser(name)
        command.add_argument("file")
        command.add_argument("--system", help="system name (default: first declaration)")
        if name == "solve":
            command.add_argument("--delta", type=float, default=None)

    command = commands.add_parser("simulate")
    command.add_argument("file")
    command.add_argument("--system", help="system name (default: first declaration)")
    command.add_argument("--steps", type=int, default=100)
    command.add_argument("--seed", type=int)

    command = commands.add_parser("diagnose")
    command.add_argument("file")
    command.add_argument("--system", help="system name (default: first declaration)")
    command.add_argument("--bootstrap", type=int, default=0)

    commands.add_parser("repl", help="start the interactive RONIN command console")

    args = parser.parse_args(argv)
    try:
        if args.command == "repl":
            from .repl import run_repl
            run_repl()
            return 0

        systems = _load_systems(args.file)
        if args.command == "list":
            for name in systems:
                print(name)
            return 0

        if args.command == "compile":
            ir = compile_program(systems)
            output = json.dumps(ir, indent=2, ensure_ascii=False, allow_nan=False)
            if args.output:
                with open(args.output, "w", encoding="utf-8") as output_file:
                    output_file.write(output + "\n")
            else:
                print(output)
            return 0

        if args.command == "run":
            results = {
                name: asdict(solve(system, delta=args.delta))
                for name, system in systems.items()
            }
            if args.format == "csv":
                _write_run_csv(systems, results, sys.stdout)
            else:
                print(json.dumps(results, indent=2, default=str))
            return 0

        if args.command == "check" and args.system is None:
            for system in systems.values():
                validate(system)
                validate_coherence(system.params)
            print(f"OK ({len(systems)} systems)")
            return 0

        system = _select_system(systems, getattr(args, "system", None))
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
