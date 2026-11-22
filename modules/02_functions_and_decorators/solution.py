"""Reference solutions for Module 02."""

from __future__ import annotations

import functools
import inspect
import operator
import time
import typing


def make_counter(start=0, step=1):
    value = start

    def counter():
        nonlocal value
        value += step
        return value

    return counter


def make_averager():
    total = 0.0
    count = 0

    def averager(x):
        nonlocal total, count
        total += x
        count += 1
        return total / count

    return averager


def make_multipliers(n):
    return [lambda x, i=i: x * i for i in range(n)]


def compose(*funcs):
    def composed(x):
        for f in reversed(funcs):
            x = f(x)
        return x

    return composed


def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)

    wrapper.calls = 0
    return wrapper


def retry(times, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise

        return wrapper

    return decorator


def memoize(func):
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache
    wrapper.cache_clear = cache.clear
    return wrapper


def timed(clock=time.perf_counter):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = clock()
            try:
                return func(*args, **kwargs)
            finally:
                wrapper.last_duration = clock() - start

        wrapper.last_duration = None
        return wrapper

    return decorator


def validate_types(func):
    sig = inspect.signature(func)
    hints = typing.get_type_hints(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        for name, value in bound.arguments.items():
            expected = hints.get(name)
            if isinstance(expected, type) and not isinstance(value, expected):
                raise TypeError(
                    f"{name} must be {expected.__name__}, got {type(value).__name__}"
                )
        return func(*args, **kwargs)

    return wrapper


OPS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "**": operator.pow,
}


def calculator(expression):
    parts = expression.split()
    if len(parts) != 3:
        raise ValueError(f"malformed expression: {expression!r}")
    left, op, right = parts
    if op not in OPS:
        raise ValueError(f"unknown operator: {op!r}")
    return float(OPS[op](float(left), float(right)))


def pipeline(data, *steps):
    return functools.reduce(lambda acc, step: step(acc), steps, data)
