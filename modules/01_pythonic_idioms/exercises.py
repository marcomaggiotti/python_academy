"""Module 01 — Pythonic Idioms & Comprehensions.

Implement each function. Aim for idiomatic one-to-few-liners where it stays readable.
Run: python academy.py check 01
"""

from __future__ import annotations


def flatten(matrix: list[list[int]]) -> list[int]:
    """Flatten a list of lists by one level using a single comprehension.

    >>> flatten([[1, 2], [3], []])
    [1, 2, 3]
    """
    raise NotImplementedError


def invert_dict(d: dict[str, int]) -> dict[int, list[str]]:
    """Invert a mapping. Values become keys; keys collected into sorted lists.

    >>> invert_dict({"a": 1, "b": 2, "c": 1})
    {1: ['a', 'c'], 2: ['b']}
    """
    raise NotImplementedError


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    """Transpose a rectangular matrix (hint: zip + unpacking).

    >>> transpose([[1, 2, 3], [4, 5, 6]])
    [[1, 4], [2, 5], [3, 6]]
    """
    raise NotImplementedError


def leaderboard(scores: dict[str, int], top: int = 3) -> list[tuple[str, int]]:
    """Return the `top` (name, score) pairs: highest score first, ties broken
    alphabetically by name.

    >>> leaderboard({"bo": 5, "al": 7, "cy": 7, "di": 1}, top=3)
    [('al', 7), ('cy', 7), ('bo', 5)]
    """
    raise NotImplementedError


def head_tail(items: list) -> tuple:
    """Return (first, middle_list, last) using star-unpacking.
    Raise ValueError if fewer than 2 items.

    >>> head_tail([1, 2, 3, 4])
    (1, [2, 3], 4)
    """
    raise NotImplementedError


def merge_configs(*configs: dict) -> dict:
    """Merge any number of dicts; later ones win. Do NOT mutate the inputs.
    Nested dicts are merged recursively.

    >>> merge_configs({"a": 1, "db": {"host": "x", "port": 1}}, {"db": {"port": 2}})
    {'a': 1, 'db': {'host': 'x', 'port': 2}}
    """
    raise NotImplementedError


def parse_valid_ints(tokens: list[str]) -> list[int]:
    """Convert tokens to ints, skipping ones that are not valid integers.
    Strip whitespace first. Try to use the walrus operator with a helper.

    >>> parse_valid_ints([" 4", "x", "-2", "3.5", ""])
    [4, -2]
    """
    raise NotImplementedError


def run_command(command: str) -> str:
    """Interpret a tiny text-adventure command with `match`/`case`:

    - "go <direction>"       -> "You go <direction>."
      (direction must be one of north/south/east/west, otherwise "You can't go that way.")
    - "take <a> [<b> ...]"   -> "You take a, b."  (items joined by ", ")
    - "take"                 -> "Take what?"
    - "look"                 -> "You see nothing special."
    - "quit" or "exit"       -> "Bye!"
    - anything else          -> "I don't understand."

    Commands are case-insensitive and extra whitespace is ignored.
    """
    raise NotImplementedError
