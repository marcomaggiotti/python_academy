# Module 02 — Functions, Closures & Decorators

Functions in Python are **objects**: you can store them, pass them, return them,
and attach attributes to them. Everything in this module follows from that.

## 1. Argument kinds

```python
def f(pos_only, /, normal, *args, kw_only, **kwargs): ...
```

- Before `/` → positional-only. After `*` (or `*args`) → keyword-only.
- **Never** use a mutable default (`def f(x=[])`) — the list is created once,
  at definition time, and shared across calls. Use `None` and create inside.

## 2. Closures and `nonlocal`

An inner function "closes over" variables from the enclosing scope:

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count      # needed because we *assign* to count
        count += 1
        return count
    return increment
```

Gotcha — late binding: `[lambda: i for i in range(3)]` all return `2`.
Fix with a default argument: `lambda i=i: i`.

## 3. Decorators

A decorator is just a callable that takes a function and returns a replacement:

```python
import functools

def log_calls(func):
    @functools.wraps(func)                 # keep __name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_calls          # same as: greet = log_calls(greet)
def greet(name): ...
```

### Decorators with arguments = three levels

```python
def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return [func(*args, **kwargs) for _ in range(times)]
        return wrapper
    return decorator

@repeat(3)
def roll(): ...
```

### State on the wrapper

Since functions are objects, `wrapper.calls = 0` is a neat way to expose state.

## 4. `functools` essentials

- `functools.wraps` — always use it in decorators.
- `functools.lru_cache` / `functools.cache` — memoization.
- `functools.partial(func, *args, **kw)` — pre-fill arguments.
- `functools.reduce` — fold a sequence into a single value.

## 5. Higher-order functions

Functions that take/return functions: `compose(f, g)(x) == f(g(x))`, pipelines,
callbacks, strategy dictionaries (`ops = {"+": operator.add, ...}`).

---

Run: `python academy.py check 02`
