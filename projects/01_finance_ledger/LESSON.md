# Project 01 — Personal Finance Ledger

A capstone that combines **dataclasses, properties, exceptions, generators,
`decimal`, `datetime`, `csv` and `json`** into one small but realistic library.

## Why cents and `Decimal`?

```python
>>> 0.1 + 0.2
0.30000000000000004
```

Never store money as `float`. Parse user input with `decimal.Decimal` and
store integer **cents**:

```python
from decimal import Decimal, InvalidOperation
cents = int((Decimal("12.345")).quantize(Decimal("0.01")) * 100)   # 1234 or 1235? check rounding!
```

Use `ROUND_HALF_UP` explicitly: `Decimal("12.345").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.

## Specification

Implement everything in `exercises.py`:

### `parse_amount(text) -> int`
`"12.50"` → `1250`, `"-3"` → `-300`, `"1,234.56"` → `123456` (commas ignored),
`"0.005"` → `1` (round half up). Invalid → `ValueError`.

### `Transaction` (frozen dataclass)
Fields: `id: int`, `date: datetime.date`, `description: str`, `cents: int`, `category: str`.
- `is_expense` property (`cents < 0`)
- `month` property → `"YYYY-MM"`

### `Ledger`
| Method | Behaviour |
|---|---|
| `add(date, description, amount, category="uncategorized")` | `date` is a `date` or ISO string `"2026-01-31"`; `amount` is a str (via `parse_amount`) or int cents. Empty description → `ValueError`. Returns the new `Transaction`. IDs start at 1 and increase. Category is lower-cased & stripped. |
| `remove(tx_id)` | Remove; unknown id → `KeyError`. |
| `len(ledger)`, `iter(ledger)` | Transactions sorted by `(date, id)`. |
| `balance()` | Sum of cents. |
| `filter(start=None, end=None, category=None)` | **Generator** of transactions; `start`/`end` inclusive (dates). |
| `totals_by_category(expenses_only=False)` | `{category: cents}`, sorted by amount ascending (biggest expense first). |
| `monthly_summary()` | `{"2026-01": {"income": +c, "expenses": -c, "net": c}, ...}` sorted by month. |
| `to_json()` / `Ledger.from_json(text)` | Round-trip all transactions (ids preserved, next id continues after the max). |
| `import_csv(text)` | CSV with header `date,description,amount,category`. Valid rows are added; invalid rows are skipped. Returns `(imported_count, errors)` where `errors` is a list of `(line_number, message)`; header is line 1. |

### Bonus (untested)
Add a small CLI with `argparse` — `python exercises.py add 2026-01-03 "Coffee" -3.50 food` —
that persists to a JSON file.

Run: `python academy.py check p1`
