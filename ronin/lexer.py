import re
from dataclasses import dataclass
from .errors import SyntaxError
@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    column: int
PATTERN = re.compile(r'(?P<SPACE>[ \\t\\r]+)|(?P<NEWLINE>\\n)|(?P<COMMENT>//[^\\n]*)|(?P<STRING>"(?:\\\\.|[^"\\\\])*")|(?P<NUMBER>(?:\\d+\\.\\d*|\\.\\d+|\\d+)(?:[eE][+-]?\\d+)?)|(?P<IDENT>[A-Za-z_][A-Za-z0-9_]*)|(?P<SYMBOL>[{}\\[\\](),:=])|(?P<OTHER>.)')
def lex(source):
    out=[]; line=1; col=1
    for m in PATTERN.finditer(source):
        k,v=m.lastgroup,m.group()
        if k in ("SPACE","COMMENT"): col+=len(v); continue
        if k=="NEWLINE": line+=1; col=1; continue
        if k=="OTHER": raise SyntaxError(f"Unexpected {v!r} at {line}:{col}")
        out.append(Token(k,v,line,col)); col+=len(v)
    out.append(Token("EOF","",line,col))
    return out
