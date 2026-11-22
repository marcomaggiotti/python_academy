"""Answers for Advanced 01, with explanations."""

from __future__ import annotations

import functools


# --- Challenge 1 -------------------------------------------------------------
# A data descriptor (has __set__) takes priority over instance __dict__, so we
# can store the value in __dict__ under the very same name: reads still go
# through __get__, and __get__ fetches from __dict__ directly.

class Validator:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return obj.__dict__[self.name]
        except KeyError:
            raise AttributeError(
                f"{type(obj).__name__!r} object has no attribute {self.name!r}"
            ) from None

    def __set__(self, obj, value):
        converted = self.validate(value)
        obj.__dict__[self.name] = value if converted is None else converted

    def validate(self, value):
        return None


class Typed(Validator):
    def __init__(self, kind):
        self.kind = kind

    def validate(self, value):
        # bool is a subclass of int, which is almost never what a schema means.
        if isinstance(value, bool) and self.kind is not bool:
            raise TypeError(f"{self.name} must be {self.kind.__name__}, got bool")
        if self.kind is float and isinstance(value, int):
            return float(value)
        if not isinstance(value, self.kind):
            raise TypeError(f"{self.name} must be {self.kind.__name__}, got {type(value).__name__}")
        return None


class Bounded(Validator):
    def __init__(self, min=None, max=None):
        self.min, self.max = min, max

    def validate(self, value):
        if self.min is not None and value < self.min:
            raise ValueError(f"{self.name} must be >= {self.min}")
        if self.max is not None and value > self.max:
            raise ValueError(f"{self.name} must be <= {self.max}")
        return None


class OneOf(Validator):
    def __init__(self, *options):
        self.options = set(options)

    def validate(self, value):
        if value not in self.options:
            raise ValueError(f"{self.name} must be one of {sorted(map(repr, self.options))}")
        return None


# --- Challenge 2 -------------------------------------------------------------
# No __set__, so this is a NON-data descriptor. After the first access we put
# the value in obj.__dict__, and from then on normal lookup finds it there first
# and never calls __get__ again. `del obj.attr` removes it from __dict__, which
# makes the descriptor visible again.

class lazy_property:
    def __init__(self, func):
        self.func = func
        functools.update_wrapper(self, func)

    def __set_name__(self, owner, name):
        self.attrname = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = self.func(obj)
        obj.__dict__[getattr(self, "attrname", self.func.__name__)] = value
        return value


# --- Challenge 3 -------------------------------------------------------------
# __getattr__ runs only after normal lookup fails, so real dict methods (keys,
# items...) still resolve normally. Convert KeyError to AttributeError so that
# hasattr() and getattr(obj, name, default) behave.

class AttrDict(dict):
    def __getattr__(self, name):
        try:
            value = self[name]
        except KeyError:
            raise AttributeError(name) from None
        if isinstance(value, dict) and not isinstance(value, AttrDict):
            value = AttrDict(value)
            self[name] = value       # so nested mutation sticks
        return value

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name) from None


# --- Challenge 4 -------------------------------------------------------------
# __getattribute__ intercepts EVERY read. To reach our own fields without
# recursing, go through object.__getattribute__ explicitly.

class RecordingProxy:
    _OWN = frozenset({"_target", "_accessed"})

    def __init__(self, target):
        object.__setattr__(self, "_target", target)
        object.__setattr__(self, "_accessed", [])

    def __getattribute__(self, name):
        if name in RecordingProxy._OWN or name.startswith("__"):
            return object.__getattribute__(self, name)
        object.__getattribute__(self, "_accessed").append(name)
        return getattr(object.__getattribute__(self, "_target"), name)

    def __setattr__(self, name, value):
        setattr(object.__getattribute__(self, "_target"), name, value)

    def __delattr__(self, name):
        delattr(object.__getattribute__(self, "_target"), name)


# --- Challenge 5 -------------------------------------------------------------
# Wrap __init__ so that a per-instance flag is set only when the OUTERMOST
# __init__ returns. A depth counter handles subclasses calling super().__init__
# (both levels are wrapped if both are decorated, and only the outer one freezes).

def frozen(cls):
    original_init = cls.__init__

    @functools.wraps(original_init)
    def __init__(self, *args, **kwargs):
        depth = self.__dict__.get("_frozen_depth", 0)
        object.__setattr__(self, "_frozen_depth", depth + 1)
        try:
            original_init(self, *args, **kwargs)
        finally:
            object.__setattr__(self, "_frozen_depth", depth)
        if depth == 0:
            object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name, value):
        if self.__dict__.get("_frozen") and not self.__dict__.get("_frozen_depth"):
            raise AttributeError(f"{type(self).__name__} is frozen")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if self.__dict__.get("_frozen") and not self.__dict__.get("_frozen_depth"):
            raise AttributeError(f"{type(self).__name__} is frozen")
        object.__delattr__(self, name)

    cls.__init__ = __init__
    cls.__setattr__ = __setattr__
    cls.__delattr__ = __delattr__
    return cls
