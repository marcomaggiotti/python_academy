"""Advanced 02: Metaprogramming.

Run: python academy.py check a2
"""

from __future__ import annotations

import inspect
from typing import Any, Callable


# --- Challenge 1: a plugin registry with __init_subclass__ -------------------------

class Exporter:
    """Every subclass registers itself automatically.

        class JSONExporter(Exporter, format="json"): ...
        class Xml(Exporter): ...                       # key defaults to "xml" (lower-cased name)

        Exporter.registry == {"json": JSONExporter, "xml": Xml}
        Exporter.create("json")  -> JSONExporter()     # KeyError-like: ValueError for unknown
        Exporter.formats()       -> ["json", "xml"]    # sorted

    - Registering a duplicate key raises TypeError at class-definition time.
    - Subclasses with `abstract=True` are NOT registered:
          class BaseBinary(Exporter, abstract=True): ...
    - Every concrete subclass must define an `export(self, data) -> str` method;
      if it doesn't (and it isn't abstract), raise TypeError at definition time.
    """

    registry: dict[str, type[Exporter]] = {}


# --- Challenge 2: singleton metaclass ---------------------------------------------------

class SingletonMeta(type):
    """Classes using this metaclass have at most one instance PER CLASS.
    Calling the class again returns the same instance (and does NOT re-run __init__).
    Subclasses get their own separate instance.
    Also add a classmethod-like helper on the metaclass: `Cls._reset()` forgets the
    instance (handy in tests).
    """


# --- Challenge 3: build a class at runtime ------------------------------------------------

def make_record(name: str, fields: list[str], *, defaults: dict[str, Any] | None = None) -> type:
    """Create a class with `type()` (no `class` statement, no dataclasses!):

        Point = make_record("Point", ["x", "y"], defaults={"y": 0})
        p = Point(1)        # positional or keyword args; missing ones use defaults
        p.x, p.y            # 1, 0
        repr(p)             # "Point(x=1, y=0)"
        Point(1, 0) == p    # True (same class & same values)
        Point._fields       # ("x", "y")
        Point(1, 2, 3)      # TypeError (too many args)
        Point()             # TypeError (missing x)
        Point(1, z=2)       # TypeError (unknown field)
    Instances must use __slots__ (no __dict__).
    """
    raise NotImplementedError


# --- Challenge 4: event handler collection via method markers ----------------------------------

def on(event: str) -> Callable:
    """Method decorator: marks a method as a handler for `event`. A method may be
    decorated several times to handle several events. Must return the original
    function (it stays a normal, callable method)."""
    raise NotImplementedError


class Component:
    """Subclasses get a class-level mapping of event -> list of method NAMES,
    collected when the subclass is defined, including handlers inherited from
    parents (parent handlers first). If a subclass overrides a handler method by
    name, the name stays registered once (it'll dispatch to the override).

        class Button(Component):
            @on("click")
            def press(self, x): return f"pressed {x}"

        Button().dispatch("click", 1) -> ["pressed 1"]   # list of all handler results
        Button().dispatch("unknown")  -> []
        Button.handlers               -> {"click": ["press"]}
    """

    handlers: dict[str, list[str]] = {}

    def dispatch(self, event: str, *args: Any, **kwargs: Any) -> list[Any]:
        raise NotImplementedError


# --- Challenge 5: auto __repr__ / __eq__ from __init__'s signature ---------------------------

def autorepr(cls: type) -> type:
    """Class decorator: look at cls.__init__'s parameters (excluding self) and add
        __repr__ -> "ClassName(a=1, b='x')"   (in parameter order, values via repr)
        __eq__   -> same type and same values for those attributes
    It assumes __init__ stores each parameter as an attribute with the same name.
    Don't overwrite __repr__/__eq__ if the class body defines them itself.
    """
    raise NotImplementedError
