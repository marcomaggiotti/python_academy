# Advanced 01 — Descriptors & Attribute Access

`property`, `classmethod`, `staticmethod`, bound methods and `functools.cached_property`
are all built on one mechanism: the **descriptor protocol**.

## 1. The protocol

An object is a descriptor if its *class* defines any of:

```python
__get__(self, instance, owner)     # instance is None when accessed on the class
__set__(self, instance, value)
__delete__(self, instance)
__set_name__(self, owner, name)    # called once at class creation (3.6+)
```

- **Data descriptor**: defines `__set__` or `__delete__`. Wins over the instance `__dict__`.
- **Non-data descriptor**: only `__get__`. The instance `__dict__` wins, which is
  how `cached_property` works: compute once, store in `__dict__`, and the
  descriptor is never consulted again.

## 2. Attribute lookup order for `obj.attr`

1. `type(obj).__mro__` is searched for `attr`. If it's a **data descriptor**, call its `__get__`.
2. Otherwise, if `attr` is in `obj.__dict__`, return it.
3. Otherwise, if the class attribute is a non-data descriptor, call `__get__`; else return it.
4. Otherwise call `type(obj).__getattr__(obj, "attr")` if defined, else `AttributeError`.

All of this lives in `object.__getattribute__`. Override `__getattr__` (a fallback
for *missing* attributes) far more often than `__getattribute__` (which runs on *every*
access and is easy to recurse into infinitely).

## 3. A reusable validator

```python
class Positive:
    def __set_name__(self, owner, name):
        self.private = "_" + name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                    # accessed on the class
        return getattr(obj, self.private)

    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self.private[1:]} must be > 0")
        setattr(obj, self.private, value)

class Order:
    qty = Positive()
    price = Positive()
```

## 4. `__setattr__` / `__delattr__` overrides

When you override `__setattr__`, use `object.__setattr__(self, name, value)` (or
`super().__setattr__`) inside it to actually store values. Otherwise you recurse
forever.

## 5. `__slots__`

`__slots__ = ("x", "y")` removes the per-instance `__dict__`, which saves memory
and blocks accidental new attributes. Each slot is itself a descriptor on the class.

---

Run: `python academy.py check a1`. The answers, with explanations, are in `solution.py`.
