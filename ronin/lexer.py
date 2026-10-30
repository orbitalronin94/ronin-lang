import re
from dataclasses import dataclass
from .errors import SyntaxError

@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    column: int

PATTERN = re.compile(
    r'(?P<SPACE>[ \t\r]+)|(?P<NEWLINE>\n)|(?P<COMMENT>//[^\n]*)|'
    r'(?P<STRING>"(?:\\.|[^"\\])*")|'
    r'(?P<NUMBER>(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?)|'
    r'(?P<IDENT>[A-Za-z_][A-Za-z0-9_]*)|(?P<SYMBOL>[{}\[\](),:=])|(?P<OTHER>.)'
)

def lex(source):
    out = []
    line = col = 1
    for match in PATTERN.finditer(source):
        kind, value = match.lastgroup, match.group()
        if kind in ("SPACE", "COMMENT"):
            col += len(value)
            continue
        if kind == "NEWLINE":
            line += 1
            col = 1
            continue
        if kind == "OTHER":
            raise SyntaxError(f"Unexpected {value!r} at {line}:{col}")
        out.append(Token(kind, value, line, col))
        col += len(value)
    out.append(Token("EOF", "", line, col))
    return out
