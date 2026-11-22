"""Answers for Advanced 03, with explanations."""

from __future__ import annotations

import heapq
import math
import string
from collections import defaultdict, deque


# --- Challenge 1 -------------------------------------------------------------
# dict: key -> node gives O(1) lookup. A doubly linked list ordered by recency
# gives O(1) move-to-front and O(1) eviction from the back. Sentinel head/tail
# nodes mean we never have to special-case an empty list.

class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=None, value=None):
        self.key, self.value = key, value
        self.prev = self.next = None


class LRUCache:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self.evictions = 0
        self._map = {}
        self._head, self._tail = _Node(), _Node()  # head.next = most recent
        self._head.next, self._tail.prev = self._tail, self._head

    def _unlink(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def _push_front(self, node):
        node.prev, node.next = self._head, self._head.next
        self._head.next.prev = node
        self._head.next = node

    def get(self, key, default=None):
        node = self._map.get(key)
        if node is None:
            return default
        self._unlink(node)
        self._push_front(node)
        return node.value

    def put(self, key, value):
        node = self._map.get(key)
        if node is not None:
            node.value = value
            self._unlink(node)
            self._push_front(node)
            return
        if len(self._map) >= self.capacity:
            lru = self._tail.prev
            self._unlink(lru)
            del self._map[lru.key]
            self.evictions += 1
        node = _Node(key, value)
        self._map[key] = node
        self._push_front(node)

    def __contains__(self, key):
        return key in self._map

    def __len__(self):
        return len(self._map)

    def keys(self):
        out, node = [], self._head.next
        while node is not self._tail:
            out.append(node.key)
            node = node.next
        return out


# --- Challenge 2 -------------------------------------------------------------
# Nested dicts are the lightest trie. A special END key marks the end of a word.
# remove() recurses and returns "this child is now empty", so the parent can
# prune it on the way back up.

_END = object()


class Trie:
    def __init__(self, words=()):
        self._root = {}
        self._size = 0
        for w in words:
            self.insert(w)

    def insert(self, word):
        node = self._root
        for ch in word:
            node = node.setdefault(ch, {})
        if _END not in node:
            node[_END] = True
            self._size += 1

    def _find(self, prefix):
        node = self._root
        for ch in prefix:
            node = node.get(ch)
            if node is None:
                return None
        return node

    def __contains__(self, word):
        node = self._find(word)
        return node is not None and _END in node

    def __len__(self):
        return self._size

    def starts_with(self, prefix):
        node = self._find(prefix)
        if node is None:
            return []
        results = []
        stack = [(node, prefix)]
        while stack:
            current, path = stack.pop()
            for key, child in current.items():
                if key is _END:
                    results.append(path)
                else:
                    stack.append((child, path + key))
        return sorted(results)

    def remove(self, word):
        def _remove(node, i):
            if i == len(word):
                if _END not in node:
                    return False, False
                del node[_END]
                return True, not node
            child = node.get(word[i])
            if child is None:
                return False, False
            removed, prune = _remove(child, i + 1)
            if prune:
                del node[word[i]]
            return removed, removed and not node

        removed, _ = _remove(self._root, 0)
        if removed:
            self._size -= 1
        return removed

    def node_count(self):
        def count(node):
            return sum(1 + count(child) for key, child in node.items() if key is not _END)

        return count(self._root)


# --- Challenge 3 -------------------------------------------------------------

def merge_intervals(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def min_meeting_rooms(meetings):
    # Min-heap of end times of meetings in progress. When the earliest end is at
    # or before the next start, that room frees up (heapreplace = pop + push).
    ends = []
    for start, end in sorted(meetings):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)
        else:
            heapq.heappush(ends, end)
    return len(ends)


# --- Challenge 4 -------------------------------------------------------------

class CycleError(ValueError):
    def __init__(self, nodes):
        nodes = set(nodes)  # materialize first: we may be given a one-shot generator
        super().__init__(f"dependency cycle among: {sorted(map(str, nodes))}")
        self.cycle_nodes = nodes


def topological_sort(deps):
    # Kahn's algorithm, using a heap instead of a queue so that ties are broken
    # in sorted order.
    dependents = defaultdict(set)
    indegree = {}
    for node, requirements in deps.items():
        indegree.setdefault(node, 0)
        for req in requirements:
            indegree.setdefault(req, 0)
            if node not in dependents[req]:
                dependents[req].add(node)
                indegree[node] += 1
    ready = [n for n, d in indegree.items() if d == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for nxt in dependents[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                heapq.heappush(ready, nxt)
    if len(order) != len(indegree):
        raise CycleError(n for n, d in indegree.items() if d > 0)
    return order


def shortest_path(graph, start, goal):
    dist = {start: 0}
    previous = {}
    heap = [(0, start)]
    while heap:
        d, node = heapq.heappop(heap)
        if node == goal:
            path = [goal]
            while path[-1] != start:
                path.append(previous[path[-1]])
            return d, path[::-1]
        if d > dist.get(node, math.inf):
            continue  # stale heap entry, a shorter path was already found
        for neighbor, weight in graph.get(node, {}).items():
            nd = d + weight
            if nd < dist.get(neighbor, math.inf):
                dist[neighbor] = nd
                previous[neighbor] = node
                heapq.heappush(heap, (nd, neighbor))
    return math.inf, []


def word_ladder(begin, end, words):
    # Neighbors are found through wildcard buckets: "h*t" -> {"hit", "hot", "hat"}.
    # Building the buckets is O(N * L), and each BFS step is then cheap, instead
    # of comparing every pair of words (O(N^2 * L)).
    vocab = set(words)
    if end not in vocab:
        return 0
    vocab.add(begin)
    buckets = defaultdict(list)
    for w in vocab:
        for i in range(len(w)):
            buckets[w[:i] + "*" + w[i + 1:]].append(w)
    queue = deque([(begin, 1)])
    seen = {begin}
    while queue:
        word, depth = queue.popleft()
        if word == end:
            return depth
        for i in range(len(word)):
            pattern = word[:i] + "*" + word[i + 1:]
            for nxt in buckets.pop(pattern, ()):  # pop: each bucket is used once
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, depth + 1))
    return 0


# --- Challenge 5 -------------------------------------------------------------
# low  = max-heap (negated values) holding the smaller half
# high = min-heap holding the larger half
# Invariant: len(low) == len(high) or len(low) == len(high) + 1

class RunningMedian:
    def __init__(self):
        self._low, self._high = [], []

    def add(self, x):
        heapq.heappush(self._low, -x)
        heapq.heappush(self._high, -heapq.heappop(self._low))  # move the max of low to high
        if len(self._high) > len(self._low):
            heapq.heappush(self._low, -heapq.heappop(self._high))

    def median(self):
        if not self._low:
            raise ValueError("median of empty stream")
        if len(self._low) > len(self._high):
            return -self._low[0]
        return (-self._low[0] + self._high[0]) / 2

    def __len__(self):
        return len(self._low) + len(self._high)
