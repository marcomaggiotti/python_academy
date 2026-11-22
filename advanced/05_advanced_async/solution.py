"""Answers for Advanced 05, with explanations."""

from __future__ import annotations

import asyncio
import functools
from contextlib import asynccontextmanager


# --- Challenge 1 -------------------------------------------------------------

class ARange:
    def __init__(self, n, delay=0):
        self.n, self.delay, self.i = n, delay, 0

    def __aiter__(self):           # NOT async: it returns the iterator directly
        return self

    async def __anext__(self):
        if self.i >= self.n:
            raise StopAsyncIteration
        if self.delay:
            await asyncio.sleep(self.delay)
        value, self.i = self.i, self.i + 1
        return value


async def achunked(source, size):
    chunk = []
    async for item in source:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


_DONE = object()


async def amerge(*sources):
    # One pump task per source pushes ("item", value), ("error", exc), or the
    # _DONE sentinel into a shared queue. The finally block runs on normal
    # completion, on errors, AND when the consumer calls aclose() or breaks out
    # (GeneratorExit), so the pumps never leak.
    queue = asyncio.Queue()

    async def pump(src):
        try:
            async for item in src:
                await queue.put(("item", item))
        except Exception as exc:  # CancelledError is BaseException: not caught
            await queue.put(("error", exc))
        finally:
            await queue.put(("done", _DONE))

    tasks = [asyncio.create_task(pump(s)) for s in sources]
    remaining = len(tasks)
    try:
        while remaining:
            kind, value = await queue.get()
            if kind == "item":
                yield value
            elif kind == "error":
                raise value
            else:
                remaining -= 1
    finally:
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


# --- Challenge 2 -------------------------------------------------------------

async def retry_async(factory, *, attempts=3, base_delay=0.1, max_delay=2.0,
                      exceptions=(Exception,), sleep=asyncio.sleep):
    for k in range(attempts):
        try:
            return await factory()
        except asyncio.CancelledError:
            raise  # explicit, in case someone passes BaseException in `exceptions`
        except exceptions:
            if k == attempts - 1:
                raise
            await sleep(min(base_delay * 2**k, max_delay))


# --- Challenge 3 -------------------------------------------------------------
# A Semaphore caps concurrency at `size` and handles fair waking of waiters.
# Idle resources sit in a list; we only call the factory when none is idle.

class AsyncPool:
    def __init__(self, factory, size):
        self._factory = factory
        self._sem = asyncio.Semaphore(size)
        self._idle = []
        self.created = 0
        self.in_use = 0

    @asynccontextmanager
    async def acquire(self):
        async with self._sem:
            if self._idle:
                resource = self._idle.pop()
            else:
                self.created += 1
                try:
                    resource = await self._factory()
                except BaseException:
                    self.created -= 1
                    raise
            self.in_use += 1
            try:
                yield resource
            finally:
                self.in_use -= 1
                self._idle.append(resource)


# --- Challenge 4 -------------------------------------------------------------
# Keep a dict of in-flight Tasks keyed by args. Callers await the shared task.
# A done-callback removes the entry no matter how the task ends. Awaiting a task
# that raised re-raises the same exception in every waiter.

def single_flight(func):
    in_flight = {}

    @functools.wraps(func)
    async def wrapper(*args):
        task = in_flight.get(args)
        if task is None:
            task = asyncio.ensure_future(func(*args))
            in_flight[args] = task
            task.add_done_callback(lambda _t, key=args: in_flight.pop(key, None))
        # shield: if ONE waiter is cancelled, the shared work keeps going for the others
        return await asyncio.shield(task)

    wrapper.in_flight = in_flight
    return wrapper


# --- Challenge 5 -------------------------------------------------------------

async def all_or_nothing(*factories):
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(f()) for f in factories]
    except BaseExceptionGroup as group:
        # The group lists the exceptions in the order they were raised.
        raise group.exceptions[0] from None
    return [t.result() for t in tasks]
