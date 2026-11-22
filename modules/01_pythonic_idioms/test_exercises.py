import copy

import pytest

from academy_loader import load

ex = load(__file__)


def test_flatten():
    assert ex.flatten([[1, 2], [3], []]) == [1, 2, 3]
    assert ex.flatten([]) == []


def test_invert_dict():
    assert ex.invert_dict({"a": 1, "b": 2, "c": 1}) == {1: ["a", "c"], 2: ["b"]}
    assert ex.invert_dict({"z": 0, "y": 0}) == {0: ["y", "z"]}
    assert ex.invert_dict({}) == {}


def test_transpose():
    assert ex.transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    assert ex.transpose([[1]]) == [[1]]


def test_leaderboard():
    scores = {"bo": 5, "al": 7, "cy": 7, "di": 1}
    assert ex.leaderboard(scores, top=3) == [("al", 7), ("cy", 7), ("bo", 5)]
    assert ex.leaderboard(scores, top=10) == [("al", 7), ("cy", 7), ("bo", 5), ("di", 1)]
    assert ex.leaderboard(scores) == ex.leaderboard(scores, top=3)


def test_head_tail():
    assert ex.head_tail([1, 2, 3, 4]) == (1, [2, 3], 4)
    assert ex.head_tail(["a", "b"]) == ("a", [], "b")
    with pytest.raises(ValueError):
        ex.head_tail([1])


def test_merge_configs_recursive_and_pure():
    a = {"a": 1, "db": {"host": "x", "port": 1}}
    b = {"db": {"port": 2}, "debug": True}
    a_copy, b_copy = copy.deepcopy(a), copy.deepcopy(b)
    merged = ex.merge_configs(a, b)
    assert merged == {"a": 1, "db": {"host": "x", "port": 2}, "debug": True}
    assert a == a_copy and b == b_copy, "inputs must not be mutated"
    merged["db"]["host"] = "changed"
    assert a["db"]["host"] == "x", "result must not share nested dicts with inputs"


def test_merge_configs_many():
    assert ex.merge_configs({"x": 1}, {"x": 2}, {"x": 3}) == {"x": 3}
    assert ex.merge_configs() == {}


def test_parse_valid_ints():
    assert ex.parse_valid_ints([" 4", "x", "-2", "3.5", ""]) == [4, -2]
    assert ex.parse_valid_ints(["0"]) == [0]


@pytest.mark.parametrize(
    "cmd, expected",
    [
        ("go north", "You go north."),
        ("  GO   West ", "You go west."),
        ("go up", "You can't go that way."),
        ("take lamp", "You take lamp."),
        ("take lamp key", "You take lamp, key."),
        ("take", "Take what?"),
        ("look", "You see nothing special."),
        ("quit", "Bye!"),
        ("exit", "Bye!"),
        ("dance", "I don't understand."),
        ("", "I don't understand."),
    ],
)
def test_run_command(cmd, expected):
    assert ex.run_command(cmd) == expected
