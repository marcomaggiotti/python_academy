# Advanced 05 — Advanced asyncio

Beyond `gather`: the async versions of the iterator and context manager
protocols, structured concurrency, and the concurrency primitives you build
production systems with.

## 1. Async iterators and generators

```python
async def ticker(n):              # an async generator: async def + yield
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

async for x in ticker(3): ...
squares = [x * x async for x in ticker(3)]   # async comprehension
```

The protocol is `__aiter__` (a regular method that returns the iterator) and
`async def __anext__` (raises `StopAsyncIteration`).

## 2. Async context managers

```python
class Connection:
    async def __aenter__(self): await self.open(); return self
    async def __aexit__(self, *exc): await self.close()

from contextlib import asynccontextmanager

@asynccontextmanager
async def lease(pool):
    item = await pool.get()
    try:
        yield item
    finally:
        pool.put_nowait(item)
```

## 3. Structured concurrency with `TaskGroup` (3.11+)

```python
async with asyncio.TaskGroup() as tg:
    a = tg.create_task(job(1))
    b = tg.create_task(job(2))
# here both are done, or, if one failed, the others were CANCELLED and an
# ExceptionGroup is raised.
```

Unwrap a group with `except* SomeError as eg:` or by inspecting `eg.exceptions`.

## 4. Sharing futures: "single flight"

When 100 coroutines ask for the same expensive key at the same time, start the
work **once** and make everyone else `await` the same `asyncio.Future`/`Task`.
Remove it when it's done so the next caller gets fresh data.

## 5. Merging async streams

Start one task per source that pushes items into an `asyncio.Queue`, plus a
sentinel when the source is finished. The consumer yields items as they arrive
and stops once it has seen every sentinel. Always cancel the helper tasks in a
`finally`, because the consumer might stop early.

## 6. Testability: inject time

Pass `sleep=asyncio.sleep` (or a clock) as a parameter. Tests can then pass a
fake that records the delays and returns at once, so the tests are fast and
deterministic.

## 7. Cancellation etiquette

`CancelledError` is a `BaseException`. Don't swallow it. Clean up in `finally`
and re-raise. `asyncio.shield()` protects an inner awaitable from outer cancellation.

---

Run: `python academy.py check a5`. The answers, with explanations, are in `solution.py`.
