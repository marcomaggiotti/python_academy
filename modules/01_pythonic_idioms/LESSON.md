# Module 01 — Pythonic Idioms & Comprehensions

You already know loops, lists and dicts. This module is about writing them the
way experienced Python developers do: shorter, clearer, and usually faster.

## 1. Comprehensions (list, dict, set) and generator expressions

```python
squares = [n * n for n in range(10) if n % 2 == 0]
by_len  = {word: len(word) for word in words}
initials = {name[0] for name in names}
total = sum(n * n for n in range(1_000_000))   # no list built in memory
```

Nested comprehensions read **left to right like the equivalent `for` loops**:

```python
flat = [x for row in matrix for x in row]
# for row in matrix:
#     for x in row:
#         flat.append(x)
```

Rule of thumb: if a comprehension needs more than two `for`/`if` clauses,
write a normal loop or a helper function.

## 2. Unpacking

```python
first, *middle, last = [1, 2, 3, 4, 5]     # middle == [2, 3, 4]
a, b = b, a                                # swap
for i, (name, score) in enumerate(pairs, start=1): ...
merged = {**defaults, **overrides}         # later keys win
combined = [*list_a, *list_b]
```

## 3. `zip`, `enumerate`, `sorted(key=...)`, `min/max(key=...)`

```python
for name, age in zip(names, ages, strict=True): ...   # 3.10+: errors on length mismatch
transposed = list(zip(*matrix))
sorted(people, key=lambda p: (-p["score"], p["name"]))  # score desc, name asc
oldest = max(people, key=lambda p: p["age"])
```

Sorting in Python is **stable**, so you can also sort in multiple passes.

## 4. The walrus operator `:=`

Assign inside an expression — handy in comprehensions and `while` loops:

```python
results = [y for x in data if (y := expensive(x)) is not None]
while (line := f.readline()):
    ...
```

## 5. Truthiness, `any` / `all`, and the `dict` API

```python
if not items: ...                        # empty containers are falsy
any(n < 0 for n in nums); all(s.isdigit() for s in parts)
counts[key] = counts.get(key, 0) + 1
groups.setdefault(key, []).append(value)
```

## 6. Structural pattern matching (3.10+)

```python
match command.split():
    case ["go", direction]:
        move(direction)
    case ["take", *objects] if objects:
        take(objects)
    case {"type": "point", "x": x, "y": y}:   # works on dicts too
        ...
    case _:
        print("unknown")
```

---

## Exercises

Open `exercises.py`, implement each function (replace `raise NotImplementedError`),
then run:

```bash
python academy.py check 01
```

Stuck? Read the docstring again, then look at `solution.py` as a last resort.
