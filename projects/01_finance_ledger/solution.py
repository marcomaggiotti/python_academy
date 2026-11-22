"""Reference solution for Project 01."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict, dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


def parse_amount(text):
    cleaned = str(text).replace(",", "").strip()
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        raise ValueError(f"invalid amount: {text!r}") from None
    if not value.is_finite():
        raise ValueError(f"invalid amount: {text!r}")
    return int(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100)


@dataclass(frozen=True)
class Transaction:
    id: int
    date: date
    description: str
    cents: int
    category: str

    @property
    def is_expense(self):
        return self.cents < 0

    @property
    def month(self):
        return self.date.strftime("%Y-%m")


class Ledger:
    def __init__(self):
        self._txs: dict[int, Transaction] = {}
        self._next_id = 1

    def add(self, when, description, amount, category="uncategorized", *, tx_id=None):
        if isinstance(when, str):
            when = date.fromisoformat(when.strip())
        if not isinstance(when, date):
            raise TypeError("date must be a date or ISO string")
        description = description.strip()
        if not description:
            raise ValueError("description required")
        cents = amount if isinstance(amount, int) else parse_amount(amount)
        if tx_id is None:
            tx_id = self._next_id
        self._next_id = max(self._next_id, tx_id + 1)
        tx = Transaction(tx_id, when, description, cents, category.strip().lower() or "uncategorized")
        self._txs[tx_id] = tx
        return tx

    def remove(self, tx_id):
        del self._txs[tx_id]

    def __len__(self):
        return len(self._txs)

    def __iter__(self):
        return iter(sorted(self._txs.values(), key=lambda t: (t.date, t.id)))

    def balance(self):
        return sum(t.cents for t in self._txs.values())

    def filter(self, start=None, end=None, category=None):
        for tx in self:
            if start and tx.date < start:
                continue
            if end and tx.date > end:
                continue
            if category and tx.category != category.lower():
                continue
            yield tx

    def totals_by_category(self, expenses_only=False):
        totals: dict[str, int] = {}
        for tx in self:
            if expenses_only and not tx.is_expense:
                continue
            totals[tx.category] = totals.get(tx.category, 0) + tx.cents
        return dict(sorted(totals.items(), key=lambda kv: (kv[1], kv[0])))

    def monthly_summary(self):
        summary: dict[str, dict[str, int]] = {}
        for tx in self:
            m = summary.setdefault(tx.month, {"income": 0, "expenses": 0, "net": 0})
            m["expenses" if tx.is_expense else "income"] += tx.cents
            m["net"] += tx.cents
        return dict(sorted(summary.items()))

    def to_json(self):
        rows = [{**asdict(t), "date": t.date.isoformat()} for t in self]
        return json.dumps(rows, indent=2)

    @classmethod
    def from_json(cls, text):
        ledger = cls()
        for row in json.loads(text):
            ledger.add(row["date"], row["description"], row["cents"], row["category"], tx_id=row["id"])
        return ledger

    def import_csv(self, text):
        imported, errors = 0, []
        reader = csv.DictReader(io.StringIO(text))
        for line_no, row in enumerate(reader, start=2):
            try:
                self.add(row["date"] or "", row["description"] or "", row["amount"] or "", row.get("category") or "uncategorized")
            except (ValueError, TypeError, KeyError) as exc:
                errors.append((line_no, str(exc)))
            else:
                imported += 1
        return imported, errors
