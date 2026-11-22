# Advanced 03 — Algorithms & Data Structures

Interview-grade problems solved the Pythonic way. For each one, think about
**time and space complexity** before you code.

## Toolbox recap

| Need | Structure | Cost |
|---|---|---|
| O(1) membership / lookup | `set`, `dict` | avg O(1) |
| FIFO queue / BFS | `collections.deque` | O(1) both ends |
| Smallest-first / Dijkstra | `heapq` | push/pop O(log n) |
| Ordered recency (LRU) | `OrderedDict` or dict + doubly linked list | O(1) |
| Prefix search | trie (nested dicts or node objects) | O(len(word)) |
| Sorted insert / range query | `bisect` on a list | O(log n) search, O(n) insert |

## Patterns

- **Graph traversal**: BFS (shortest path in unweighted graphs) with a `deque`;
  DFS with recursion or an explicit stack.
- **Topological sort (Kahn's algorithm)**: count in-degrees, start a queue with
  the nodes whose in-degree is 0, and remove their edges as you pop them. If any
  nodes are left over, the graph has a cycle.
- **Dijkstra**: a heap of `(distance, node)`. Skip stale entries when popped
  (`if d > dist[node]: continue`). It only works with non-negative weights.
- **Two heaps for a running median**: a max-heap for the low half (store negatives)
  and a min-heap for the high half. Keep their sizes within 1 of each other.
- **Sort and sweep**: intervals, meeting rooms, merges. Sort by start, then walk once.
- **Doubly linked list + hash map**: O(1) LRU. Sentinel head/tail nodes remove edge cases.

## Complexity checklist

Ask yourself: what is *n*? What dominates? Is there a hidden O(n) inside the loop
(`list.pop(0)`, `x in list`, string `+=` in a loop, `sorted()` inside a loop)?

---

Run: `python academy.py check a3`. The answers, with explanations, are in `solution.py`.
