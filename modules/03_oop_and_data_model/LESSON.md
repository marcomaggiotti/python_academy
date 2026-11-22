# Module 03 — OOP & the Python Data Model

Python's "data model" is the set of **dunder (double-underscore) methods** that
let your objects plug into built-in syntax: `+`, `==`, `len()`, `for`, `in`, `[]`...

## 1. The essential dunders

| You write           | Python calls                |
|---------------------|-----------------------------|
| `repr(x)` / REPL    | `x.__repr__()`              |
| `str(x)` / `print`  | `x.__str__()` (falls back to `__repr__`) |
| `a == b`            | `a.__eq__(b)`               |
| `hash(a)`, dict key | `a.__hash__()`              |
| `a + b`             | `a.__add__(b)`, then `b.__radd__(a)` |
| `3 * v`             | `v.__rmul__(3)` (after `int.__mul__` returns `NotImplemented`) |
| `abs(v)`, `bool(v)` | `__abs__`, `__bool__`       |
| `len(c)`, `c[i]`    | `__len__`, `__getitem__`    |
| `x in c`, `for x in c` | `__contains__`, `__iter__` |

Return the singleton **`NotImplemented`** (not raise!) from binary operators
when you don't support the other operand — Python then tries the reflected method.

If you define `__eq__`, Python sets `__hash__ = None` (unhashable) unless you
define `__hash__` too. Only hash immutable objects.

## 2. Properties, classmethods, staticmethods

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius            # goes through the setter!

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @classmethod
    def from_fahrenheit(cls, f):          # alternative constructor
        return cls((f - 32) * 5 / 9)
```

## 3. Dataclasses

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, order=True)
class Money:
    amount: int
    currency: str = "EUR"
    tags: list[str] = field(default_factory=list, compare=False)

    def __post_init__(self):              # validation hook
        ...
```

`frozen=True` → immutable and hashable. `order=True` → `<`, `>` compare fields as tuples.
In a frozen dataclass, set attributes in `__post_init__` via
`object.__setattr__(self, "name", value)`.

## 4. Inheritance & abstract base classes

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    def describe(self):                   # template method using the abstract one
        return f"{type(self).__name__} with area {self.area():.2f}"
```

Instantiating `Shape()` raises `TypeError`. Use `super().__init__(...)` to call
the parent. Prefer composition over deep hierarchies.

## 5. `functools.total_ordering`

Define `__eq__` and one of `__lt__`/`__le__`/`__gt__`/`__ge__`, and the
decorator fills in the rest.

## 6. Making a sequence

Implement `__len__` and `__getitem__` and you get iteration, `in`, `reversed`
for free. Handle `slice` objects in `__getitem__` to support `obj[1:3]`.

---

Run: `python academy.py check 03`
