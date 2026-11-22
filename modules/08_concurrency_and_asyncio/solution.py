"""Reference solutions for Module 08."""

from __future__ import annotations

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor


def parallel_map(func, items, max_workers=8):
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(func, items))


class ThreadSafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self, n=1):
        with self._lock:
            self._value += n

    @property
    def value(self):
        return self._value


async def fetch_all(urls, fetch):
    results = await asyncio.gather(*(fetch(u) for u in urls))
    return dict(zip(urls, results))


async def fetch_all_safe(urls, fetch):
    results = await asyncio.gather(*(fetch(u) for u in urls), return_exceptions=True)
    ok, failed = {}, {}
    for url, result in zip(urls, results):
        (failed if isinstance(result, Exception) else ok)[url] = result
    return ok, failed


async def bounded_gather(items, worker, limit):
    sem = asyncio.Semaphore(limit)

    async def run(item):
        async with sem:
            return await worker(item)

    return await asyncio.gather(*(run(i) for i in items))


async def with_timeout(aw, seconds, default):
    try:
        return await asyncio.wait_for(aw, timeout=seconds)
    except TimeoutError:
        return default


async def race(*coro_factories):
    tasks = [asyncio.ensure_future(f()) for f in coro_factories]
    try:
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    finally:
        for t in tasks:
            if not t.done():
                t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    return next(iter(done)).result()


async def process_queue(items, handler, workers):
    queue = asyncio.Queue()
    for item in items:
        queue.put_nowait(item)
    results = []

    async def consumer():
        while True:
            item = await queue.get()
            try:
                results.append(await handler(item))
            finally:
                queue.task_done()

    tasks = [asyncio.create_task(consumer()) for _ in range(workers)]
    await queue.join()
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    return sorted(results)


async def run_blocking(func, *args):
    return await asyncio.to_thread(func, *args)
