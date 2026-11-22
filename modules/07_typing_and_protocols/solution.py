"""Reference solutions for Module 07."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Generic, Iterable, Iterator, Protocol, Sequence, TypedDict, TypeVar, runtime_checkable

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def first(items: Sequence[T], default: T | None = None) -> T | None:
    return items[0] if items else default


def group_by(items: Iterable[V], key: Callable[[V], K]) -> dict[K, list[V]]:
    groups: dict[K, list[V]] = {}
    for item in items:
        groups.setdefault(key(item), []).append(item)
    return groups


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    @classmethod
    def from_iterable(cls, items: Iterable[T]) -> Stack[T]:
        stack: Stack[T] = cls()
        for item in items:
            stack.push(item)
        return stack

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("empty stack")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise IndexError("empty stack")
        return self._items[-1]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return reversed(self._items)


@runtime_checkable
class SupportsArea(Protocol):
    def area(self) -> float: ...


def total_area(shapes: Iterable[object]) -> float:
    return sum(s.area() for s in shapes if isinstance(s, SupportsArea))


class User(TypedDict):
    name: str
    age: int
    email: str


def parse_user(raw: dict[str, object]) -> User:
    name, age, email = raw["name"], raw["age"], raw["email"]
    if not isinstance(name, str) or not isinstance(email, str):
        raise TypeError("name and email must be strings")
    if not isinstance(age, int) or isinstance(age, bool):
        raise TypeError("age must be an int")
    if email.count("@") != 1:
        raise ValueError(f"invalid email: {email!r}")
    return User(name=name, age=age, email=email)


class OrderStatus(Enum):
    PENDING = auto()
    PAID = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()

    @property
    def is_final(self) -> bool:
        return self in (OrderStatus.DELIVERED, OrderStatus.CANCELLED)

    def can_transition_to(self, other: OrderStatus) -> bool:
        if self.is_final:
            return False
        if other is OrderStatus.CANCELLED:
            return True
        return other in _NEXT.get(self, ())

    @classmethod
    def parse(cls, text: str) -> OrderStatus:
        try:
            return cls[text.strip().upper()]
        except KeyError:
            raise ValueError(f"unknown status: {text!r}") from None


_NEXT = {
    OrderStatus.PENDING: (OrderStatus.PAID,),
    OrderStatus.PAID: (OrderStatus.SHIPPED,),
    OrderStatus.SHIPPED: (OrderStatus.DELIVERED,),
}


class Order:
    def __init__(self, order_id: int) -> None:
        self.id = order_id
        self.history: list[OrderStatus] = [OrderStatus.PENDING]

    @property
    def status(self) -> OrderStatus:
        return self.history[-1]

    def advance(self, new_status: OrderStatus) -> None:
        if not self.status.can_transition_to(new_status):
            raise ValueError(f"cannot go from {self.status.name} to {new_status.name}")
        self.history.append(new_status)


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T


@dataclass(frozen=True)
class Err:
    error: str


def safe_sqrt(x: float) -> Ok[float] | Err:
    return Ok(math.sqrt(x)) if x >= 0 else Err("negative input")


def unwrap_all(results: Iterable[Ok[T] | Err]) -> list[T]:
    values: list[T] = []
    for result in results:
        match result:
            case Ok(value=v):
                values.append(v)
            case Err(error=msg):
                raise ValueError(msg)
    return values
