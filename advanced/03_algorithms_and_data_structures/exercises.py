"""Advanced 03: Algorithms & Data Structures.

Some tests include performance checks, so mind your complexity.
Run: python academy.py check a3
"""

from __future__ import annotations

from typing import Hashable, Iterable, Mapping


# --- Challenge 1: O(1) LRU cache (no OrderedDict, no functools!) ---------------------

class LRUCache:
    """Fixed-capacity cache that evicts the least-recently-used key.

      cache = LRUCache(2)
      cache.put("a", 1); cache.put("b", 2)
      cache.get("a")       -> 1          ("a" is now most recently used)
      cache.put("c", 3)                  evicts "b"
      cache.get("b")       -> None       (or cache.get("b", default))
      "a" in cache, len(cache)
      cache.keys()         -> list from MOST to LEAST recently used
      cache.evictions      -> count of evicted keys

    `put` on an existing key updates the value and marks it as recently used.
    `in` must NOT change recency. Implement with a dict + doubly linked list.
    capacity < 1 -> ValueError.
    """

    def __init__(self, capacity: int) -> None:
        raise NotImplementedError


# --- Challenge 2: Trie ---------------------------------------------------------------------

class Trie:
    """Prefix tree of words.

      t = Trie(["car", "cart", "cat", "dog"])
      t.insert("care")
      "cat" in t       -> True;  "ca" in t -> False (only whole words)
      t.starts_with("car") -> ["car", "care", "cart"]   (sorted)
      t.remove("car")  -> True (False if it wasn't there); "cart" still present
      len(t)           -> number of words
    After remove, branches that no longer lead to any word should be pruned
    (t.node_count() returns the number of nodes excluding the root).
    """

    def __init__(self, words: Iterable[str] = ()) -> None:
        raise NotImplementedError


# --- Challenge 3: intervals ------------------------------------------------------------------

def merge_intervals(intervals: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge overlapping or touching intervals; return them sorted.

    >>> merge_intervals([(5, 7), (1, 3), (2, 4), (7, 8), (10, 11)])
    [(1, 4), (5, 8), (10, 11)]
    """
    raise NotImplementedError


def min_meeting_rooms(meetings: Iterable[tuple[int, int]]) -> int:
    """Minimum number of rooms so that no two overlapping meetings share one.
    A meeting ending at t frees the room for a meeting starting at t."""
    raise NotImplementedError


# --- Challenge 4: graphs ----------------------------------------------------------------------

class CycleError(ValueError):
    """Raised by topological_sort; .cycle_nodes holds the set of nodes involved
    in (or blocked by) a cycle."""


def topological_sort(deps: Mapping[Hashable, Iterable[Hashable]]) -> list:
    """`deps` maps a node to the nodes it DEPENDS ON (which must come first).
    Nodes that appear only as dependencies are still included. Among nodes that
    are ready at the same time, choose in sorted order (so output is deterministic).

    >>> topological_sort({"app": ["lib", "utils"], "lib": ["utils"]})
    ['utils', 'lib', 'app']
    """
    raise NotImplementedError


def shortest_path(
    graph: Mapping[str, Mapping[str, float]], start: str, goal: str
) -> tuple[float, list[str]]:
    """Dijkstra on a directed weighted graph {node: {neighbor: weight}}.
    Return (total_cost, [start, ..., goal]). If the goal is unreachable return
    (math.inf, []). start == goal -> (0, [start]).
    """
    raise NotImplementedError


def word_ladder(begin: str, end: str, words: Iterable[str]) -> int:
    """Length of the shortest transformation sequence begin -> end, changing one
    letter at a time, where every intermediate word (and end) is in `words`.
    Count includes both ends ("hit"->"hot"->"dot"->"dog"->"cog" == 5). 0 if impossible.
    Must handle a few thousand words quickly (BFS + smart neighbor generation).
    """
    raise NotImplementedError


# --- Challenge 5: running median ----------------------------------------------------------------

class RunningMedian:
    """add(x) in O(log n), median() in O(1). median() of an empty stream -> ValueError.
    For an even count, the median is the mean of the two middle values (float)."""

    def __init__(self) -> None:
        raise NotImplementedError
