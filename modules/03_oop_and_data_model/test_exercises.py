import dataclasses
import math

import pytest

from academy_loader import load

ex = load(__file__)


# --- Vector -----------------------------------------------------------------

def test_vector_basics():
    v = ex.Vector(3, 4)
    assert (v.x, v.y) == (3, 4)
    assert repr(v) == "Vector(3, 4)"
    assert abs(v) == 5.0
    x, y = v
    assert (x, y) == (3, 4)


def test_vector_immutable():
    v = ex.Vector(1, 2)
    with pytest.raises(AttributeError):
        v.x = 10


def test_vector_equality_and_hash():
    assert ex.Vector(1, 2) == ex.Vector(1, 2)
    assert ex.Vector(1, 2) != ex.Vector(2, 1)
    assert len({ex.Vector(1, 2), ex.Vector(1, 2), ex.Vector(0, 0)}) == 2
    assert ex.Vector(1, 2) != (1, 2)


def test_vector_arithmetic():
    v, w = ex.Vector(1, 2), ex.Vector(3, 5)
    assert v + w == ex.Vector(4, 7)
    assert w - v == ex.Vector(2, 3)
    assert v * 3 == ex.Vector(3, 6)
    assert 3 * v == ex.Vector(3, 6)
    assert v.dot(w) == 13
    with pytest.raises(TypeError):
        v + 1


def test_vector_bool():
    assert not ex.Vector(0, 0)
    assert ex.Vector(0, 1)


# --- Temperature ------------------------------------------------------------

def test_temperature_conversion():
    t = ex.Temperature(100)
    assert t.celsius == 100
    assert t.fahrenheit == pytest.approx(212)
    t.fahrenheit = 32
    assert t.celsius == pytest.approx(0)
    assert ex.Temperature.from_fahrenheit(212).celsius == pytest.approx(100)


def test_temperature_validation():
    with pytest.raises(ValueError):
        ex.Temperature(-300)
    t = ex.Temperature(0)
    with pytest.raises(ValueError):
        t.celsius = -274


def test_temperature_ordering():
    cold, warm = ex.Temperature(5), ex.Temperature(25)
    assert cold < warm and warm > cold
    assert cold <= ex.Temperature(5) and warm >= cold
    assert ex.Temperature(5) == cold
    assert sorted([warm, cold]) == [cold, warm]


# --- Money --------------------------------------------------------------------

def test_money_basics():
    m = ex.Money(1050, "EUR")
    assert str(m) == "10.50 EUR"
    assert str(ex.Money(5)) == "0.05 EUR"
    assert ex.Money.parse("10.50 USD") == ex.Money(1050, "USD")
    assert ex.Money.parse("3 GBP") == ex.Money(300, "GBP")


def test_money_frozen_and_hashable():
    m = ex.Money(100)
    with pytest.raises(dataclasses.FrozenInstanceError):
        m.cents = 5
    assert len({ex.Money(1), ex.Money(1)}) == 1


@pytest.mark.parametrize("code", ["eur", "EURO", "E1R", ""])
def test_money_currency_validation(code):
    with pytest.raises(ValueError):
        ex.Money(1, code)


def test_money_arithmetic():
    assert ex.Money(100) + ex.Money(250) == ex.Money(350)
    assert ex.Money(150, "USD") * 3 == ex.Money(450, "USD")
    with pytest.raises(ValueError):
        ex.Money(1, "EUR") + ex.Money(1, "USD")


def test_money_split():
    parts = ex.Money(100).split(3)
    assert [p.cents for p in parts] == [34, 33, 33]
    assert sum(p.cents for p in parts) == 100
    assert all(p.currency == "EUR" for p in parts)
    assert [p.cents for p in ex.Money(10, "USD").split(4)] == [3, 3, 2, 2]


# --- Shapes -----------------------------------------------------------------

def test_shape_is_abstract():
    with pytest.raises(TypeError):
        ex.Shape()


def test_shapes():
    c = ex.Circle(1)
    assert c.area() == pytest.approx(math.pi)
    assert c.describe() == "Circle: area=3.14, perimeter=6.28"
    r = ex.Rectangle(2, 3)
    assert (r.area(), r.perimeter()) == (6, 10)
    s = ex.Square(4)
    assert isinstance(s, ex.Rectangle) and isinstance(s, ex.Shape)
    assert s.describe() == "Square: area=16.00, perimeter=16.00"


@pytest.mark.parametrize("make", [lambda: ex.Circle(0), lambda: ex.Rectangle(1, -1), lambda: ex.Square(-2)])
def test_shape_validation(make):
    with pytest.raises(ValueError):
        make()


# --- Playlist -----------------------------------------------------------------

def test_playlist_sequence_protocol():
    p = ex.Playlist("road trip", ["a", "b", "c", "d"])
    assert len(p) == 4
    assert p[0] == "a" and p[-1] == "d"
    assert "b" in p and "z" not in p
    assert list(p) == ["a", "b", "c", "d"]
    assert list(reversed(p)) == ["d", "c", "b", "a"]


def test_playlist_slicing_returns_playlist():
    p = ex.Playlist("mix", ["a", "b", "c", "d"])
    sub = p[1:3]
    assert isinstance(sub, ex.Playlist)
    assert sub.name == "mix"
    assert list(sub) == ["b", "c"]


def test_playlist_add_concat_repr():
    p = ex.Playlist("x", ["a"])
    assert repr(p) == "Playlist('x', 1 song)"
    p.add("b")
    p.add("a")
    assert list(p) == ["a", "b"]
    q = ex.Playlist("y", ["b", "c"])
    both = p + q
    assert both.name == "x + y"
    assert list(both) == ["a", "b", "c"]
    assert repr(both) == "Playlist('x + y', 3 songs)"
    assert list(ex.Playlist("empty")) == []
