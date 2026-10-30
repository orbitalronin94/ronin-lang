import argparse,json,sys
from dataclasses import asdict
from . import __version__
from .parser import parse
from .validator import validate,validate_coherence
from .solver import solve
from .simulator import simulate
from .diagnose import diagnose
from .errors import RoninError
def main(argv=None):
    p=argparse.ArgumentParser(prog="ronin"); p.add_argument("--version",action="version",version=f"RONIN {__version__}")
    sub=p.add_subparsers(dest="cmd",required=True)
    for name in ("check","solve"): sub.add_parser(name).add_argument("file")
    q=sub.add_parser("simulate"); q.add_argument("file"); q.add_argument("--steps",type=int,default=100); q.add_argument("--seed",type=int)
    q=sub.add_parser("diagnose"); q.add_argument("file"); q.add_argument("--bootstrap",type=int,default=0)
    a=p.parse_args(argv)
    try:
        with open(a.file,encoding="utf-8") as f: systems=parse(f.read())
        if not systems: raise RoninError("no system declarations")
        s=next(iter(systems.values()))
        if a.cmd=="check": validate(s); validate_coherence(s.params); print("OK"); return 0
        r=solve(s) if a.cmd=="solve" else simulate(s,a.steps,a.seed) if a.cmd=="simulate" else diagnose(s,a.bootstrap)
        print(json.dumps(asdict(r),indent=2,default=str)); return 0
    except RoninError as e: print(f"RONIN ERROR: {e}",file=sys.stderr); return e.code
    except Exception as e: print(f"RONIN ERROR: {e}",file=sys.stderr); return 3
if __name__=="__main__": raise SystemExit(main())
