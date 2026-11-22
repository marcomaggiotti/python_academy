import asyncio
import inspect
import time

import pytest

from academy_loader import load

ex = load(__file__)


def run(coro):
    return asyncio.run(coro)


async def timed_source(items, delay):
    for item in items:
        await asyncio.sleep(delay)
        yield item


# --- Challenge 1 ---------------------------------------------------------------

def test_arange():
    async def main():
        return [x async for x in ex.ARange(3)], [x async for x in ex.ARange(2, delay=0.01)]

    assert run(main()) == ([0, 1, 2], [0, 1])
    assert not inspect.isasyncgenfunction(ex.ARange.__anext__)
    assert hasattr(ex.ARange, "__anext__")


def test_achunked():
    async def main():
        return [c async for c in ex.achunked(ex.ARange(7), 3)]

    assert run(main()) == [[0, 1, 2], [3, 4, 5], [6]]


def test_amerge_interleaves_by_time():
    async def main():
        fast = timed_source(["f1", "f2", "f3"], 0.02)
        slow = timed_source(["s1", "s2"], 0.05)
        return [x async for x in ex.amerge(slow, fast)]

    start = time.perf_counter()
    out = run(main())
    took = time.perf_counter() - start
    assert sorted(out) == ["f1", "f2", "f3", "s1", "s2"]
    assert out[:2] == ["f1", "f2"] and out[-1] == "s2"
    assert took < 0.2, "sources must be consumed concurrently"


def test_amerge_early_exit_cancels():
    cancelled = []

    async def endless(name):
        try:
            while True:
                await asyncio.sleep(0.005)
                yield name
        finally:
            cancelled.append(name)

    async def main():
        gen = ex.amerge(endless("a"), endless("b"))
        got = [await gen.__anext__() for _ in range(4)]
        await gen.aclose()
        await asyncio.sleep(0.02)
        return got

    got = run(main())
    assert len(got) == 4
    assert sorted(cancelled) == ["a", "b"]


def test_amerge_propagates_errors():
    async def broken():
        yield 1
        raise ValueError("source failed")

    async def main():
        return [x async for x in ex.amerge(broken(), timed_source([2], 0.05))]

    with pytest.raises(ValueError, match="source failed"):
        run(main())


# --- Challenge 2 -----------------------------------------------------------------

def test_retry_async_backoff():
    delays, calls = [], []

    async def fake_sleep(d):
        delays.append(d)

    async def flaky():
        calls.append(1)
        if len(calls) < 4:
            raise ConnectionError
        return "ok"

    result = run(ex.retry_async(flaky, attempts=5, base_delay=0.5, max_delay=1.5, sleep=fake_sleep))
    assert result == "ok"
    assert delays == [0.5, 1.0, 1.5]


def test_retry_async_gives_up_and_filters():
    delays = []

    async def fake_sleep(d):
        delays.append(d)

    async def always():
        raise ConnectionError("down")

    with pytest.raises(ConnectionError):
        run(ex.retry_async(always, attempts=3, base_delay=1, sleep=fake_sleep))
    assert delays == [1, 2]

    calls = []

    async def wrong_kind():
        calls.append(1)
        raise KeyError

    with pytest.raises(KeyError):
        run(ex.retry_async(wrong_kind, exceptions=(ConnectionError,), sleep=fake_sleep))
    assert len(calls) == 1


# --- Challenge 3 -------------------------------------------------------------------

def test_async_pool_limits_and_reuses():
    peak = 0

    async def factory():
        await asyncio.sleep(0)
        return object()

    async def main():
        nonlocal peak
        pool = ex.AsyncPool(factory, size=2)
        used = []

        async def job():
            nonlocal peak
            async with pool.acquire() as r:
                used.append(r)
                peak = max(peak, pool.in_use)
                await asyncio.sleep(0.02)

        await asyncio.gather(*(job() for _ in range(6)))
        return pool, used

    start = time.perf_counter()
    pool, used = run(main())
    assert pool.created == 2
    assert len(set(map(id, used))) == 2
    assert peak == 2 and pool.in_use == 0
    assert time.perf_counter() - start >= 0.05  # 3 waves of 0.02s


def test_async_pool_releases_on_error():
    async def factory():
        return "conn"

    async def main():
        pool = ex.AsyncPool(factory, size=1)
        with pytest.raises(RuntimeError):
            async with pool.acquire():
                raise RuntimeError("boom")
        async with pool.acquire() as again:
            return pool, again

    pool, again = run(main())
    assert again == "conn" and pool.created == 1 and pool.in_use == 0


# --- Challenge 4 ---------------------------------------------------------------------

def test_single_flight_dedupes_concurrent_calls():
    calls = []

    @ex.single_flight
    async def load_user(uid):
        calls.append(uid)
        await asyncio.sleep(0.02)
        return {"id": uid}

    async def main():
        results = await asyncio.gather(*(load_user(1) for _ in range(10)), load_user(2))
        again = await load_user(1)
        return results, again

    results, again = run(main())
    assert all(r == {"id": 1} for r in results[:10]) and results[10] == {"id": 2}
    assert calls == [1, 2, 1], "concurrent calls share one execution; later calls run again"
    assert again == {"id": 1}


def test_single_flight_errors_reach_everyone_and_reset():
    calls = []

    @ex.single_flight
    async def flaky(k):
        calls.append(k)
        await asyncio.sleep(0.01)
        if len(calls) == 1:
            raise ValueError("first time fails")
        return "ok"

    async def main():
        results = await asyncio.gather(flaky("a"), flaky("a"), return_exceptions=True)
        return results, await flaky("a")

    results, later = run(main())
    assert all(isinstance(r, ValueError) for r in results)
    assert later == "ok" and calls == ["a", "a"]


# --- Challenge 5 -------------------------------------------------------------------------

def test_all_or_nothing_success():
    async def job(x, d):
        await asyncio.sleep(d)
        return x

    out = run(ex.all_or_nothing(lambda: job(1, 0.02), lambda: job(2, 0.01)))
    assert out == [1, 2]


def test_all_or_nothing_failure_cancels_and_unwraps():
    cancelled = []

    async def slow():
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            cancelled.append("slow")
            raise

    async def bad():
        await asyncio.sleep(0.01)
        raise KeyError("bad job")

    start = time.perf_counter()
    with pytest.raises(KeyError):
        run(ex.all_or_nothing(slow, bad))
    assert cancelled == ["slow"]
    assert time.perf_counter() - start < 0.5
