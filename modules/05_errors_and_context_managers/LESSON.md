# Module 05 — Exceptions & Context Managers

## 1. Designing exceptions

Create a small **hierarchy** so callers can catch broadly or narrowly:

```python
class AppError(Exception):
    """Base for everything this library raises."""

class NotFound(AppError):
    def __init__(self, key):
        super().__init__(f"{key!r} not found")
        self.key = key                     # keep structured data on the exception
```

## 2. `try` / `except` / `else` / `finally`

```python
try:
    value = risky()
except (KeyError, IndexError) as exc:      # catch specific exceptions only
    handle(exc)
else:
    runs_only_if_no_exception(value)
finally:
    always_runs()
```

**Never** use bare `except:` — it swallows `KeyboardInterrupt` and `SystemExit`.

## 3. Exception chaining

Translate low-level errors into domain errors without losing the cause:

```python
try:
    port = int(raw)
except ValueError as exc:
    raise ConfigError(f"bad port {raw!r}") from exc   # sets __cause__
```

`raise ... from None` hides the original when it's just noise.

## 4. Exception groups (3.11+)

When you want to report *several* failures at once:

```python
errors = [ValueError("a"), TypeError("b")]
raise ExceptionGroup("validation failed", errors)

try:
    ...
except* ValueError as group:     # handles just the ValueErrors in the group
    ...
```

## 5. Context managers

`with` guarantees cleanup. A class-based context manager implements:

```python
class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self                         # bound to the `as` target
    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self.start
        return False                        # True would SUPPRESS the exception
```

Or use a generator with `contextlib.contextmanager`:

```python
from contextlib import contextmanager

@contextmanager
def cd(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield                               # the body of the `with` runs here
    finally:
        os.chdir(old)                       # runs even if the body raised
```

Also explore `contextlib.suppress`, `contextlib.ExitStack`, `contextlib.redirect_stdout`.

---

Run: `python academy.py check 05`
