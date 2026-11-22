"""Advanced 05: Advanced asyncio.

Run: python academy.py check a5
"""

from __future__ import annotations

import asyncio
import functools
from contextlib import asynccontextmanager
from typing import Any, AsyncIterable, AsyncIterator, Awaitable, Callable, TypeVar

T = TypeVar("T")


# --- Challenge 1: async iteration helpers --------------------------------------------

class ARange:
    """A class-based ASYNC iterator (no async generator allowed here):

        [x async for x in ARange(3)]          -> [0, 1, 2]
        ARange(3, delay=0.01)                 -> awaits asyncio.sleep(delay) before each item
    """

    def __init__(self, n: int, delay: float = 0) -> None:
        raise NotImplementedError


async def achunked(source: AsyncIterable[T], size: int) -> AsyncIterator[list[T]]:
    """Async generator: yield lists of `size` items from an async iterable (last may be shorter)."""
    raise NotImplementedError
    yield


async def amerge(*sources: AsyncIterable[T]) -> AsyncIterator[T]:
    """Async generator that yields items from all sources AS THEY ARRIVE
    (interleaved by timing, not source order). Finishes when all sources are
    exhausted. If the consumer stops early (breaks / aclose()), all helper tasks
    must be cancelled. If a source raises, the exception propagates to the consumer.
    """
    raise NotImplementedError
    yield


# --- Challenge 2: retry with exponential backoff -----------------------------------------

async def retry_async(
    factory: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 2.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> T:
    """Call `await factory()`; on one of `exceptions`, wait and retry.
    Delay before retry k (k = 0, 1, 2, ...) is min(base_delay * 2**k, max_delay).
    After `attempts` total failures, re-raise the last exception.
    Never retry on asyncio.CancelledError.
    """
    raise NotImplementedError


# --- Challenge 3: async resource pool ------------------------------------------------------

class AsyncPool:
    """A pool of at most `size` resources created lazily by an async `factory()`.

        pool = AsyncPool(make_connection, size=2)
        async with pool.acquire() as conn:   # waits if all resources are in use
            ...
        pool.created    -> how many resources the factory has created so far
        pool.in_use     -> how many are currently acquired

    - Released resources are reused (LIFO or FIFO, your choice) before creating new ones.
    - A resource is returned to the pool even if the body raises.
    - Waiters are served as resources are released (no busy-waiting).
    """

    def __init__(self, factory: Callable[[], Awaitable[T]], size: int) -> None:
        raise NotImplementedError


# --- Challenge 4: single-flight de-duplication -------------------------------------------------

def single_flight(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """Decorator for an async function with hashable positional args.
    While a call for some args is in flight, other callers with the same args
    await the SAME result instead of starting a new call. Once it finishes
    (successfully or with an error), the next call runs the function again.
    Errors propagate to every waiter. Different args run independently.
    """
    raise NotImplementedError


# --- Challenge 5: all-or-nothing with TaskGroup ---------------------------------------------------

async def all_or_nothing(*factories: Callable[[], Awaitable[Any]]) -> list[Any]:
    """Run all coroutines concurrently using asyncio.TaskGroup.
    - If all succeed: return their results in order.
    - If any fails: the others get cancelled (TaskGroup does that) and you raise
      the FIRST failure's exception itself (unwrapped from the ExceptionGroup).
    """
    raise NotImplementedError
