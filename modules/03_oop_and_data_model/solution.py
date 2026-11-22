"""Reference solutions for Module 03."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import total_ordering


class Vector:
    __slots__ = ("_x", "_y")

    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __repr__(self):
        return f"{type(self).__name__}({self._x!r}, {self._y!r})"

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __iter__(self):
        yield self.x
        yield self.y

    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector(self.x * scalar, self.y * scalar)

    __rmul__ = __mul__

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(self.x or self.y)

    def dot(self, other):
        return self.x * other.x + self.y * other.y


ABSOLUTE_ZERO = -273.15


@total_ordering
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < ABSOLUTE_ZERO:
            raise ValueError("temperature below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5 / 9

    @classmethod
    def from_fahrenheit(cls, f):
        return cls((f - 32) * 5 / 9)

    def __eq__(self, other):
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius == other.celsius

    def __lt__(self, other):
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius < other.celsius

    def __repr__(self):
        return f"Temperature({self.celsius!r})"


@dataclass(frozen=True)
class Money:
    cents: int
    currency: str = "EUR"

    def __post_init__(self):
        if not (len(self.currency) == 3 and self.currency.isalpha() and self.currency.isupper()):
            raise ValueError(f"invalid currency code: {self.currency!r}")

    def __str__(self):
        sign = "-" if self.cents < 0 else ""
        whole, frac = divmod(abs(self.cents), 100)
        return f"{sign}{whole}.{frac:02d} {self.currency}"

    @classmethod
    def parse(cls, text):
        amount, currency = text.split()
        whole, _, frac = amount.partition(".")
        sign = -1 if whole.startswith("-") else 1
        cents = abs(int(whole)) * 100 + int(frac.ljust(2, "0")[:2] or 0)
        return cls(sign * cents, currency)

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if other.currency != self.currency:
            raise ValueError("cannot add different currencies")
        return Money(self.cents + other.cents, self.currency)

    def __mul__(self, factor):
        if not isinstance(factor, int):
            return NotImplemented
        return Money(self.cents * factor, self.currency)

    __rmul__ = __mul__

    def split(self, parts):
        base, extra = divmod(self.cents, parts)
        return [Money(base + (1 if i < extra else 0), self.currency) for i in range(parts)]


class Shape(ABC):
    @abstractmethod
    def area(self): ...

    @abstractmethod
    def perimeter(self): ...

    def describe(self):
        return f"{type(self).__name__}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"


def _positive(name, value):
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


class Circle(Shape):
    def __init__(self, radius):
        self.radius = _positive("radius", radius)

    def area(self):
        return math.pi * self.radius**2

    def perimeter(self):
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = _positive("width", width)
        self.height = _positive("height", height)

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)


class Playlist:
    def __init__(self, name, songs=None):
        self.name = name
        self._songs = []
        for song in songs or []:
            self.add(song)

    def add(self, song):
        if song not in self._songs:
            self._songs.append(song)

    def __len__(self):
        return len(self._songs)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return Playlist(self.name, self._songs[index])
        return self._songs[index]

    def __contains__(self, song):
        return song in self._songs

    def __iter__(self):
        return iter(self._songs)

    def __add__(self, other):
        if not isinstance(other, Playlist):
            return NotImplemented
        return Playlist(f"{self.name} + {other.name}", [*self, *other])

    def __repr__(self):
        n = len(self)
        return f"Playlist({self.name!r}, {n} song{'' if n == 1 else 's'})"
