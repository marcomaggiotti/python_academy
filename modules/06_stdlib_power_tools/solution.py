"""Reference solutions for Module 06."""

from __future__ import annotations

import bisect
import heapq
import itertools
import re
from collections import ChainMap, Counter, defaultdict, deque
from functools import lru_cache, singledispatch
from itertools import accumulate, groupby, pairwise


def top_words(text, n):
    counts = Counter(re.findall(r"[a-z']+", text.lower()))
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        groups["".join(sorted(w))].append(w)
    return sorted(sorted(g) for g in groups.values())


_BREAKPOINTS = [60, 70, 80, 90]
_GRADES = "FDCBA"


def letter_grade(score):
    return _GRADES[bisect.bisect_right(_BREAKPOINTS, score)]


def run_length_encode(s):
    return "".join(f"{ch}{len(list(group))}" for ch, group in groupby(s))


def run_length_decode(s):
    return "".join(ch * int(n) for ch, n in re.findall(r"(\D)(\d+)", s))


def running_max(values):
    return list(accumulate(values, max))


def increasing_steps(values):
    return sum(b > a for a, b in pairwise(values))


def k_closest(points, k):
    return heapq.nsmallest(k, points, key=lambda p: p[0] ** 2 + p[1] ** 2)


class PriorityQueue:
    def __init__(self):
        self._heap = []
        self._counter = itertools.count()

    def push(self, item, priority):
        heapq.heappush(self._heap, (priority, next(self._counter), item))

    def pop(self):
        if not self._heap:
            raise IndexError("pop from empty PriorityQueue")
        return heapq.heappop(self._heap)[-1]

    def peek(self):
        if not self._heap:
            raise IndexError("peek at empty PriorityQueue")
        return self._heap[0][-1]

    def __len__(self):
        return len(self._heap)


class RecentItems:
    def __init__(self, capacity):
        self._items = deque(maxlen=capacity)

    def add(self, item):
        if item in self._items:
            self._items.remove(item)
        self._items.appendleft(item)

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


def layered_settings(cli, env, defaults):
    return ChainMap({}, cli, env, defaults)


def count_paths(rows, cols):
    @lru_cache(maxsize=None)
    def paths(r, c):
        if r == 1 or c == 1:
            return 1
        return paths(r - 1, c) + paths(r, c - 1)

    return paths(rows, cols)


@singledispatch
def describe(value):
    return f"object of type {type(value).__name__}"


@describe.register
def _(value: int):
    return f"int: {value}"


@describe.register
def _(value: bool):
    return f"bool: {value}"


@describe.register
def _(value: float):
    return f"float: {value:.2f}"


@describe.register
def _(value: str):
    return f"str of length {len(value)}"


@describe.register
def _(value: list):
    inner = ", ".join(describe(v) for v in value)
    return f"list of {len(value)} items: [{inner}]"
