import asyncio
import threading
import time

import pytest

from academy_loader import load

ex = load(__file__)


def elapsed(fn):
    start = time.perf_counter()
    result = fn()
    return result, time.perf_counter() - start


# --- Threads ----------------------------------------------------------------------

def test_parallel_map_order_and_speed():
    def slow_square(x):
        time.sleep(0.1)
        return x * x

    result, took = elapsed(lambda: ex.parallel_map(slow_square, range(8), max_workers=8))
    assert result == [x * x for x in range(8)]
    assert took < 0.5, f"took {took:.2f}s — not running in parallel?"


def test_thread_safe_counter():
    c = ex.ThreadSafeCounter()

    def work():
        for _ in range(10_000):
            c.increment()

    threads = [threading.Thread(target=work) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert c.value == 80_000
    c.increment(5)
    assert c.value == 80_005
    with pytest.raises(AttributeError):
        c.value = 0


# --- asyncio ------------------------------------------------------------------------

async def fake_fetch(url):
    await asyncio.sleep(0.1)
    if "bad" in url:
        raise ConnectionError(url)
    return len(url)


def test_fetch_all_concurrent():
    urls = [f"https://site{i}.test" for i in range(10)]
    result, took = elapsed(lambda: asyncio.run(ex.fetch_all(urls, fake_fetch)))
    assert result == {u: len(u) for u in urls}
    assert took < 0.5


def test_fetch_all_safe():
    urls = ["a.test", "bad.test", "c.test"]
    ok, failed = asyncio.run(ex.fetch_all_safe(urls, fake_fetch))
    assert ok == {"a.test": 6, "c.test": 6}
    assert list(failed) == ["bad.test"]
    assert isinstance(failed["bad.test"], ConnectionError)


def test_bounded_gather_respects_limit():
    running = 0
    peak = 0

    async def worker(x):
        nonlocal running, peak
        running += 1
        peak = max(peak, running)
        await asyncio.sleep(0.05)
        running -= 1
        return x * 2

    result, took = elapsed(lambda: asyncio.run(ex.bounded_gather(list(range(9)), worker, limit=3)))
    assert result == [x * 2 for x in range(9)]
    assert peak == 3
    assert took < 0.4


def test_with_timeout():
    async def slow():
        await asyncio.sleep(5)
        return "slow"

    async def fast():
        await asyncio.sleep(0.01)
        return "fast"

    assert asyncio.run(ex.with_timeout(fast(), 1, "default")) == "fast"
    result, took = elapsed(lambda: asyncio.run(ex.with_timeout(slow(), 0.05, "default")))
    assert result == "default" and took < 1


def test_race_cancels_losers():
    cancelled = []

    def make(delay, value):
        async def coro():
            try:
                await asyncio.sleep(delay)
                return value
            except asyncio.CancelledError:
                cancelled.append(value)
                raise

        return coro

    async def main():
        return await ex.race(make(0.3, "slow"), make(0.01, "fast"), make(0.2, "medium"))

    result, took = elapsed(lambda: asyncio.run(main()))
    assert result == "fast"
    assert sorted(cancelled) == ["medium", "slow"]
    assert took < 0.25


def test_process_queue():
    seen_workers = set()

    async def handler(x):
        seen_workers.add(id(asyncio.current_task()))
        await asyncio.sleep(0.05)
        return x * 10

    result, took = elapsed(lambda: asyncio.run(ex.process_queue([5, 3, 1, 4, 2, 6], handler, workers=3)))
    assert result == [10, 20, 30, 40, 50, 60]
    assert len(seen_workers) == 3
    assert took < 0.3


def test_run_blocking_does_not_block_loop():
    def blocking():
        time.sleep(0.2)
        return "done"

    async def main():
        ticks = 0

        async def ticker():
            nonlocal ticks
            for _ in range(10):
                await asyncio.sleep(0.01)
                ticks += 1

        async def call():
            value = await ex.run_blocking(blocking)
            return value, ticks  # how many ticks happened while blocking() ran

        (result, ticks_during), _ = await asyncio.gather(call(), ticker())
        return result, ticks_during

    result, ticks_during = asyncio.run(main())
    assert result == "done"
    assert ticks_during >= 5, "the event loop was blocked while the function ran"
