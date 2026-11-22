# Module 04 — Iterators & Generators

## 1. The iteration protocol

- An **iterable** has `__iter__()` returning an iterator (lists, dicts, files...).
- An **iterator** has `__next__()` (raises `StopIteration` when done) and an
  `__iter__()` that returns itself.

`for x in obj` is really:

```python
it = iter(obj)
while True:
    try:
        x = next(it)
    except StopIteration:
        break
    ...
```

Iterators are **single-use**: once exhausted, they stay exhausted. An iterable
(like a list) can produce fresh iterators again and again.

## 2. Generators

A function containing `yield` returns a generator — an iterator whose state is
the paused function frame:

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1
```

Generators are **lazy**: nothing runs until you ask for the next value. This
makes them ideal for big files, infinite sequences, and streaming pipelines.

## 3. `yield from`

Delegates to a sub-iterator (and handles recursion elegantly):

```python
def walk(tree):
    yield tree.value
    for child in tree.children:
        yield from walk(child)
```

## 4. Generator pipelines

Chain small generators like Unix pipes. Each stage pulls one item at a time:

```python
lines   = (line.rstrip() for line in open("app.log"))
errors  = (l for l in lines if "ERROR" in l)
codes   = (l.split()[2] for l in errors)
```

## 5. `send()` — generators as coroutines

`value = yield result` both produces `result` and receives whatever the caller
passes to `gen.send(value)`. You must "prime" the generator with `next(gen)`
first (which runs it up to the first `yield`).

```python
def accumulator():
    total = 0
    while True:
        x = yield total
        total += x

acc = accumulator(); next(acc)    # prime -> 0
acc.send(5)   # 5
acc.send(10)  # 15
```

## 6. Useful built-ins

`iter(callable, sentinel)`, `next(it, default)`, `itertools.islice`,
`itertools.chain`, `itertools.count`, `zip`, `enumerate`, `reversed`.

---

Run: `python academy.py check 04`
