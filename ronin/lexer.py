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
    r'(?P<SPACE>[ \\t\\r]+)|(?P<NEWLINE>\\n)|(?P<COMMENT>//[^\\n]*)|'
    r'(?P<STRING>"(?:\\\\.|[^"\\\\])*")|'
    r'(?P<NUMBER>[+-]?(?:\\d+\\.\\d*|\\.\\d+|\\d+)(?:[eE][+-]?\\d+)?)|'
    r'(?P<IDENT>[A-Za-z_][A-Za-z0-9_]*)|'
    r'(?P<SYMBOL>[{}\\[\\](),:=])|(?P<OTHER>.)'
)


def lex(source):
    tokens = []
    line = column = 1
    for match in PATTERN.finditer(source):
        kind, value = match.lastgroup, match.group()
        if kind in ("SPACE", "COMMENT"):
            column += len(value)
            continue
        if kind == "NEWLINE":
            line += 1
            column = 1
            continue
        if kind == "OTHER":
            raise SyntaxError(f"Unexpected {value!r} at {line}:{column}")
        tokens.append(Token(kind, value, line, column))
        column += len(value)
    tokens.append(Token("EOF", "", line, column))
    return tokens
