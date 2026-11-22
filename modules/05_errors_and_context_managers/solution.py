"""Reference solutions for Module 05."""

from __future__ import annotations

import copy
import time
from contextlib import contextmanager


class InventoryError(Exception):
    pass


class UnknownItem(InventoryError):
    def __init__(self, item):
        super().__init__(f"unknown item: {item!r}")
        self.item = item


class OutOfStock(InventoryError):
    def __init__(self, item, requested, available):
        super().__init__(f"cannot take {requested} {item!r} (only {available} left)")
        self.item = item
        self.requested = requested
        self.available = available


class Inventory:
    def __init__(self, stock):
        self._stock = dict(stock)

    @property
    def stock(self):
        return dict(self._stock)

    def take(self, item, amount=1):
        if amount <= 0:
            raise ValueError("amount must be positive")
        if item not in self._stock:
            raise UnknownItem(item)
        available = self._stock[item]
        if amount > available:
            raise OutOfStock(item, amount, available)
        self._stock[item] = available - amount
        return self._stock[item]


class ConfigError(Exception):
    pass


def parse_config(text):
    result = {}
    for n, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            raise ConfigError(f"line {n}: missing '='")
        try:
            result[key.strip()] = int(value.strip())
        except ValueError as exc:
            raise ConfigError(f"line {n}: invalid integer {value.strip()!r}") from exc
    return result


def validate_users(users):
    errors = []
    for i, user in enumerate(users):
        if not user.get("name"):
            errors.append(ValueError(f"user {i}: name required"))
        age = user.get("age")
        if not isinstance(age, int) or isinstance(age, bool):
            errors.append(TypeError(f"user {i}: age must be int"))
        elif age < 0:
            errors.append(ValueError(f"user {i}: age must be >= 0"))
    if errors:
        raise ExceptionGroup("invalid users", errors)


class Timer:
    def __init__(self, clock=time.perf_counter):
        self._clock = clock
        self.elapsed = None

    def __enter__(self):
        self._start = self._clock()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = self._clock() - self._start
        return False


_MISSING = object()


@contextmanager
def temporary_attr(obj, name, value):
    old = getattr(obj, name, _MISSING)
    setattr(obj, name, value)
    try:
        yield obj
    finally:
        if old is _MISSING:
            delattr(obj, name)
        else:
            setattr(obj, name, old)


@contextmanager
def collect_errors(log, *types):
    types = types or (Exception,)
    try:
        yield
    except types as exc:
        log.append(exc)


class Transaction:
    def __init__(self, data):
        self._data = data

    def __enter__(self):
        self._work = copy.deepcopy(self._data)
        return self._work

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self._data.clear()
            self._data.update(self._work)
        return False
