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

    @staticmethod
    def add_field(fields, key, value, scope):
        if key in fields:
            raise SyntaxError(f"Duplicate {scope} field: {key}")
        fields[key] = value

    @staticmethod
    def number(value, field):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field} must be numeric")
        return float(value)

    @staticmethod
    def string(value, field):
        if not isinstance(value, str):
            raise ValueError(f"{field} must be a string")
        return value

    def value(self):
        token = self.token
        if token.kind == "NUMBER":
            self.take()
            return float(token.value)
        if token.kind == "STRING":
            self.take()
            return json.loads(token.value)
        if token.value == "∞":
            self.take()
            return math.inf
        if token.kind == "IDENT":
            self.take()
            value = token.value
            if value.lower() in ("inf", "infinity"):
                return math.inf
            if value.lower() == "null":
                return None
            if value.lower() in ("true", "false"):
                return value.lower() == "true"
            return value
        if token.value == "{":
            self.take()
            values = {}
            while self.token.value != "}":
                if self.token.kind == "EOF":
                    raise SyntaxError("Unterminated object")
                key_token = self.token
                if key_token.kind == "STRING":
                    key = json.loads(self.take().value)
                elif key_token.kind == "IDENT":
                    key = self.take().value
                else:
                    raise SyntaxError(
                        f"Expected object key at {key_token.line}:{key_token.column}"
                    )
                self.expect(":")
                self.add_field(values, key, self.value(), "object")
                if self.token.value == ",":
                    self.take()
                elif self.token.value != "}":
                    raise SyntaxError(
                        f"Expected ',' or '}}' at {self.token.line}:{self.token.column}"
                    )
            self.take()
            return values
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
            self.add_field(fields, key, value, "agent")
        self.take()
        if self.token.value == ",":
            self.take()
        try:
            required = {key: fields.pop(key) for key in ("phi", "psi", "frequency")}
            return Agent(
                phi=self.number(required["phi"], "phi"),
                psi=self.number(required["psi"], "psi"),
                frequency=self.number(required["frequency"], "frequency"),
                metadata=fields,
            )
        except KeyError as error:
            raise SyntaxError(f"Missing agent field: {error.args[0]}") from error
        except (TypeError, ValueError) as error:
            raise SyntaxError(f"Invalid agent numeric value: {error}") from error

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
            self.add_field(fields, key, value, "params")
        self.take()
        if self.token.value == ",":
            self.take()
        allowed = {
            "alpha", "gamma", "sigma", "coexistence_delta", "model", "lambda",
            "K", "alpha_h", "memory_order", "memory_weights",
            "degeneracy_check", "omega_range_report",
        }
        unknown = sorted(set(fields) - allowed)
        if unknown:
            raise SyntaxError(f"Unknown params field: {unknown[0]}")
        K = fields.get("K", math.inf)
        if isinstance(K, str) and K.lower() in ("inf", "infinity", "∞"):
            K = math.inf
        memory_order = fields.get("memory_order", 1)
        try:
            memory_order = self.number(memory_order, "memory_order")
            if not memory_order.is_integer() or memory_order < 0:
                raise ValueError("memory_order must be a non-negative integer")
            return Params(
                alpha=self.number(fields.get("alpha", 1.0), "alpha"),
                gamma=self.number(fields.get("gamma", 0.4), "gamma"),
                sigma=self.number(fields.get("sigma", 0.0), "sigma"),
                coexistence_delta=self.number(fields.get("coexistence_delta", 0.05), "coexistence_delta"),
                model=self.string(fields.get("model", "pusfre"), "model"),
                lambda_=self.number(fields.get("lambda", 0.0), "lambda"),
                K=self.number(K, "K"),
                alpha_h=self.number(fields.get("alpha_h", 1.0), "alpha_h"),
                memory_order=int(memory_order),
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
                    value = self.agents()
                elif key == "params":
                    value = self.params()
                else:
                    value = self.value()
                    if self.token.value == ",":
                        self.take()
                self.add_field(fields, key, value, f"system {name}")
            self.take()
            if name in systems:
                raise SyntaxError(f"Duplicate system {name}")
            unknown = sorted(set(fields) - {"parts", "resource", "agents", "params"})
            if unknown:
                raise SyntaxError(f"Unknown system field: {unknown[0]}")
            try:
                parts = self.number(fields["parts"], "parts")
                if not parts.is_integer() or parts <= 0:
                    raise ValueError("parts must be a positive integer")
                systems[name] = System(
                    name=name,
                    parts=int(parts),
                    resource=self.number(fields["resource"], "resource"),
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
