"""Answers for Advanced 04, with explanations."""

from __future__ import annotations

import math
import operator
import re
from dataclasses import dataclass
from typing import Union


class CalcError(Exception):
    def __init__(self, message, pos=None):
        super().__init__(message)
        self.pos = pos


class ParseError(CalcError):
    pass


class EvalError(CalcError):
    pass


@dataclass(frozen=True)
class Token:
    kind: str
    value: object
    pos: int


@dataclass(frozen=True)
class Num:
    value: float


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class UnaryOp:
    op: str
    operand: "Node"


@dataclass(frozen=True)
class BinOp:
    op: str
    left: "Node"
    right: "Node"


@dataclass(frozen=True)
class Call:
    func: str
    args: tuple


@dataclass(frozen=True)
class Assign:
    name: str
    value: "Node"


Node = Union[Num, Var, UnaryOp, BinOp, Call, Assign]


# --- Tokenizer ------------------------------------------------------------------
# One regex with named alternatives, tried at the current position. Order matters:
# "**" must come before "*". A number followed straight away by "." or a digit
# (e.g. "1.2.3") is rejected by the lookahead check below.

_TOKEN_RE = re.compile(
    r"""
    (?P<WS>\s+)
  | (?P<NUMBER>(?:\d+\.\d*|\.\d+|\d+))
  | (?P<NAME>[A-Za-z_]\w*)
  | (?P<OP>\*\*|[-+*/%])
  | (?P<LPAREN>\()
  | (?P<RPAREN>\))
  | (?P<COMMA>,)
  | (?P<EQUALS>=)
    """,
    re.VERBOSE,
)


def tokenize(src):
    tokens, pos = [], 0
    while pos < len(src):
        m = _TOKEN_RE.match(src, pos)
        if not m:
            raise ParseError(f"unexpected character {src[pos]!r}", pos)
        kind, text = m.lastgroup, m.group()
        if kind == "NUMBER":
            if m.end() < len(src) and (src[m.end()] == "." or src[m.end()].isalpha()):
                raise ParseError(f"malformed number near {src[pos:m.end() + 1]!r}", pos)
            tokens.append(Token("NUMBER", float(text), pos))
        elif kind != "WS":
            tokens.append(Token(kind, text, pos))
        pos = m.end()
    tokens.append(Token("END", "", len(src)))
    return tokens


# --- Parser ---------------------------------------------------------------------
# One method per grammar rule. Loops give left associativity (1 - 2 - 3 is
# (1 - 2) - 3); recursion on the right gives right associativity for "**".

class _Parser:
    def __init__(self, src):
        self.tokens = tokenize(src)
        self.i = 0

    def peek(self):
        return self.tokens[self.i]

    def advance(self):
        tok = self.tokens[self.i]
        self.i += 1
        return tok

    def accept(self, kind, *values):
        tok = self.peek()
        if tok.kind == kind and (not values or tok.value in values):
            return self.advance()
        return None

    def expect(self, kind, what):
        tok = self.accept(kind)
        if tok is None:
            bad = self.peek()
            found = "end of input" if bad.kind == "END" else repr(bad.value)
            raise ParseError(f"expected {what}, found {found}", bad.pos)
        return tok

    def fail(self):
        tok = self.peek()
        found = "end of input" if tok.kind == "END" else repr(tok.value)
        raise ParseError(f"unexpected {found}", tok.pos)

    # statement := NAME "=" expr | expr
    def statement(self):
        if self.peek().kind == "NAME" and self.tokens[self.i + 1].kind == "EQUALS":
            name = self.advance().value
            self.advance()
            node = Assign(name, self.expr())
        else:
            node = self.expr()
            if self.peek().kind == "EQUALS":
                raise ParseError("can only assign to a name", self.peek().pos)
        if self.peek().kind != "END":
            self.fail()
        return node

    def expr(self):
        node = self.term()
        while tok := self.accept("OP", "+", "-"):
            node = BinOp(tok.value, node, self.term())
        return node

    def term(self):
        node = self.unary()
        while tok := self.accept("OP", "*", "/", "%"):
            node = BinOp(tok.value, node, self.unary())
        return node

    def unary(self):
        if tok := self.accept("OP", "-", "+"):
            return UnaryOp(tok.value, self.unary())
        return self.power()

    def power(self):
        base = self.primary()
        if self.accept("OP", "**"):
            return BinOp("**", base, self.unary())  # recursion = right-assoc
        return base

    def primary(self):
        tok = self.peek()
        if tok.kind == "NUMBER":
            self.advance()
            return Num(tok.value)
        if tok.kind == "NAME":
            self.advance()
            if self.accept("LPAREN"):
                args = []
                if not self.accept("RPAREN"):
                    args.append(self.expr())
                    while self.accept("COMMA"):
                        args.append(self.expr())
                    self.expect("RPAREN", "')'")
                return Call(tok.value, tuple(args))
            return Var(tok.value)
        if self.accept("LPAREN"):
            node = self.expr()
            self.expect("RPAREN", "')'")
            return node
        self.fail()


def parse(src):
    return _Parser(src).statement()


def _fmt_number(x):
    return str(int(x)) if float(x).is_integer() else repr(x)


def unparse(node):
    match node:
        case Num(value):
            return _fmt_number(value)
        case Var(name):
            return name
        case UnaryOp(op, operand):
            return f"{op}{unparse(operand)}"
        case BinOp(op, left, right):
            return f"({unparse(left)} {op} {unparse(right)})"
        case Call(func, args):
            return f"{func}({', '.join(unparse(a) for a in args)})"
        case Assign(name, value):
            return f"{name} = {unparse(value)}"
    raise TypeError(f"not an AST node: {node!r}")


# --- Evaluator ------------------------------------------------------------------

_BINOPS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "%": operator.mod,
    "**": operator.pow,
}
_CONSTANTS = {"pi": math.pi, "e": math.e}


def _fixed(n, fn):
    """Wrap a function that takes exactly n arguments."""

    def call(*args):
        if len(args) != n:
            raise EvalError(f"expected {n} argument(s), got {len(args)}")
        return fn(*args)

    return call


def _sqrt(x):
    if x < 0:
        raise EvalError("sqrt of negative number")
    return math.sqrt(x)


def _variadic(fn):
    def call(*args):
        if not args:
            raise EvalError("expected at least 1 argument")
        return fn(args)

    return call


_FUNCTIONS = {
    "sqrt": _fixed(1, _sqrt),
    "abs": _fixed(1, abs),
    "round": _fixed(1, lambda x: float(round(x))),
    "min": _variadic(min),
    "max": _variadic(max),
}


class Interpreter:
    def __init__(self):
        self.variables = {}

    def run(self, src):
        result = self.evaluate(parse(src))
        self.variables["_"] = result
        return result

    def evaluate(self, node):
        match node:
            case Num(value):
                return value
            case Var(name):
                if name in _CONSTANTS:
                    return _CONSTANTS[name]
                try:
                    return self.variables[name]
                except KeyError:
                    raise EvalError(f"undefined variable {name!r}") from None
            case UnaryOp(op, operand):
                value = self.evaluate(operand)
                return -value if op == "-" else +value
            case BinOp(op, left, right):
                a, b = self.evaluate(left), self.evaluate(right)
                try:
                    return float(_BINOPS[op](a, b))
                except ZeroDivisionError:
                    raise EvalError("division by zero") from None
                except (OverflowError, TypeError) as exc:
                    raise EvalError(str(exc)) from exc
            case Call(func, args):
                fn = _FUNCTIONS.get(func)
                if fn is None:
                    raise EvalError(f"unknown function {func!r}")
                return float(fn(*(self.evaluate(a) for a in args)))
            case Assign(name, value):
                if name in _CONSTANTS:
                    raise EvalError(f"cannot assign to constant {name!r}")
                result = self.evaluate(value)
                self.variables[name] = result
                return result
        raise EvalError(f"cannot evaluate {node!r}")


if __name__ == "__main__":
    # A tiny REPL: python advanced/04_build_an_interpreter/solution.py
    it = Interpreter()
    while True:
        try:
            line = input("calc> ")
        except EOFError:
            break
        if not line.strip():
            continue
        try:
            print(it.run(line))
        except CalcError as exc:
            if exc.pos is not None:
                print(" " * (exc.pos + 6) + "^")
            print(f"error: {exc}")
