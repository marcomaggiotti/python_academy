"""Module 03 — OOP & the Python Data Model.

Each class below has a spec in its docstring. Fill in the bodies, add any
methods you need. Run: python academy.py check 03
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import total_ordering


class Vector:
    """An immutable 2D vector.

    Required behaviour:
      - Vector(3, 4) stores floats or ints as .x and .y (read-only properties;
        assigning to v.x must raise AttributeError).
      - repr(Vector(3, 4)) == "Vector(3, 4)"
      - ==, and hashable (equal vectors have equal hashes)
      - v + w, v - w  -> Vector  (return NotImplemented for non-Vectors)
      - v * 3 and 3 * v -> scaled Vector
      - abs(v) -> length (float); bool(v) is False only for Vector(0, 0)
      - x, y = v  (iterable)
      - v.dot(w) -> dot product
    """

    def __init__(self, x: float, y: float) -> None:
        raise NotImplementedError


class Temperature:
    """Temperature stored in Celsius.

      - Temperature(25).celsius == 25
      - .celsius is a property; setting below -273.15 raises ValueError
        (also in __init__).
      - .fahrenheit property (read & write) converts: F = C * 9/5 + 32
      - Temperature.from_fahrenheit(212).celsius == 100   (classmethod)
      - Temperatures compare with == and < (and therefore <=, >, >= via
        functools.total_ordering) based on celsius.
    """

    def __init__(self, celsius: float) -> None:
        raise NotImplementedError


@dataclass(frozen=True)
class Money:
    """Immutable amount of money, stored in integer cents.

      - Money(1050, "EUR")  -> 10.50 EUR.  Currency defaults to "EUR".
      - Currency must be a 3-letter uppercase code, else ValueError
        (validate in __post_init__).
      - str(Money(1050, "EUR")) == "10.50 EUR"
      - Money.parse("10.50 EUR") -> Money(1050, "EUR")  (classmethod)
      - m1 + m2 with the same currency -> new Money; different currencies
        raise ValueError.
      - m * 3 -> Money (int multiplier only)
      - m.split(3) -> list of 3 Money objects that sum exactly to m, with the
        leftover cents distributed to the first parts:
        Money(100).split(3) -> [34, 33, 33] cents
    """

    cents: int
    currency: str = "EUR"


class Shape(ABC):
    """Abstract base class. Subclasses must implement area() and perimeter().

    describe() is implemented here and returns e.g.
        "Circle: area=3.14, perimeter=6.28"
    (class name, both values rounded to 2 decimals)
    """

    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

    def describe(self) -> str:
        raise NotImplementedError


class Circle(Shape):
    """Circle(radius). Radius must be > 0 else ValueError."""

    def __init__(self, radius: float) -> None:
        raise NotImplementedError


class Rectangle(Shape):
    """Rectangle(width, height). Both must be > 0 else ValueError."""

    def __init__(self, width: float, height: float) -> None:
        raise NotImplementedError


class Square(Rectangle):
    """Square(side) — a Rectangle with equal sides. Reuse Rectangle via super()."""

    def __init__(self, side: float) -> None:
        raise NotImplementedError


class Playlist:
    """A sequence of song titles.

      - Playlist("name", ["a", "b"]) ; .name attribute
      - len(p), p[0], p[-1], "a" in p, for song in p
      - p[1:3] returns a NEW Playlist (same name) with that slice
      - p + q returns a new Playlist named "<p.name> + <q.name>"
      - p.add(song) appends; duplicates are ignored
      - repr(p) == "Playlist('name', 2 songs)"  (use "1 song" for one)
    """

    def __init__(self, name: str, songs: list[str] | None = None) -> None:
        raise NotImplementedError
