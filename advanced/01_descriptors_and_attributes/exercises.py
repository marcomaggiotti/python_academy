"""Advanced 01: Descriptors & Attribute Access.

Run: python academy.py check a1
"""

from __future__ import annotations

from typing import Any, Callable


# --- Challenge 1: validating descriptors ------------------------------------------

class Validator:
    """Base data descriptor.

    - Uses __set_name__ to learn its attribute name (store it as self.name).
    - Stores values in the instance's __dict__ under the SAME name (a data
      descriptor still wins over __dict__, so this is safe and needs no "_name").
    - Accessing on the class returns the descriptor itself.
    - Reading an unset attribute raises AttributeError.
    - __set__ calls self.validate(value), which subclasses override to raise
      ValueError / TypeError. validate() may also return a converted value: if it
      returns something other than None, store that instead.
    """

    def validate(self, value: Any) -> Any:
        return None


class Typed(Validator):
    """Typed(int) rejects non-int values with TypeError (bool is NOT an int here).
    Typed(float) accepts ints too and stores them converted to float."""

    def __init__(self, kind: type) -> None:
        raise NotImplementedError


class Bounded(Validator):
    """Bounded(min=None, max=None): numbers outside [min, max] -> ValueError."""

    def __init__(self, min: float | None = None, max: float | None = None) -> None:
        raise NotImplementedError


class OneOf(Validator):
    """OneOf("a", "b"): anything else -> ValueError."""

    def __init__(self, *options: Any) -> None:
        raise NotImplementedError


# --- Challenge 2: your own cached_property ---------------------------------------------

class lazy_property:
    """A NON-data descriptor that computes the value on first access, stores it in
    the instance __dict__, and is never called again for that instance.
    `del obj.attr` resets it (that already works for free once you get it right).
    Accessed on the class -> returns the descriptor. Keep the wrapped function's __doc__.
    """

    def __init__(self, func: Callable[[Any], Any]) -> None:
        raise NotImplementedError


# --- Challenge 3: AttrDict ----------------------------------------------------------------

class AttrDict(dict):
    """A dict that also supports attribute access:

        d = AttrDict({"db": {"host": "x"}})
        d.db.host == "x"        # nested dicts are wrapped on ACCESS (as AttrDict)
        d.port = 5432           # sets d["port"]
        del d.port              # deletes d["port"]
        d.missing               # AttributeError (not KeyError!)
        hasattr(d, "missing")   # False
        d.keys()                # real dict methods still work

    Hint: __getattr__ is only called when normal lookup fails.
    """


# --- Challenge 4: an access-recording proxy ------------------------------------------------

class RecordingProxy:
    """Wrap any object and forward attribute reads, writes and deletes to it,
    recording every READ attribute name in `proxy._accessed` (a list, in order).

        p = RecordingProxy([3, 1, 2])
        p.sort(); p.append(5)
        p._accessed == ["sort", "append"]
        p.new_attr = 1         # forwarded to the wrapped object

    Accessing `_target` and `_accessed` themselves must NOT be recorded.
    """

    def __init__(self, target: Any) -> None:
        raise NotImplementedError


# --- Challenge 5: freezing instances --------------------------------------------------------

def frozen(cls: type) -> type:
    """Class decorator: instances may set attributes freely during __init__
    (including in subclasses' __init__ that call super().__init__), but afterwards
    any setattr/delattr raises AttributeError("<ClassName> is frozen").
    Return the same class (modified), not a new one.
    """
    raise NotImplementedError
