"""Module 02 — Functions, Closures & Decorators.

Run: python academy.py check 02
"""

from __future__ import annotations

import functools
import time
from typing import Any, Callable


# --- Closures ---------------------------------------------------------------

def make_counter(start: int = 0, step: int = 1) -> Callable[[], int]:
    """Return a function that returns start+step, start+2*step, ... on each call.

    >>> c = make_counter(10, 5)
    >>> c(), c()
    (15, 20)
    """
    raise NotImplementedError


def make_averager() -> Callable[[float], float]:
    """Return a function that accepts a number and returns the running average
    of every number it has received so far.

    >>> avg = make_averager()
    >>> avg(10), avg(20), avg(0)
    (10.0, 15.0, 10.0)
    """
    raise NotImplementedError


def make_multipliers(n: int) -> list[Callable[[int], int]]:
    """Return n functions where the i-th multiplies its argument by i.
    Beware of late binding!

    >>> [f(10) for f in make_multipliers(3)]
    [0, 10, 20]
    """
    raise NotImplementedError


def compose(*funcs: Callable) -> Callable:
    """Compose functions right-to-left: compose(f, g, h)(x) == f(g(h(x))).
    compose() with no functions is the identity function.
    """
    raise NotImplementedError


# --- Decorators -------------------------------------------------------------

def count_calls(func: Callable) -> Callable:
    """Decorator that counts how many times the function has been called.
    The count is available as the attribute `calls` on the decorated function.
    Must preserve the original __name__ and __doc__.
    """
    raise NotImplementedError


def retry(times: int, exceptions: tuple[type[BaseException], ...] = (Exception,)):
    """Decorator factory. Call the function up to `times` times total, retrying
    only when one of `exceptions` is raised. If the last attempt still fails,
    re-raise that exception. Other exceptions propagate immediately.

    @retry(3, exceptions=(ConnectionError,))
    def fetch(): ...
    """
    raise NotImplementedError


def memoize(func: Callable) -> Callable:
    """Cache results keyed by positional AND keyword args (don't use functools.cache
    — write it yourself). Expose the cache dict as `func.cache` and a function
    `func.cache_clear()` that empties it. Assume all arguments are hashable.
    """
    raise NotImplementedError


def timed(clock: Callable[[], float] = time.perf_counter):
    """Decorator factory. After every call, store the elapsed time (in seconds,
    measured with `clock`) on the wrapper as `last_duration`. Return the
    function's result unchanged. Duration must be recorded even if it raises.
    """
    raise NotImplementedError


def validate_types(func: Callable) -> Callable:
    """Decorator that checks arguments against the function's annotations at call
    time and raises TypeError on mismatch. Only check parameters whose annotation
    is an actual class (e.g. int, str) — skip others. Ignore the return annotation.

    Hints: inspect.signature(func).bind(*args, **kwargs), typing.get_type_hints.

    @validate_types
    def greet(name: str, times: int = 1) -> str: ...
    greet("bob", times="2")  # TypeError
    """
    raise NotImplementedError


# --- Higher-order functions --------------------------------------------------

def calculator(expression: str) -> float:
    """Evaluate "a <op> b" where op is one of + - * / ** using a dispatch dict
    of functions (look at the `operator` module). No eval()!
    Raise ValueError for unknown operators or malformed input.

    >>> calculator("3 * 4")
    12.0
    """
    raise NotImplementedError


def pipeline(data: list[Any], *steps: Callable[[list[Any]], list[Any]]) -> list[Any]:
    """Apply each step (a function list -> list) to the data in order.

    >>> pipeline([3, 1, 2], sorted, lambda xs: [x * 10 for x in xs])
    [10, 20, 30]
    """
    raise NotImplementedError
