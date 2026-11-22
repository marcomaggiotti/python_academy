import pytest

from academy_loader import load

ex = load(__file__)


@pytest.fixture(autouse=True)
def clean_registry():
    ex.Exporter.registry.clear()
    yield
    ex.Exporter.registry.clear()


def test_plugin_registry():
    class JSONExporter(ex.Exporter, format="json"):
        def export(self, data):
            return "json"

    class Xml(ex.Exporter):
        def export(self, data):
            return "xml"

    assert ex.Exporter.registry == {"json": JSONExporter, "xml": Xml}
    assert ex.Exporter.formats() == ["json", "xml"]
    assert isinstance(ex.Exporter.create("json"), JSONExporter)
    with pytest.raises(ValueError):
        ex.Exporter.create("yaml")


def test_plugin_registry_rules():
    class First(ex.Exporter, format="csv"):
        def export(self, data):
            return ""

    with pytest.raises(TypeError):
        class Second(ex.Exporter, format="csv"):
            def export(self, data):
                return ""

    with pytest.raises(TypeError):
        class NoExport(ex.Exporter):
            pass

    class BaseBinary(ex.Exporter, abstract=True):
        pass

    class Protobuf(BaseBinary):
        def export(self, data):
            return "pb"

    assert ex.Exporter.formats() == ["csv", "protobuf"]


def test_singleton():
    class Config(metaclass=ex.SingletonMeta):
        inits = 0

        def __init__(self, value=0):
            Config.inits += 1
            self.value = value

    a = Config(1)
    b = Config(2)
    assert a is b and a.value == 1 and Config.inits == 1

    class SubConfig(Config):
        pass

    assert SubConfig() is not a
    assert SubConfig() is SubConfig()
    Config._reset()
    assert Config(5) is not a and Config().value == 5


def test_make_record():
    Point = ex.make_record("Point", ["x", "y"], defaults={"y": 0})
    assert isinstance(Point, type) and Point.__name__ == "Point"
    p = Point(1)
    assert (p.x, p.y) == (1, 0)
    assert repr(p) == "Point(x=1, y=0)"
    assert Point(1, 0) == p and Point(x=1, y=0) == p and Point(1, 2) != p
    assert Point._fields == ("x", "y")
    assert not hasattr(p, "__dict__"), "use __slots__"


@pytest.mark.parametrize("call", [lambda P: P(1, 2, 3), lambda P: P(), lambda P: P(1, z=2), lambda P: P(1, x=2)])
def test_make_record_bad_args(call):
    Point = ex.make_record("Point", ["x", "y"], defaults={"y": 0})
    with pytest.raises(TypeError):
        call(Point)


def test_make_record_different_classes_not_equal():
    A = ex.make_record("A", ["v"])
    B = ex.make_record("B", ["v"])
    assert A(1) != B(1)


def test_component_handlers():
    class Button(ex.Component):
        @ex.on("click")
        def press(self, x):
            return f"pressed {x}"

        @ex.on("click")
        @ex.on("hover")
        def glow(self, x):
            return f"glow {x}"

    b = Button()
    assert Button.handlers == {"click": ["press", "glow"], "hover": ["glow"]}
    assert b.dispatch("click", 1) == ["pressed 1", "glow 1"]
    assert b.dispatch("hover", 2) == ["glow 2"]
    assert b.dispatch("unknown") == []
    assert b.press(3) == "pressed 3"


def test_component_inheritance_and_override():
    class Base(ex.Component):
        @ex.on("save")
        def validate(self):
            return "base-validate"

    class Child(Base):
        def validate(self):  # override WITHOUT re-decorating
            return "child-validate"

        @ex.on("save")
        def write(self):
            return "write"

    assert Child.handlers == {"save": ["validate", "write"]}
    assert Child().dispatch("save") == ["child-validate", "write"]
    assert Base.handlers == {"save": ["validate"]}


def test_autorepr():
    @ex.autorepr
    class User:
        def __init__(self, name, age=0):
            self.name = name
            self.age = age

    u = User("ada", 36)
    assert repr(u) == "User(name='ada', age=36)"
    assert u == User("ada", 36) and u != User("ada", 37)
    assert u != ("ada", 36)


def test_autorepr_respects_existing():
    @ex.autorepr
    class Custom:
        def __init__(self, a):
            self.a = a

        def __repr__(self):
            return "custom!"

    assert repr(Custom(1)) == "custom!"
    assert Custom(1) == Custom(1)
