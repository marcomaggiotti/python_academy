"""Advanced 04: Build an Interpreter.

The data classes (Token, AST nodes, errors) are given. Implement tokenize(),
parse(), unparse() and Interpreter. Read LESSON.md for the grammar.
Run: python academy.py check a4
"""

from __future__ import annotations

import math
import operator
from dataclasses import dataclass
from typing import Callable, Union


# ----- Given: errors ------------------------------------------------------------------

class CalcError(Exception):
    """Base error. `pos` is the 0-based index in the source (or None)."""

    def __init__(self, message: str, pos: int | None = None) -> None:
        super().__init__(message)
        self.pos = pos


class ParseError(CalcError):
    pass


class EvalError(CalcError):
    pass


# ----- Given: tokens -------------------------------------------------------------------

@dataclass(frozen=True)
class Token:
    kind: str      # "NUMBER", "NAME", "OP", "LPAREN", "RPAREN", "COMMA", "EQUALS", "END"
    value: object  # float for NUMBER, str otherwise ("" for END)
    pos: int


# ----- Given: AST nodes ---------------------------------------------------------------------

@dataclass(frozen=True)
class Num:
    value: float


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class UnaryOp:
    op: str          # "-" or "+"
    operand: "Node"


@dataclass(frozen=True)
class BinOp:
    op: str          # "+", "-", "*", "/", "%", "**"
    left: "Node"
    right: "Node"


@dataclass(frozen=True)
class Call:
    func: str
    args: tuple["Node", ...]


@dataclass(frozen=True)
class Assign:
    name: str
    value: "Node"


Node = Union[Num, Var, UnaryOp, BinOp, Call, Assign]


# ----- Challenges -----------------------------------------------------------------------------

def tokenize(src: str) -> list[Token]:
    """Turn source into tokens ending with Token("END", "", len(src)).

    OP values: "+", "-", "*", "/", "%", "**".  Numbers become floats.
    Unknown characters -> ParseError(f"unexpected character {ch!r}", pos).
    A malformed number such as "1.2.3" -> ParseError.

    >>> [t.kind for t in tokenize("x = 2**-1")]
    ['NAME', 'EQUALS', 'NUMBER', 'OP', 'OP', 'NUMBER', 'END']
    """
    raise NotImplementedError


def parse(src: str) -> Node:
    """Parse a single statement into an AST (see the grammar in LESSON.md).
    Errors -> ParseError with the position of the offending token, e.g.
      "1 +"      -> ParseError at pos 3 (the END token)
      "(1 + 2"   -> ParseError (expected ')')
      "1 2"      -> ParseError at pos 2 (unexpected trailing token)
      "3 = x"    -> ParseError (can only assign to a name)
    """
    raise NotImplementedError


def unparse(node: Node) -> str:
    """Turn an AST back into source, FULLY parenthesising binary operations and
    using the shortest number form (2.0 -> "2", 2.5 -> "2.5"):

      unparse(parse("1 + 2 * x"))      -> "(1 + (2 * x))"
      unparse(parse("-max(a, 2)"))     -> "-max(a, 2)"
      unparse(parse("y = 2 ** 3 ** 2"))-> "y = (2 ** (3 ** 2))"
    """
    raise NotImplementedError


class Interpreter:
    """Evaluates statements, keeping variables between calls.

      it = Interpreter()
      it.run("x = 4")       -> 4.0     (assignment returns the value)
      it.run("sqrt(x) * 2") -> 4.0
      it.variables          -> {"x": 4.0}   (a dict; `pi` and `e` are constants, not in it)

    - Built-in constants: pi, e (read-only: assigning to them -> EvalError)
    - Built-in functions: sqrt(x), abs(x), min(a, b, ...), max(a, b, ...), round(x)
      Wrong number of args for sqrt/abs/round -> EvalError. Unknown function -> EvalError.
    - Unknown variable -> EvalError(f"undefined variable {name!r}")
    - Division or modulo by zero -> EvalError
    - sqrt of a negative -> EvalError
    - Every successful run() also stores its result in the variable "_".
    """

    def __init__(self) -> None:
        raise NotImplementedError
