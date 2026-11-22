"""Module 07 — Type Hints, Generics, Protocols & Enums.

Write fully type-annotated code (bonus: make `mypy --strict` happy on this file).
Run: python academy.py check 07
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import (
    Callable,
    Generic,
    Iterable,
    Iterator,
    Protocol,
    Sequence,
    TypedDict,
    TypeVar,
    runtime_checkable,
)

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


# --- Generic functions --------------------------------------------------------

def first(items: Sequence[T], default: T | None = None) -> T | None:
    """First item, or `default` if the sequence is empty."""
    raise NotImplementedError


def group_by(items: Iterable[V], key: Callable[[V], K]) -> dict[K, list[V]]:
    """Group items into a dict keyed by key(item), preserving order within groups."""
    raise NotImplementedError


# --- Generic class ----------------------------------------------------------------

class Stack(Generic[T]):
    """A LIFO stack.

      s: Stack[int] = Stack()
      s.push(1); s.push(2)
      s.peek() -> 2 ; s.pop() -> 2 ; len(s) -> 1
      pop/peek on empty -> IndexError("empty stack")
      iter(s) yields from top to bottom
      Stack.from_iterable([1, 2, 3]) -> stack with 3 on top  (classmethod)
    """

    def __init__(self) -> None:
        raise NotImplementedError


# --- Protocols ------------------------------------------------------------------

@runtime_checkable
class SupportsArea(Protocol):
    def area(self) -> float: ...


def total_area(shapes: Iterable[object]) -> float:
    """Sum the areas of the objects that satisfy SupportsArea; ignore the rest."""
    raise NotImplementedError


# --- TypedDict ---------------------------------------------------------------------

class User(TypedDict):
    name: str
    age: int
    email: str


def parse_user(raw: dict[str, object]) -> User:
    """Validate a raw dict and return a User.
      - all three keys required (KeyError otherwise)
      - name/email must be str, age must be int (not bool) -> TypeError otherwise
      - email must contain exactly one "@" -> ValueError otherwise
      - extra keys are dropped
    """
    raise NotImplementedError


# --- Enum-based state machine --------------------------------------------------------

class OrderStatus(Enum):
    """Order lifecycle:  PENDING -> PAID -> SHIPPED -> DELIVERED
    Any status except DELIVERED may go to CANCELLED. CANCELLED and DELIVERED are final.

    Implement:
      - status.can_transition_to(other) -> bool
      - status.is_final  (property)
      - OrderStatus.parse("paid") -> OrderStatus.PAID (case-insensitive; ValueError if unknown)
    """

    PENDING = auto()
    PAID = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()


class Order:
    """Order(id) starts PENDING. order.advance(new_status) changes status if the
    transition is allowed, else raises ValueError. order.history is a list of
    every status it has had, in order (starting with PENDING).
    """

    def __init__(self, order_id: int) -> None:
        raise NotImplementedError


# --- A generic Result type -------------------------------------------------------------

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T


@dataclass(frozen=True)
class Err:
    error: str


def safe_sqrt(x: float) -> Ok[float] | Err:
    """Ok(sqrt(x)) for x >= 0, else Err("negative input")."""
    raise NotImplementedError


def unwrap_all(results: Iterable[Ok[T] | Err]) -> list[T]:
    """Return all Ok values; if ANY result is an Err, raise ValueError with the
    first error message. Use `match`/`case` with class patterns (case Ok(value=v)).
    """
    raise NotImplementedError
