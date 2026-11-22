# Advanced 02 — Metaprogramming

Code that writes or modifies code: classes created at runtime, hooks that run
when a class is *defined*, and decorators applied to whole classes.

## 1. Classes are objects; `type` makes them

```python
Point = type("Point", (object,), {"x": 0, "norm": lambda self: abs(self.x)})
# equivalent to
class Point:
    x = 0
    def norm(self): return abs(self.x)
```

`type(name, bases, namespace)` is the default **metaclass**: the class of a class.

## 2. `__init_subclass__`: the 90% solution

A hook on the *parent* that runs every time a subclass is defined. You usually
don't need a metaclass.

```python
class Plugin:
    registry = {}

    def __init_subclass__(cls, /, key=None, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.registry[key or cls.__name__.lower()] = cls

class CSVExporter(Plugin, key="csv"): ...
```

## 3. Metaclasses: when you need control over class creation itself

```python
class Meta(type):
    def __new__(mcls, name, bases, ns, **kwargs):
        # inspect/modify ns BEFORE the class exists
        return super().__new__(mcls, name, bases, ns)

    def __call__(cls, *args, **kwargs):
        # runs on Instance(...); controls instance creation (singletons, caching)
        return super().__call__(*args, **kwargs)
```

`__prepare__` can even pick the namespace mapping used while the class body runs.

## 4. Class decorators

Simpler than metaclasses, and they apply to one class (not inherited):

```python
def add_repr(cls):
    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{cls.__name__}({fields})"
    cls.__repr__ = __repr__
    return cls
```

## 5. Introspection toolkit

`inspect.signature`, `inspect.getmembers`, `vars()`, `getattr/setattr`,
`cls.__mro__`, `cls.__dict__`, `func.__qualname__`, `typing.get_type_hints`.

## 6. Method markers

A common pattern: a decorator tags functions (`func._event = "click"`), and
`__init_subclass__` scans the class namespace to collect the tagged ones.

---

Run: `python academy.py check a2`. The answers, with explanations, are in `solution.py`.
