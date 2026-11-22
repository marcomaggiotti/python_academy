"""Module 05 — Exceptions & Context Managers.

Run: python academy.py check 05
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any, Callable, Iterator


# --- Exception hierarchy -------------------------------------------------------

class InventoryError(Exception):
    """Base class for inventory errors. (Already done — leave as is.)"""


class UnknownItem(InventoryError):
    """Raised for unknown items.
    UnknownItem("apple") -> str(exc) == "unknown item: 'apple'", exc.item == "apple"
    """


class OutOfStock(InventoryError):
    """OutOfStock("apple", requested=5, available=2)
    -> str(exc) == "cannot take 5 'apple' (only 2 left)"
    Attributes: .item, .requested, .available
    """


class Inventory:
    """A simple stock counter that uses the exceptions above.

      inv = Inventory({"apple": 3})
      inv.take("apple", 2)   -> returns remaining (1)
      inv.take("pear")       -> UnknownItem
      inv.take("apple", 5)   -> OutOfStock (stock unchanged!)
      inv.take("apple", 0)   -> ValueError (amount must be positive)
      inv.stock              -> a COPY of the internal dict
    """

    def __init__(self, stock: dict[str, int]) -> None:
        raise NotImplementedError


# --- Chaining --------------------------------------------------------------------

class ConfigError(Exception):
    pass


def parse_config(text: str) -> dict[str, int]:
    """Parse lines of "key = integer". Ignore blank lines and lines starting with '#'.

    - A line without '=' -> ConfigError("line N: missing '='")  (N is 1-based)
    - A value that isn't an int -> ConfigError("line N: invalid integer ...")
      raised FROM the original ValueError (so exc.__cause__ is the ValueError).
    """
    raise NotImplementedError


def validate_users(users: list[dict]) -> None:
    """Check every user dict and report ALL problems at once.

    For each user (index i):
      - missing or empty "name"           -> ValueError(f"user {i}: name required")
      - "age" not an int                  -> TypeError(f"user {i}: age must be int")
      - "age" int but < 0                 -> ValueError(f"user {i}: age must be >= 0")
    If there were any problems, raise ExceptionGroup("invalid users", [...errors in order]).
    """
    raise NotImplementedError


# --- Context managers ---------------------------------------------------------------

class Timer:
    """Class-based context manager.

      with Timer(clock=fake_clock) as t:
          ...
      t.elapsed  -> seconds spent inside the block (also set if the block raises)

    Must not suppress exceptions. `clock` defaults to time.perf_counter.
    """

    def __init__(self, clock: Callable[[], float] = time.perf_counter) -> None:
        raise NotImplementedError


@contextmanager
def temporary_attr(obj: Any, name: str, value: Any) -> Iterator[Any]:
    """Temporarily set obj.<name> = value inside the block, yielding obj.
    Afterwards restore the old value — or delete the attribute if it didn't exist
    before. Restore even if the block raises.
    """
    raise NotImplementedError
    yield  # (keeps this a generator; remove once implemented)


@contextmanager
def collect_errors(log: list[BaseException], *types: type[BaseException]) -> Iterator[None]:
    """Like contextlib.suppress, but appends the suppressed exception to `log`.
    Only suppress the given exception `types` (default: Exception if none given);
    anything else propagates.
    """
    raise NotImplementedError
    yield


class Transaction:
    """Transactional edits on a dict.

      data = {"a": 1}
      with Transaction(data) as tx:   # tx is a working copy (a dict)
          tx["a"] = 2
          tx["b"] = 3
      data == {"a": 2, "b": 3}        # committed on success

      with Transaction(data) as tx:
          tx["a"] = 100
          raise RuntimeError          # propagates...
      data == {"a": 2, "b": 3}        # ...and nothing was changed (rollback)

    Commit must update the SAME dict object (not rebind), including deleting
    keys that were deleted from the working copy.
    """

    def __init__(self, data: dict) -> None:
        raise NotImplementedError
