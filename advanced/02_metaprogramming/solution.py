"""Answers for Advanced 02, with explanations."""

from __future__ import annotations

import inspect


# --- Challenge 1 -------------------------------------------------------------
# __init_subclass__ receives class keyword arguments (format=..., abstract=...).
# It runs after the subclass object exists, so we can inspect it and raise
# TypeError to reject the definition.

class Exporter:
    registry = {}

    def __init_subclass__(cls, /, format=None, abstract=False, **kwargs):
        super().__init_subclass__(**kwargs)
        if abstract:
            return
        if not callable(getattr(cls, "export", None)):
            raise TypeError(f"{cls.__name__} must define export(self, data)")
        key = format or cls.__name__.lower()
        if key in Exporter.registry:
            raise TypeError(f"format {key!r} already registered by {Exporter.registry[key].__name__}")
        Exporter.registry[key] = cls

    @classmethod
    def create(cls, key, *args, **kwargs):
        try:
            return Exporter.registry[key](*args, **kwargs)
        except KeyError:
            raise ValueError(f"unknown format {key!r}; known: {Exporter.formats()}") from None

    @classmethod
    def formats(cls):
        return sorted(Exporter.registry)


# --- Challenge 2 -------------------------------------------------------------
# Instance creation is `type(cls).__call__(cls, ...)`, which calls __new__ then
# __init__. Overriding __call__ on the metaclass lets us skip both after the
# first time. The dict is keyed by class, so subclasses get their own instance.

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in SingletonMeta._instances:
            SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]

    def _reset(cls):
        # Methods defined on the metaclass become methods of the *class*.
        SingletonMeta._instances.pop(cls, None)


# --- Challenge 3 -------------------------------------------------------------
# inspect.Signature lets us reuse Python's own argument binding rules (and its
# error messages), so we don't hand-roll the positional/keyword logic.

def make_record(name, fields, *, defaults=None):
    defaults = defaults or {}
    params = []
    for f in fields:
        default = defaults.get(f, inspect.Parameter.empty)
        params.append(inspect.Parameter(f, inspect.Parameter.POSITIONAL_OR_KEYWORD, default=default))
    signature = inspect.Signature(params)  # raises if a default precedes a non-default

    def __init__(self, *args, **kwargs):
        bound = signature.bind(*args, **kwargs)  # TypeError on bad args
        bound.apply_defaults()
        for key, value in bound.arguments.items():
            setattr(self, key, value)

    def __repr__(self):
        inner = ", ".join(f"{f}={getattr(self, f)!r}" for f in fields)
        return f"{name}({inner})"

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return all(getattr(self, f) == getattr(other, f) for f in fields)

    namespace = {
        "__slots__": tuple(fields),
        "_fields": tuple(fields),
        "__init__": __init__,
        "__repr__": __repr__,
        "__eq__": __eq__,
        "__hash__": None,
        "__signature__": signature,
    }
    return type(name, (object,), namespace)


# --- Challenge 4 -------------------------------------------------------------
# The decorator only TAGS the function; collection happens in __init_subclass__,
# which walks the MRO from the most basic class to the most derived so parent
# handlers come first. We store names, not functions, so getattr(self, name)
# picks up overrides via normal method resolution.

def on(event):
    def mark(func):
        func.__dict__.setdefault("_events", []).append(event)
        return func

    return mark


class Component:
    handlers = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        handlers = {}
        for klass in reversed(cls.__mro__):
            for attr_name, value in vars(klass).items():
                for event in getattr(value, "_events", ()):
                    names = handlers.setdefault(event, [])
                    if attr_name not in names:
                        names.append(attr_name)
        cls.handlers = handlers

    def dispatch(self, event, *args, **kwargs):
        return [getattr(self, name)(*args, **kwargs) for name in self.handlers.get(event, [])]


# --- Challenge 5 -------------------------------------------------------------
# Read the parameter names once, at decoration time. Check cls.__dict__ (not
# hasattr) to see whether the class itself defines the method, since every class
# inherits __repr__/__eq__ from object.

def autorepr(cls):
    names = [p for p in inspect.signature(cls.__init__).parameters if p != "self"]

    def __repr__(self):
        inner = ", ".join(f"{n}={getattr(self, n)!r}" for n in names)
        return f"{type(self).__name__}({inner})"

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return all(getattr(self, n) == getattr(other, n) for n in names)

    if "__repr__" not in cls.__dict__:
        cls.__repr__ = __repr__
    if "__eq__" not in cls.__dict__:
        cls.__eq__ = __eq__
        cls.__hash__ = None  # mirror Python: defining __eq__ disables hashing
    return cls
