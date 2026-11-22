"""Module 08 — Concurrency: Threads & asyncio.

The tests use small sleeps and measure wall time, so sequential solutions
will fail. Run: python academy.py check 08
"""

from __future__ import annotations

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Awaitable, Callable, Iterable, TypeVar

T = TypeVar("T")
R = TypeVar("R")


# --- Threads ----------------------------------------------------------------------

def parallel_map(func: Callable[[T], R], items: Iterable[T], max_workers: int = 8) -> list[R]:
    """Apply a (blocking, I/O-bound) func to every item using a thread pool.
    Results must be in the same order as the input."""
    raise NotImplementedError


class ThreadSafeCounter:
    """A counter safe to increment from many threads at once.
      c.increment(n=1) ; c.value  (read-only property)
    """

    def __init__(self) -> None:
        raise NotImplementedError


# --- asyncio ------------------------------------------------------------------------

async def fetch_all(urls: list[str], fetch: Callable[[str], Awaitable[Any]]) -> dict[str, Any]:
    """Call `await fetch(url)` for every url CONCURRENTLY and return {url: result}."""
    raise NotImplementedError


async def fetch_all_safe(urls: list[str], fetch: Callable[[str], Awaitable[Any]]) -> tuple[dict, dict]:
    """Like fetch_all, but one failure must not kill the others.
    Return (successes, failures) where failures maps url -> the exception object.
    """
    raise NotImplementedError


async def bounded_gather(items: list[T], worker: Callable[[T], Awaitable[R]], limit: int) -> list[R]:
    """Run worker(item) for all items with AT MOST `limit` running at the same time.
    Return results in input order. Hint: asyncio.Semaphore."""
    raise NotImplementedError


async def with_timeout(aw: Awaitable[T], seconds: float, default: T) -> T:
    """Await `aw`; if it takes longer than `seconds`, cancel it and return `default`."""
    raise NotImplementedError


async def race(*coro_factories: Callable[[], Awaitable[T]]) -> T:
    """Start every coroutine (call each factory), return the result of whichever
    finishes first, and CANCEL all the others before returning."""
    raise NotImplementedError


async def process_queue(items: Iterable[T], handler: Callable[[T], Awaitable[R]], workers: int) -> list[R]:
    """Producer/consumer: put all items on an asyncio.Queue, start `workers`
    consumer tasks that `await handler(item)` and collect results. When all items
    are processed, stop the workers and return the results SORTED.
    """
    raise NotImplementedError


async def run_blocking(func: Callable[..., R], *args: Any) -> R:
    """Run a blocking (non-async) function without blocking the event loop."""
    raise NotImplementedError
