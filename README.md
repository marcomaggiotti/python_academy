# 🐍 Python Academy — Intermediate → Advanced

A hands-on study track for people who already know Python basics (variables,
loops, functions, lists/dicts) and want to write code like an experienced
Python developer.

Each module has:

| File | Purpose |
|---|---|
| `LESSON.md` | Short, dense notes with examples — read this first |
| `exercises.py` | Stubs for you to implement (`raise NotImplementedError`) |
| `test_exercises.py` | Tests that tell you when you got it right |
| `solution.py` | Reference solution — **only peek after a real attempt** |

## Setup

Requires **Python 3.11+**.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install pytest
```

## Workflow

```bash
python academy.py list            # see all modules and projects
python academy.py check 01        # run tests for module 01 (verbose)
python academy.py check p1        # run tests for project 1
python academy.py check 03 -k vector   # only tests matching "vector"
python academy.py progress        # scoreboard across everything
```

The loop: read `LESSON.md` → implement one function in `exercises.py` →
`python academy.py check NN` → repeat until green → move on.

To verify the reference solutions pass the tests (or compare behaviour):

```bash
python academy.py verify
```

## Curriculum

| # | Module | Key topics |
|---|---|---|
| 01 | Pythonic Idioms | comprehensions, unpacking, `zip`/`sorted(key=)`, walrus, `match`/`case` |
| 02 | Functions & Decorators | closures, `nonlocal`, late binding, decorators (with args, with state), `functools.wraps`, `inspect` |
| 03 | OOP & the Data Model | dunder methods, operator overloading, `NotImplemented`, properties, classmethods, dataclasses, ABCs, sequences |
| 04 | Iterators & Generators | iteration protocol, `yield`/`yield from`, laziness, pipelines, `send()` coroutines |
| 05 | Exceptions & Context Managers | exception hierarchies, chaining (`from`), `ExceptionGroup`, `__enter__/__exit__`, `@contextmanager` |
| 06 | Stdlib Power Tools | `collections`, `itertools`, `functools` (`lru_cache`, `singledispatch`), `heapq`, `bisect` |
| 07 | Typing & Protocols | generics, `TypeVar`, `Protocol`, `TypedDict`, `Enum` state machines, Result types |
| 08 | Concurrency & asyncio | thread pools, locks, `gather`, semaphores, timeouts, racing & cancellation, queues |

### Capstone projects

| # | Project | Combines |
|---|---|---|
| P1 | Personal Finance Ledger | `Decimal` money, dataclasses, generators, CSV import with error reporting, JSON round-trip |
| P2 | Access Log Analyzer CLI | regex with named groups, single-pass streaming stats, percentiles, `argparse`, stdout/stderr |

Projects have a longer spec in their `LESSON.md` and a near-empty
`exercises.py` — you design the internals.

## Tips for getting the most out of it

- **Don't read the solution first.** Struggle productively for 15–20 minutes.
- After passing, **compare with `solution.py`** — there's often a more idiomatic trick.
- Read the tests: they're executable specifications and show edge cases.
- Bonus: run `pip install mypy ruff` then `mypy --strict` and `ruff check` on your work.
- Extend: add your own tests for edge cases you think are missing.

## Where to go next

Descriptors and metaclasses, `__slots__` and memory, packaging (`pyproject.toml`),
profiling (`cProfile`, `timeit`), `pytest` fixtures & mocking, and building a
real project (a FastAPI service, a CLI with `typer`, a data pipeline with `polars`).
