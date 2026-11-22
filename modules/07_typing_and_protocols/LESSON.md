# Module 07 — Type Hints, Generics, Protocols & Enums

Type hints don't change runtime behaviour — they're checked by tools like
**mypy** or **pyright** and make code self-documenting. Modern syntax (3.10+):

```python
def find(users: list[User], name: str) -> User | None: ...
Callback = Callable[[int, str], bool]          # type alias
```

## 1. Generics with `TypeVar`

```python
from typing import TypeVar, Generic, Sequence

T = TypeVar("T")

def first(items: Sequence[T]) -> T | None:     # returns the SAME type it receives
    return items[0] if items else None

class Box(Generic[T]):
    def __init__(self, item: T) -> None:
        self.item = item
```

Python 3.12 adds shorthand: `def first[T](items: Sequence[T]) -> T | None` and
`class Box[T]: ...`. We use `TypeVar` here so the code runs on 3.11.

## 2. Protocols — static duck typing

Instead of forcing inheritance, describe the *shape* an object needs:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class SupportsArea(Protocol):
    def area(self) -> float: ...

class Square:                       # never mentions SupportsArea
    def area(self) -> float: return 4.0

isinstance(Square(), SupportsArea)  # True (runtime_checkable checks method names only)
```

## 3. `TypedDict`, `Literal`, `Final`

```python
from typing import TypedDict, Literal, NotRequired

class Movie(TypedDict):
    title: str
    year: int
    rating: NotRequired[float]

Mode = Literal["r", "w", "a"]
```

## 4. Enums

```python
from enum import Enum, auto

class Color(Enum):
    RED = auto()
    GREEN = auto()

Color["RED"], Color(1), Color.RED.name, Color.RED.value
for c in Color: ...
```

Enums can have methods and properties — great for state machines.

## 5. Running a type checker

```bash
pip install mypy
mypy --strict modules/07_typing_and_protocols/exercises.py
```

Try it after finishing: the tests check behaviour; mypy checks your hints.

---

Run: `python academy.py check 07`
