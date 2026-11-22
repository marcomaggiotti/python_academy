import inspect
import itertools

import pytest

from academy_loader import load

ex = load(__file__)


def test_countdown_reiterable_without_yield():
    c = ex.Countdown(3)
    assert list(c) == [3, 2, 1]
    assert list(c) == [3, 2, 1]
    it = iter(c)
    assert iter(it) is it, "the iterator's __iter__ must return itself"
    assert next(it) == 3
    assert list(ex.Countdown(0)) == []
    assert not inspect.isgeneratorfunction(type(c).__iter__)


def test_fibonacci_and_take():
    assert inspect.isgeneratorfunction(ex.fibonacci)
    assert ex.take(10, ex.fibonacci()) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    assert ex.take(3, [1]) == [1]


def test_chunked():
    assert list(ex.chunked(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]]
    assert list(ex.chunked([], 3)) == []
    gen = (x for x in "abcd")
    assert list(ex.chunked(gen, 2)) == [["a", "b"], ["c", "d"]]


def test_chunked_is_lazy():
    first = next(ex.chunked(itertools.count(), 2))
    assert first == [0, 1]


def test_sliding_window():
    assert list(ex.sliding_window([1, 2, 3, 4], 2)) == [(1, 2), (2, 3), (3, 4)]
    assert list(ex.sliding_window([1, 2], 3)) == []
    assert next(ex.sliding_window(itertools.count(), 3)) == (0, 1, 2)


def test_flatten_deep():
    assert list(ex.flatten_deep([1, [2, (3, [4])], "ab"])) == [1, 2, 3, 4, "ab"]
    assert list(ex.flatten_deep([[[[]]], b"xy"])) == [b"xy"]


def test_unique():
    assert list(ex.unique([3, 1, 3, 2, 1])) == [3, 1, 2]
    assert list(ex.unique("AbBa", key=str.lower)) == ["A", "b"]
    assert ex.take(3, ex.unique(itertools.cycle([1, 2, 3]))) == [1, 2, 3]


def test_interleave():
    assert list(ex.interleave("ABC", "d", "ef")) == ["A", "d", "e", "B", "f", "C"]
    assert list(ex.interleave()) == []
    assert ex.take(4, ex.interleave(itertools.count(), "xy")) == [0, "x", 1, "y"]


LOG = """\
2026-01-05 INFO service started
2026-01-05 ERROR payment timeout after 30s

garbage
2026-01-06 error   disk full
2026-01-06 WARNING high memory
"""


def test_parse_log():
    records = list(ex.parse_log(LOG.splitlines()))
    assert len(records) == 4
    assert records[1] == {"date": "2026-01-05", "level": "ERROR", "message": "payment timeout after 30s"}
    assert records[2]["message"] == "disk full"


def test_pipeline_is_lazy():
    def lines():
        yield "2026-01-01 ERROR first"
        raise AssertionError("pipeline read more than needed")

    errors = ex.only_level(ex.parse_log(lines()), "error")
    assert next(errors)["message"] == "first"


def test_only_level():
    errors = list(ex.only_level(ex.parse_log(LOG.splitlines()), "Error"))
    assert [r["message"] for r in errors] == ["payment timeout after 30s", "disk full"]


def test_running_stats():
    s = ex.running_stats()
    assert next(s) == {"count": 0}
    assert s.send(4) == {"count": 1, "mean": 4.0, "min": 4, "max": 4}
    assert s.send(10) == {"count": 2, "mean": 7.0, "min": 4, "max": 10}
    out = s.send(-2)
    assert out["count"] == 3
    assert out["mean"] == pytest.approx(4.0)
    assert (out["min"], out["max"]) == (-2, 10)
