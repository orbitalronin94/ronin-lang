import json, math
from .lexer import lex
from .model import Agent, Params, System
from .errors import SyntaxError
class Parser:
    def __init__(self,s): self.ts=lex(s); self.i=0
    @property
    def t(self): return self.ts[self.i]
    def take(self): t=self.t; self.i+=1; return t
    def expect(self,v):
        t=self.take()
        if t.value!=v: raise SyntaxError(f"Expected {v!r} at {t.line}:{t.column}")
    def ident(self):
        t=self.take()
        if t.kind!="IDENT": raise SyntaxError(f"Expected identifier at {t.line}:{t.column}")
        return t.value
    def value(self):
        t=self.take()
        if t.kind=="NUMBER": return float(t.value)
        if t.kind=="STRING": return json.loads(t.value)
        if t.kind=="IDENT":
            if t.value.lower() in ("inf","infinity"): return math.inf
            if t.value in ("true","false"): return t.value=="true"
            return t.value
        raise SyntaxError(f"Expected value at {t.line}:{t.column}")
    def field(self):
        k=self.ident(); self.expect(":"); v=self.value()
        if self.t.value==",": self.take()
        return k,v
    def agent(self):
        self.expect("{"); d={}
        while self.t.value!="}":
            if self.t.kind=="EOF": raise SyntaxError("Unterminated agent")
            k,v=self.field(); d[k]=v
        self.take()
        if self.t.value==",": self.take()
        try: return Agent(float(d["phi"]),float(d["psi"]),float(d["frequency"]))
        except KeyError as e: raise SyntaxError(f"Missing agent field {e.args[0]}")
    def agents(self):
        self.expect("["); a=[]
        while self.t.value!="]":
            if self.t.kind=="EOF": raise SyntaxError("Unterminated agents")
            a.append(self.agent())
        self.take()
        if self.t.value==",": self.take()
        return a
    def params(self):
        self.expect("{"); d={}
        while self.t.value!="}":
            if self.t.kind=="EOF": raise SyntaxError("Unterminated params")
            k,v=self.field(); d[k]=v
        self.take()
        if self.t.value==",": self.take()
        return Params(alpha=float(d.get("alpha",1)),gamma=float(d.get("gamma",.4)),
          sigma=float(d.get("sigma",0)),coexistence_delta=float(d.get("coexistence_delta",.05)),
          model=d.get("model","pusfre"),lambda_=float(d.get("lambda",0)),K=float(d.get("K",math.inf)),
          alpha_h=float(d.get("alpha_h",1)),memory_order=int(d.get("memory_order",1)),
          memory_weights=d.get("memory_weights"),degeneracy_check=bool(d.get("degeneracy_check",False)),
          omega_range_report=bool(d.get("omega_range_report",False)))
    def program(self):
        systems={}
        while self.t.kind!="EOF":
            self.expect("system"); name=self.ident(); self.expect("="); self.expect("{"); d={}
            while self.t.value!="}":
                if self.t.kind=="EOF": raise SyntaxError("Unterminated system")
                k=self.ident(); self.expect(":")
                if k=="agents": d[k]=self.agents()
                elif k=="params": d[k]=self.params()
                else:
                    d[k]=self.value()
                    if self.t.value==",": self.take()
            self.take()
            if name in systems: raise SyntaxError(f"Duplicate system {name}")
            try: systems[name]=System(name,int(d["parts"]),float(d["resource"]),d["agents"],d.get("params",Params()))
            except KeyError as e: raise SyntaxError(f"Missing system field {e.args[0]}")
        return systems
def parse(source): return Parser(source).program()
