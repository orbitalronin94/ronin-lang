import json
import math

from .errors import SyntaxError
from .lexer import lex
from .model import Agent, Params, System


class Parser:
    def __init__(self, source):
        self.tokens = lex(source)
        self.index = 0

    @property
    def token(self):
        return self.tokens[self.index]

    def take(self):
        token = self.token
        self.index += 1
        return token

    def expect(self, value):
        token = self.take()
        if token.value != value:
            raise SyntaxError(
                f"Expected {value!r} at {token.line}:{token.column}, got {token.value!r}"
            )
        return token

    def identifier(self):
        token = self.take()
        if token.kind != "IDENT":
            raise SyntaxError(f"Expected identifier at {token.line}:{token.column}")
        return token.value

    def value(self):
        token = self.token
        if token.kind == "NUMBER":
            self.take()
            return float(token.value)
        if token.kind == "STRING":
            self.take()
            return json.loads(token.value)
        if token.kind == "IDENT":
            self.take()
            value = token.value
            if value.lower() in ("inf", "infinity"):
                return math.inf
            if value in ("true", "false"):
                return value == "true"
            return value
        if token.value == "[":
            self.take()
            values = []
            while self.token.value != "]":
                if self.token.kind == "EOF":
                    raise SyntaxError("Unterminated array")
                values.append(self.value())
                if self.token.value == ",":
                    self.take()
                elif self.token.value != "]":
                    raise SyntaxError(
                        f"Expected ',' or ']' at {self.token.line}:{self.token.column}"
                    )
            self.take()
            return values
        raise SyntaxError(f"Expected value at {token.line}:{token.column}")

    def field(self):
        key = self.identifier()
        self.expect(":")
        value = self.value()
        if self.token.value == ",":
            self.take()
        return key, value

    def agent(self):
        self.expect("{")
        fields = {}
        while self.token.value != "}":
            if self.token.kind == "EOF":
                raise SyntaxError("Unterminated agent")
            key, value = self.field()
            fields[key] = value
        self.take()
        if self.token.value == ",":
            self.take()
        try:
            return Agent(
                phi=float(fields["phi"]),
                psi=float(fields["psi"]),
                frequency=float(fields["frequency"]),
            )
        except KeyError as error:
            raise SyntaxError(f"Missing agent field: {error.args[0]}") from error

    def agents(self):
        self.expect("[")
        result = []
        while self.token.value != "]":
            if self.token.kind == "EOF":
                raise SyntaxError("Unterminated agents list")
            result.append(self.agent())
        self.take()
        if self.token.value == ",":
            self.take()
        return result

    def params(self):
        self.expect("{")
        fields = {}
        while self.token.value != "}":
            if self.token.kind == "EOF":
                raise SyntaxError("Unterminated params block")
            key, value = self.field()
            fields[key] = value
        self.take()
        if self.token.value == ",":
            self.take()
        K = fields.get("K", math.inf)
        if isinstance(K, str) and K.lower() in ("inf", "infinity"):
            K = math.inf
        try:
            return Params(
                alpha=float(fields.get("alpha", 1.0)),
                gamma=float(fields.get("gamma", 0.4)),
                sigma=float(fields.get("sigma", 0.0)),
                coexistence_delta=float(fields.get("coexistence_delta", 0.05)),
                model=str(fields.get("model", "pusfre")),
                lambda_=float(fields.get("lambda", 0.0)),
                K=float(K),
                alpha_h=float(fields.get("alpha_h", 1.0)),
                memory_order=int(fields.get("memory_order", 1)),
                memory_weights=fields.get("memory_weights"),
                degeneracy_check=bool(fields.get("degeneracy_check", False)),
                omega_range_report=bool(fields.get("omega_range_report", False)),
            )
        except (TypeError, ValueError) as error:
            raise SyntaxError(f"Invalid params value: {error}") from error

    def program(self):
        systems = {}
        while self.token.kind != "EOF":
            self.expect("system")
            name = self.identifier()
            self.expect("=")
            self.expect("{")
            fields = {}
            while self.token.value != "}":
                if self.token.kind == "EOF":
                    raise SyntaxError(f"Unterminated system {name}")
                key = self.identifier()
                self.expect(":")
                if key == "agents":
                    fields[key] = self.agents()
                elif key == "params":
                    fields[key] = self.params()
                else:
                    fields[key] = self.value()
                    if self.token.value == ",":
                        self.take()
            self.take()
            if name in systems:
                raise SyntaxError(f"Duplicate system {name}")
            try:
                systems[name] = System(
                    name=name,
                    parts=int(fields["parts"]),
                    resource=float(fields["resource"]),
                    agents=fields["agents"],
                    params=fields.get("params", Params()),
                )
            except KeyError as error:
                raise SyntaxError(f"Missing system field: {error.args[0]}") from error
            except (TypeError, ValueError) as error:
                raise SyntaxError(f"Invalid system value: {error}") from error
        return systems


def parse(source):
    return Parser(source).program()
