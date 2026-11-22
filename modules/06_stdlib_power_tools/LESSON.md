# Module 06 — Standard Library Power Tools

The fastest code is code you don't write. These modules solve 80% of everyday
data-wrangling problems.

## `collections`

```python
from collections import Counter, defaultdict, deque, namedtuple, ChainMap

Counter("mississippi").most_common(2)      # [('i', 4), ('s', 4)]
groups = defaultdict(list); groups[k].append(v)   # no KeyError, no setdefault
q = deque(maxlen=3); q.append(x); q.appendleft(y); q.rotate(1)   # O(1) both ends
Point = namedtuple("Point", "x y")
settings = ChainMap(cli_args, env_vars, defaults)  # first mapping that has the key wins
```

## `itertools`

```python
from itertools import groupby, accumulate, chain, combinations, permutations, product, pairwise, islice, count

[(k, len(list(g))) for k, g in groupby("aaabcc")]   # groupby needs SORTED/consecutive input
list(accumulate([3, 1, 4], max))                     # running max -> [3, 3, 4]
list(combinations("abc", 2))                         # ab ac bc
list(product([0, 1], repeat=2))                      # 00 01 10 11
list(pairwise([1, 2, 3]))                            # (1,2) (2,3)   (3.10+)
```

## `functools`

```python
from functools import lru_cache, cache, partial, reduce, singledispatch

@cache                     # memoize — turns exponential recursion into linear
def fib(n): return n if n < 2 else fib(n - 1) + fib(n - 2)

int_from_binary = partial(int, base=2)

@singledispatch            # function overloading by type of first argument
def show(x): return f"object {x}"
@show.register
def _(x: int): return f"int {x}"
```

## `heapq` and `bisect`

```python
import heapq, bisect
heapq.nsmallest(3, data); heapq.nlargest(3, data, key=...)
heap = []; heapq.heappush(heap, (priority, counter, item)); heapq.heappop(heap)
heapq.merge(sorted_a, sorted_b)                # lazy merge of sorted inputs

bisect.bisect_right([60, 70, 80, 90], 75)      # -> 2 (insertion index in a sorted list)
bisect.insort(sorted_list, value)
```

`heapq` is a **min-heap** on a plain list. Add a tie-breaking counter so items
that compare equal on priority never get compared themselves.

## Others worth knowing

`operator.itemgetter/attrgetter`, `statistics`, `datetime`, `pathlib`, `json`,
`csv`, `re`, `textwrap`, `dataclasses`, `enum`.

---

Run: `python academy.py check 06`
