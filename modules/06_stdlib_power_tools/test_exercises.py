import time

import pytest

from academy_loader import load

ex = load(__file__)


def test_top_words():
    text = "The cat and the hat. The cat's hat! And AND"
    assert ex.top_words(text, 3) == [("and", 3), ("the", 3), ("hat", 2)]
    assert ex.top_words("", 2) == []


def test_group_anagrams():
    words = ["listen", "google", "silent", "enlist", "tab", "bat"]
    assert ex.group_anagrams(words) == [["bat", "tab"], ["enlist", "listen", "silent"], ["google"]]


@pytest.mark.parametrize(
    "score, grade", [(100, "A"), (90, "A"), (89.9, "B"), (80, "B"), (75, "C"), (60, "D"), (59, "F"), (0, "F")]
)
def test_letter_grade(score, grade):
    assert ex.letter_grade(score) == grade


def test_run_length():
    assert ex.run_length_encode("aaabccdddd") == "a3b1c2d4"
    assert ex.run_length_encode("") == ""
    assert ex.run_length_decode("a3b1c2d4") == "aaabccdddd"
    assert ex.run_length_decode("x12") == "x" * 12
    s = "zzzzzzzzzzzzzyyx"
    assert ex.run_length_decode(ex.run_length_encode(s)) == s


def test_running_max_and_steps():
    assert ex.running_max([3, 1, 4, 1, 5]) == [3, 3, 4, 4, 5]
    assert ex.running_max([]) == []
    assert ex.increasing_steps([1, 2, 2, 3, 1, 5]) == 3
    assert ex.increasing_steps(iter([5])) == 0


def test_k_closest():
    pts = [(3, 3), (1, 1), (-2, 0), (5, -1), (0, 1)]
    assert ex.k_closest(pts, 3) == [(0, 1), (1, 1), (-2, 0)]


def test_priority_queue():
    pq = ex.PriorityQueue()
    assert not pq and len(pq) == 0
    pq.push({"task": "low"}, 5)
    pq.push({"task": "urgent-1"}, 1)
    pq.push({"task": "urgent-2"}, 1)
    pq.push({"task": "mid"}, 3)
    assert len(pq) == 4 and pq
    assert pq.peek() == {"task": "urgent-1"}
    assert [pq.pop()["task"] for _ in range(4)] == ["urgent-1", "urgent-2", "mid", "low"]
    with pytest.raises(IndexError):
        pq.pop()


def test_recent_items():
    r = ex.RecentItems(3)
    for f in "abcab":
        r.add(f)
    assert list(r) == ["b", "a", "c"]
    r.add("d")
    assert list(r) == ["d", "b", "a"]
    assert len(r) == 3


def test_layered_settings():
    cli, env, defaults = {"debug": True}, {"port": 9000, "debug": False}, {"port": 80, "host": "x"}
    s = ex.layered_settings(cli, env, defaults)
    assert s["debug"] is True and s["port"] == 9000 and s["host"] == "x"
    s["host"] = "override"
    assert s["host"] == "override"
    assert defaults["host"] == "x" and "host" not in cli and "host" not in env


def test_count_paths():
    assert ex.count_paths(1, 1) == 1
    assert ex.count_paths(2, 2) == 2
    assert ex.count_paths(3, 3) == 6
    start = time.perf_counter()
    assert ex.count_paths(18, 18) == 2333606220
    assert time.perf_counter() - start < 1


@pytest.mark.parametrize(
    "value, expected",
    [
        (5, "int: 5"),
        (2.5, "float: 2.50"),
        ("abc", "str of length 3"),
        (True, "bool: True"),
        ([1, "ab"], "list of 2 items: [int: 1, str of length 2]"),
        ([], "list of 0 items: []"),
        ({1: 2}, "object of type dict"),
        (None, "object of type NoneType"),
    ],
)
def test_describe(value, expected):
    assert ex.describe(value) == expected


def test_describe_is_singledispatch():
    assert hasattr(ex.describe, "register"), "use functools.singledispatch"
