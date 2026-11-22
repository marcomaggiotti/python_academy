import math
from typing import Generic

import pytest

from academy_loader import load

ex = load(__file__)


def test_first():
    assert ex.first([3, 4]) == 3
    assert ex.first([]) is None
    assert ex.first("", default="z") == "z"


def test_group_by():
    words = ["apple", "avocado", "banana", "blueberry", "cherry"]
    assert ex.group_by(words, key=lambda w: w[0]) == {
        "a": ["apple", "avocado"],
        "b": ["banana", "blueberry"],
        "c": ["cherry"],
    }
    assert ex.group_by(range(6), key=lambda n: n % 2 == 0) == {True: [0, 2, 4], False: [1, 3, 5]}


def test_stack():
    assert issubclass(ex.Stack, Generic)
    s = ex.Stack[int]()
    s.push(1)
    s.push(2)
    assert s.peek() == 2 and len(s) == 2
    assert s.pop() == 2 and len(s) == 1
    s.pop()
    with pytest.raises(IndexError, match="empty stack"):
        s.pop()
    with pytest.raises(IndexError):
        s.peek()


def test_stack_from_iterable_and_iter():
    s = ex.Stack.from_iterable([1, 2, 3])
    assert isinstance(s, ex.Stack)
    assert list(s) == [3, 2, 1]
    assert s.peek() == 3


def test_total_area_uses_protocol():
    class Sq:
        def area(self):
            return 4.0

    class Circ:
        def area(self):
            return math.pi

    class NotAShape:
        perimeter = 3

    assert isinstance(Sq(), ex.SupportsArea)
    assert not isinstance(NotAShape(), ex.SupportsArea)
    assert ex.total_area([Sq(), Circ(), NotAShape(), "hi"]) == pytest.approx(4 + math.pi)


def test_parse_user():
    raw = {"name": "Ada", "age": 36, "email": "ada@example.com", "extra": 1}
    assert ex.parse_user(raw) == {"name": "Ada", "age": 36, "email": "ada@example.com"}


@pytest.mark.parametrize(
    "raw, error",
    [
        ({"name": "A", "age": 1}, KeyError),
        ({"name": "A", "age": "1", "email": "a@b"}, TypeError),
        ({"name": "A", "age": True, "email": "a@b"}, TypeError),
        ({"name": 5, "age": 1, "email": "a@b"}, TypeError),
        ({"name": "A", "age": 1, "email": "nope"}, ValueError),
        ({"name": "A", "age": 1, "email": "a@@b"}, ValueError),
    ],
)
def test_parse_user_errors(raw, error):
    with pytest.raises(error):
        ex.parse_user(raw)


def test_order_status_transitions():
    S = ex.OrderStatus
    assert S.PENDING.can_transition_to(S.PAID)
    assert not S.PENDING.can_transition_to(S.SHIPPED)
    assert S.SHIPPED.can_transition_to(S.CANCELLED)
    assert not S.DELIVERED.can_transition_to(S.CANCELLED)
    assert not S.CANCELLED.can_transition_to(S.PENDING)
    assert S.DELIVERED.is_final and S.CANCELLED.is_final and not S.PAID.is_final


def test_order_status_parse():
    assert ex.OrderStatus.parse("paid") is ex.OrderStatus.PAID
    assert ex.OrderStatus.parse(" Shipped ") is ex.OrderStatus.SHIPPED
    with pytest.raises(ValueError):
        ex.OrderStatus.parse("lost")


def test_order_lifecycle():
    S = ex.OrderStatus
    o = ex.Order(1)
    o.advance(S.PAID)
    o.advance(S.SHIPPED)
    with pytest.raises(ValueError):
        o.advance(S.PAID)
    o.advance(S.DELIVERED)
    assert o.history == [S.PENDING, S.PAID, S.SHIPPED, S.DELIVERED]
    with pytest.raises(ValueError):
        o.advance(S.CANCELLED)


def test_result_type():
    assert ex.safe_sqrt(9) == ex.Ok(3.0)
    assert ex.safe_sqrt(-1) == ex.Err("negative input")
    assert ex.unwrap_all([ex.safe_sqrt(4), ex.safe_sqrt(16)]) == [2.0, 4.0]
    with pytest.raises(ValueError, match="negative input"):
        ex.unwrap_all([ex.safe_sqrt(1), ex.safe_sqrt(-5), ex.Err("later")])
