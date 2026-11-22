"""Reference solutions for Module 01. Try the exercises first!"""

from __future__ import annotations


def flatten(matrix):
    return [x for row in matrix for x in row]


def invert_dict(d):
    out: dict[int, list[str]] = {}
    for key, value in d.items():
        out.setdefault(value, []).append(key)
    return {v: sorted(keys) for v, keys in out.items()}


def transpose(matrix):
    return [list(col) for col in zip(*matrix)]


def leaderboard(scores, top=3):
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[:top]


def head_tail(items):
    if len(items) < 2:
        raise ValueError("need at least 2 items")
    first, *middle, last = items
    return first, middle, last


def merge_configs(*configs):
    result: dict = {}
    for cfg in configs:
        for key, value in cfg.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = merge_configs(result[key], value)
            elif isinstance(value, dict):
                result[key] = merge_configs(value)  # copy
            else:
                result[key] = value
    return result


def _to_int(token: str) -> int | None:
    try:
        return int(token.strip())
    except ValueError:
        return None


def parse_valid_ints(tokens):
    return [n for t in tokens if (n := _to_int(t)) is not None]


DIRECTIONS = {"north", "south", "east", "west"}


def run_command(command):
    match command.lower().split():
        case ["go", direction] if direction in DIRECTIONS:
            return f"You go {direction}."
        case ["go", *_]:
            return "You can't go that way."
        case ["take"]:
            return "Take what?"
        case ["take", *items]:
            return f"You take {', '.join(items)}."
        case ["look"]:
            return "You see nothing special."
        case ["quit" | "exit"]:
            return "Bye!"
        case _:
            return "I don't understand."
