import pytest

from academy_loader import load

ex = load(__file__)


@pytest.fixture
def Product():
    class Product:
        name = ex.Typed(str)
        price = ex.Typed(float)
        qty = ex.Bounded(min=0, max=1000)
        size = ex.OneOf("S", "M", "L")

        def __init__(self, name, price, qty, size="M"):
            self.name, self.price, self.qty, self.size = name, price, qty, size

    return Product


def test_validators_accept_and_convert(Product):
    p = Product("shirt", 20, 3)
    assert (p.name, p.price, p.qty, p.size) == ("shirt", 20.0, 3, "M")
    assert isinstance(p.price, float)
    assert p.__dict__["name"] == "shirt", "store values in the instance __dict__ under the same name"


def test_validators_reject(Product):
    with pytest.raises(TypeError):
        Product(5, 1.0, 1)
    with pytest.raises(TypeError):
        Product("x", "cheap", 1)
    with pytest.raises(ValueError):
        Product("x", 1.0, -1)
    with pytest.raises(ValueError):
        Product("x", 1.0, 1001)
    with pytest.raises(ValueError):
        Product("x", 1.0, 1, size="XL")


def test_typed_rejects_bool():
    class C:
        n = ex.Typed(int)

    c = C()
    with pytest.raises(TypeError):
        c.n = True
    c.n = 3
    assert c.n == 3


def test_descriptor_on_class_and_unset(Product):
    assert isinstance(Product.qty, ex.Bounded)
    assert Product.qty.name == "qty"

    class Empty:
        v = ex.Typed(int)

    with pytest.raises(AttributeError):
        Empty().v


def test_descriptor_is_data_descriptor(Product):
    p = Product("x", 1.0, 1)
    p.__dict__["qty"] = -50  # sneaky direct write...
    with pytest.raises(ValueError):
        p.qty = -1  # ...but normal assignment still validates


def test_lazy_property():
    calls = []

    class Circle:
        def __init__(self, r):
            self.r = r

        @ex.lazy_property
        def area(self):
            """The area."""
            calls.append(self.r)
            return 3 * self.r**2

    c = Circle(2)
    assert c.area == 12 and c.area == 12
    assert calls == [2]
    assert "area" in c.__dict__
    del c.area
    assert c.area == 12 and calls == [2, 2]
    assert isinstance(Circle.area, ex.lazy_property)
    assert Circle.area.__doc__ == "The area."
    assert not hasattr(ex.lazy_property, "__set__"), "must be a NON-data descriptor"


def test_attrdict():
    d = ex.AttrDict({"db": {"host": "x", "port": 1}, "debug": False})
    assert d.db.host == "x"
    assert isinstance(d.db, ex.AttrDict)
    d.db.port = 2
    assert d["db"]["port"] == 2, "nested changes must persist"
    d.timeout = 30
    assert d["timeout"] == 30
    del d.timeout
    assert "timeout" not in d
    with pytest.raises(AttributeError):
        d.missing
    with pytest.raises(AttributeError):
        del d.missing
    assert not hasattr(d, "nope")
    assert sorted(d.keys()) == ["db", "debug"]
    assert isinstance(d, dict)


def test_recording_proxy():
    data = [3, 1, 2]
    p = ex.RecordingProxy(data)
    p.sort()
    p.append(5)
    assert data == [1, 2, 3, 5]
    assert p._accessed == ["sort", "append"]


def test_recording_proxy_set_and_delete():
    class Thing:
        pass

    t = Thing()
    p = ex.RecordingProxy(t)
    p.color = "red"
    assert t.color == "red"
    assert p.color == "red"
    del p.color
    assert not hasattr(t, "color")
    assert p._accessed == ["color"]


def test_frozen():
    @ex.frozen
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    p = Point(1, 2)
    assert (p.x, p.y) == (1, 2)
    with pytest.raises(AttributeError, match="Point is frozen"):
        p.x = 10
    with pytest.raises(AttributeError):
        del p.y
    with pytest.raises(AttributeError):
        p.z = 0
    assert Point(3, 4).x == 3


def test_frozen_subclass_init():
    @ex.frozen
    class Base:
        def __init__(self, a):
            self.a = a

    @ex.frozen
    class Child(Base):
        def __init__(self, a, b):
            super().__init__(a)
            self.b = b  # still inside construction

    c = Child(1, 2)
    assert (c.a, c.b) == (1, 2)
    with pytest.raises(AttributeError):
        c.a = 5
