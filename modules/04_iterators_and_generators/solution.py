"""Reference solutions for Module 04."""

from __future__ import annotations

from collections import deque
from itertools import cycle, islice


class CountdownIterator:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


class Countdown:
    def __init__(self, start):
        self.start = start

    def __iter__(self):
        return CountdownIterator(self.start)


def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def take(n, iterable):
    return list(islice(iterable, n))


def chunked(iterable, size):
    it = iter(iterable)
    while chunk := list(islice(it, size)):
        yield chunk


def sliding_window(iterable, size):
    window = deque(maxlen=size)
    for item in iterable:
        window.append(item)
        if len(window) == size:
            yield tuple(window)


def flatten_deep(nested):
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten_deep(item)
        else:
            yield item


def unique(iterable, key=None):
    seen = set()
    for item in iterable:
        k = item if key is None else key(item)
        if k not in seen:
            seen.add(k)
            yield item


def interleave(*iterables):
    iterators = deque(iter(it) for it in iterables)
    while iterators:
        it = iterators.popleft()
        try:
            yield next(it)
        except StopIteration:
            continue
        iterators.append(it)


def parse_log(lines):
    for line in lines:
        parts = line.split(maxsplit=2)
        if len(parts) < 3:
            continue
        date, level, message = parts
        yield {"date": date, "level": level, "message": message.strip()}


def only_level(records, level):
    wanted = level.upper()
    return (r for r in records if r["level"].upper() == wanted)


def running_stats():
    count, total = 0, 0.0
    lo = hi = None
    stats = {"count": 0}
    while True:
        x = yield stats
        count += 1
        total += x
        lo = x if lo is None else min(lo, x)
        hi = x if hi is None else max(hi, x)
        stats = {"count": count, "mean": total / count, "min": lo, "max": hi}
