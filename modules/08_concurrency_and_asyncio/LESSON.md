# Module 08 — Concurrency: Threads & asyncio

## Which tool when?

| Workload                       | Tool                                   |
|--------------------------------|----------------------------------------|
| I/O-bound, few blocking calls  | `concurrent.futures.ThreadPoolExecutor` |
| I/O-bound, many connections    | `asyncio`                              |
| CPU-bound (pure Python math)   | `ProcessPoolExecutor` / `multiprocessing` (sidesteps the GIL) |

The **GIL** lets only one thread run Python bytecode at a time, so threads help
when you *wait* (network, disk), not when you *compute*. (Free-threaded builds
of Python 3.13+ are changing this, but the advice above still holds by default.)

## 1. Threads with `concurrent.futures`

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(download, urls))         # keeps input order
    futures = [pool.submit(download, u) for u in urls]
    for fut in as_completed(futures):                # completion order
        print(fut.result())
```

Shared mutable state needs a lock — `count += 1` is *not* atomic:

```python
lock = threading.Lock()
with lock:
    count += 1
```

## 2. asyncio fundamentals

```python
import asyncio

async def fetch(url):              # calling fetch() creates a coroutine object
    await asyncio.sleep(1)         # yield control while waiting
    return url

async def main():
    results = await asyncio.gather(*(fetch(u) for u in urls))   # concurrent
    async with asyncio.TaskGroup() as tg:                       # 3.11+, structured
        t = tg.create_task(fetch("x"))
    print(t.result())

asyncio.run(main())                # the single entry point
```

Key tools:

- `asyncio.gather(*aws, return_exceptions=True)` — run many, collect results in order.
- `asyncio.Semaphore(n)` — limit how many run at once (`async with sem:`).
- `asyncio.wait_for(aw, timeout)` / `asyncio.timeout(s)` — deadlines (`TimeoutError`).
- `asyncio.Queue` — producer/consumer pipelines; `queue.join()` + `task_done()`.
- `asyncio.wait(tasks, return_when=FIRST_COMPLETED)` — race; cancel the losers.
- **Never** call blocking functions (`time.sleep`, `requests.get`) inside a coroutine —
  use `await asyncio.to_thread(blocking_fn, ...)` instead.

---

Run: `python academy.py check 08`
