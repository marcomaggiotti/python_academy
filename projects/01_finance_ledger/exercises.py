"""Project 01 — Personal Finance Ledger.

Read LESSON.md for the full specification.
Run: python academy.py check p1
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, asdict
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Iterator


def parse_amount(text: str) -> int:
    """Parse a money string into integer cents (see LESSON.md)."""
    raise NotImplementedError


@dataclass(frozen=True)
class Transaction:
    id: int
    date: date
    description: str
    cents: int
    category: str

    # TODO: is_expense and month properties


class Ledger:
    def __init__(self) -> None:
        raise NotImplementedError

    # TODO: add, remove, __len__, __iter__, balance, filter,
    #       totals_by_category, monthly_summary, to_json, from_json, import_csv
