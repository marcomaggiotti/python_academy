"""Module 04 — Iterators & Generators.

Most of these should be *generator functions* (use `yield`). The tests check
laziness, so don't build full lists internally unless the docstring allows it.
Run: python academy.py check 04
"""

from __future__ import annotations

from typing import Any, Callable, Generator, Hashable, Iterable, Iterator


class Countdown:
    """A class-based ITERABLE (not iterator): Countdown(3) yields 3, 2, 1.
    It must be re-iterable: list(c) twice gives the same result both times.
    Implement __iter__ returning a separate iterator object (write a
    CountdownIterator class with __next__) — no `yield` allowed here.
    """

    def __init__(self, start: int) -> None:
        raise NotImplementedError


def fibonacci() -> Iterator[int]:
    """Infinite generator: 0, 1, 1, 2, 3, 5, 8, ..."""
    raise NotImplementedError


def take(n: int, iterable: Iterable) -> list:
    """Return the first n items as a list (works on infinite iterators)."""
    raise NotImplementedError


def chunked(iterable: Iterable, size: int) -> Iterator[list]:
    """Yield successive lists of `size` items; the last may be shorter.
    Must work on any iterable, including generators (no len() / slicing!).

    >>> list(chunked(range(7), 3))
    [[0, 1, 2], [3, 4, 5], [6]]
    """
    raise NotImplementedError


def sliding_window(iterable: Iterable, size: int) -> Iterator[tuple]:
    """Yield overlapping tuples of `size` consecutive items.
    Hint: collections.deque(maxlen=size).

    >>> list(sliding_window([1, 2, 3, 4], 2))
    [(1, 2), (2, 3), (3, 4)]
    """
    raise NotImplementedError


def flatten_deep(nested: Iterable) -> Iterator:
    """Recursively flatten arbitrarily nested lists/tuples using `yield from`.
    Strings and bytes must NOT be split into characters.

    >>> list(flatten_deep([1, [2, (3, [4])], "ab"]))
    [1, 2, 3, 4, 'ab']
    """
    raise NotImplementedError


def unique(iterable: Iterable, key: Callable[[Any], Hashable] | None = None) -> Iterator:
    """Yield items in order, skipping any whose key (default: the item itself)
    has been seen before.

    >>> list(unique("AbBa", key=str.lower))
    ['A', 'b']
    """
    raise NotImplementedError


def interleave(*iterables: Iterable) -> Iterator:
    """Round-robin across iterables until all are exhausted.

    >>> list(interleave("ABC", "d", "ef"))
    ['A', 'd', 'e', 'B', 'f', 'C']
    """
    raise NotImplementedError


# --- A lazy pipeline ---------------------------------------------------------
# Lines look like: "2026-01-05 ERROR payment timeout after 30s"

def parse_log(lines: Iterable[str]) -> Iterator[dict]:
    """Yield dicts {"date": ..., "level": ..., "message": ...} for each line.
    Skip blank lines and lines with fewer than 3 space-separated parts.
    `message` is the rest of the line after the level (whitespace-stripped).
    """
    raise NotImplementedError


def only_level(records: Iterable[dict], level: str) -> Iterator[dict]:
    """Yield the records with the given level (case-insensitive)."""
    raise NotImplementedError


# --- Coroutine-style generator ------------------------------------------------

def running_stats() -> Generator[dict, float, None]:
    """A generator you `send()` numbers into. After priming with next(), each
    send(x) returns {"count": n, "mean": m, "min": lo, "max": hi} over all
    values so far. The priming next() returns {"count": 0} .

    >>> s = running_stats(); next(s)
    {'count': 0}
    >>> s.send(4)
    {'count': 1, 'mean': 4.0, 'min': 4, 'max': 4}
    """
    raise NotImplementedError
