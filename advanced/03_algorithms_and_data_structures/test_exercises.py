import itertools
import math
import random
import statistics
import string
import time

import pytest

from academy_loader import load

ex = load(__file__)


# --- LRU ---------------------------------------------------------------------------

def test_lru_basic():
    c = ex.LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1
    c.put("c", 3)
    assert c.get("b") is None and c.get("b", "x") == "x"
    assert c.keys() == ["c", "a"]
    assert c.evictions == 1 and len(c) == 2


def test_lru_update_and_contains_does_not_touch():
    c = ex.LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert "a" in c  # must NOT make "a" recent
    c.put("c", 3)
    assert "a" not in c and c.keys() == ["c", "b"]
    c.put("b", 20)
    assert c.keys() == ["b", "c"] and c.get("b") == 20


def test_lru_validation():
    with pytest.raises(ValueError):
        ex.LRUCache(0)


def test_lru_is_constant_time():
    c = ex.LRUCache(50_000)
    start = time.perf_counter()
    for i in range(150_000):
        c.put(i, i)
        c.get(i - 100)
    assert time.perf_counter() - start < 2.0
    assert len(c) == 50_000 and c.evictions == 100_000


def test_lru_matches_reference_model():
    rng = random.Random(1)
    c = ex.LRUCache(5)
    model = []  # most recent first
    store = {}
    for _ in range(2000):
        k = rng.randrange(12)
        if rng.random() < 0.5:
            c.put(k, k * 2)
            store[k] = k * 2
            if k in model:
                model.remove(k)
            model.insert(0, k)
            if len(model) > 5:
                store.pop(model.pop())
        else:
            expected = store.get(k) if k in model else None
            assert c.get(k) == expected
            if k in model:
                model.remove(k)
                model.insert(0, k)
        assert c.keys() == model


# --- Trie --------------------------------------------------------------------------

def test_trie():
    t = ex.Trie(["car", "cart", "cat", "dog"])
    t.insert("care")
    t.insert("car")  # duplicate
    assert len(t) == 5
    assert "cat" in t and "ca" not in t and "cartoon" not in t
    assert t.starts_with("car") == ["car", "care", "cart"]
    assert t.starts_with("") == ["car", "care", "cart", "cat", "dog"]
    assert t.starts_with("x") == []


def test_trie_remove_and_prune():
    t = ex.Trie(["car", "cart"])
    nodes_before = t.node_count()
    assert nodes_before == 4
    assert t.remove("car") is True
    assert "car" not in t and "cart" in t and t.node_count() == 4
    assert t.remove("car") is False
    assert t.remove("cart") is True
    assert t.node_count() == 0 and len(t) == 0
    t2 = ex.Trie(["ab", "abc", "abd"])
    t2.remove("abc")
    assert t2.node_count() == 3 and t2.starts_with("a") == ["ab", "abd"]


# --- Intervals -------------------------------------------------------------------------

def test_merge_intervals():
    assert ex.merge_intervals([(5, 7), (1, 3), (2, 4), (7, 8), (10, 11)]) == [(1, 4), (5, 8), (10, 11)]
    assert ex.merge_intervals([]) == []
    assert ex.merge_intervals([(1, 10), (2, 3)]) == [(1, 10)]


def test_min_meeting_rooms():
    assert ex.min_meeting_rooms([(0, 30), (5, 10), (15, 20)]) == 2
    assert ex.min_meeting_rooms([(1, 5), (5, 10)]) == 1
    assert ex.min_meeting_rooms([(1, 4), (2, 5), (3, 6), (7, 8)]) == 3
    assert ex.min_meeting_rooms([]) == 0


# --- Graphs ----------------------------------------------------------------------------

def test_topological_sort():
    assert ex.topological_sort({"app": ["lib", "utils"], "lib": ["utils"]}) == ["utils", "lib", "app"]
    deps = {"d": ["b", "c"], "b": ["a"], "c": ["a"], "e": []}
    assert ex.topological_sort(deps) == ["a", "b", "c", "d", "e"]
    assert ex.topological_sort({}) == []


def test_topological_sort_cycle():
    with pytest.raises(ex.CycleError) as info:
        ex.topological_sort({"a": ["b"], "b": ["c"], "c": ["a"], "x": [], "y": ["a"]})
    assert isinstance(info.value, ValueError)
    assert {"a", "b", "c"} <= info.value.cycle_nodes
    assert "x" not in info.value.cycle_nodes


GRAPH = {
    "A": {"B": 4, "C": 1},
    "C": {"B": 2, "D": 7},
    "B": {"D": 1},
    "D": {"E": 3},
    "X": {"A": 1},
}


def test_shortest_path():
    assert ex.shortest_path(GRAPH, "A", "E") == (7, ["A", "C", "B", "D", "E"])
    assert ex.shortest_path(GRAPH, "A", "A") == (0, ["A"])
    assert ex.shortest_path(GRAPH, "A", "X") == (math.inf, [])
    assert ex.shortest_path(GRAPH, "E", "A") == (math.inf, [])


def test_word_ladder():
    words = ["hot", "dot", "dog", "lot", "log", "cog"]
    assert ex.word_ladder("hit", "cog", words) == 5
    assert ex.word_ladder("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0
    assert ex.word_ladder("abc", "abc", ["abc"]) == 1


def test_word_ladder_performance():
    rng = random.Random(42)
    letters = "abcdefghij"
    words = {"".join(rng.choice(letters) for _ in range(4)) for _ in range(6000)}
    words |= {"aaaa", "aaab", "aabb", "abbb", "bbbb"}
    start = time.perf_counter()
    result = ex.word_ladder("aaaa", "bbbb", words)
    assert time.perf_counter() - start < 2.0
    assert 2 <= result <= 5


# --- Running median ------------------------------------------------------------------------

def test_running_median():
    rm = ex.RunningMedian()
    with pytest.raises(ValueError):
        rm.median()
    seen = []
    rng = random.Random(3)
    for _ in range(500):
        x = rng.randint(-100, 100)
        rm.add(x)
        seen.append(x)
        assert rm.median() == statistics.median(seen)
