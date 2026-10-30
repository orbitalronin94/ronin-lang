"""Interactive command console for working with loaded RONIN systems.

This is a command-oriented REPL, not yet a general-purpose expression evaluator.
"""
import json
import shlex
from dataclasses import asdict

from .diagnose import diagnose
from .parser import parse
from .simulator import simulate
from .solver import solve
from .validator import validate, validate_coherence


HELP = """Commands:
  :load PATH                 Parse and load all systems from a .ronin file
  :list                      List loaded systems
  :check NAME                Validate a loaded system
  :solve NAME                Solve a loaded system
  :diagnose NAME             Diagnose a loaded system
  :simulate NAME [STEPS] [SEED]
                             Simulate (defaults: 100 steps, no seed)
  :help                      Show this help
  :quit                      Exit the console

The console operates on complete system declarations loaded from files.
"""


def run_repl(input_fn=input, output_fn=print):
    systems = {}
    output_fn("RONIN interactive console. Type :help for commands.")
    while True:
        try:
            line = input_fn("ronin> ")
        except (EOFError, StopIteration):
            output_fn("")
            return
        try:
            words = shlex.split(line)
            if not words:
                continue
            command, *args = words
            if command in (":quit", ":q", ":exit"):
                output_fn("Bye.")
                return
            if command == ":help":
                output_fn(HELP)
                continue
            if command == ":load":
                if len(args) != 1:
                    raise ValueError("usage: :load PATH")
                with open(args[0], encoding="utf-8") as source_file:
                    loaded = parse(source_file.read())
                if not loaded:
                    raise ValueError("file contains no system declarations")
                systems.update(loaded)
                output_fn("Loaded: " + ", ".join(loaded))
                continue
            if command == ":list":
                output_fn("\n".join(sorted(systems)) if systems else "No systems loaded.")
                continue
            if command not in (":check", ":solve", ":diagnose", ":simulate"):
                raise ValueError(f"unknown command: {command} (try :help)")
            if not args:
                raise ValueError(f"usage: {command} NAME")
            name = args[0]
            if name not in systems:
                raise ValueError(f"unknown system: {name}")
            system = systems[name]
            if command == ":check":
                validate(system)
                validate_coherence(system.params)
                output_fn("OK")
            elif command == ":solve":
                output_fn(json.dumps(asdict(solve(system)), indent=2, default=str))
            elif command == ":diagnose":
                output_fn(json.dumps(asdict(diagnose(system)), indent=2, default=str))
            else:
                if len(args) > 3:
                    raise ValueError("usage: :simulate NAME [STEPS] [SEED]")
                steps = int(args[1]) if len(args) >= 2 else 100
                seed = int(args[2]) if len(args) == 3 else None
                output_fn(json.dumps(asdict(simulate(system, steps=steps, seed=seed)), indent=2, default=str))
        except Exception as error:
            output_fn(f"ERROR: {error}")
