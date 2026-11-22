import gc

import pytest

from academy_loader import load

ex = load(__file__)


# --- EventBus --------------------------------------------------------------------

def test_event_bus_basic_and_wildcard():
    bus = ex.EventBus()
    log = []
    bus.subscribe("order.created", lambda t, p: log.append(("handler", t, p)))
    bus.subscribe("*", lambda t, p: log.append(("audit", t, p)))
    assert bus.publish("order.created", {"id": 1}) == 2
    assert bus.publish("user.deleted", 5) == 1
    assert log == [
        ("handler", "order.created", {"id": 1}),
        ("audit", "order.created", {"id": 1}),
        ("audit", "user.deleted", 5),
    ]


def test_event_bus_unsubscribe_and_duplicates():
    bus = ex.EventBus()
    calls = []

    def handler(t, p):
        calls.append(p)

    unsub = bus.subscribe("x", handler)
    bus.subscribe("x", handler)
    assert bus.subscriber_count("x") == 1
    bus.publish("x", 1)
    unsub()
    unsub()
    assert bus.publish("x", 2) == 0
    assert calls == [1]


def test_event_bus_weak_bound_methods():
    bus = ex.EventBus()
    received = []

    class Listener:
        def on_event(self, topic, payload):
            received.append(payload)

    listener = Listener()
    bus.subscribe("tick", listener.on_event)
    assert bus.publish("tick", 1) == 1
    del listener
    gc.collect()
    assert bus.publish("tick", 2) == 0
    assert bus.subscriber_count("tick") == 0
    assert received == [1]


def test_event_bus_two_instances_same_method():
    bus = ex.EventBus()
    seen = []

    class L:
        def __init__(self, n):
            self.n = n

        def handle(self, t, p):
            seen.append(self.n)

    a, b = L("a"), L("b")
    bus.subscribe("e", a.handle)
    bus.subscribe("e", b.handle)
    bus.publish("e")
    assert seen == ["a", "b"]


def test_event_bus_errors_collected():
    bus = ex.EventBus()
    ran = []
    bus.subscribe("e", lambda t, p: 1 / 0)
    bus.subscribe("e", lambda t, p: ran.append("second"))
    bus.subscribe("e", lambda t, p: {}["k"])
    with pytest.raises(ExceptionGroup) as info:
        bus.publish("e")
    assert ran == ["second"]
    assert [type(e) for e in info.value.exceptions] == [ZeroDivisionError, KeyError]


# --- TextEditor ----------------------------------------------------------------------

def test_editor_undo_redo():
    ed = ex.TextEditor()
    ed.insert(0, "Hello")
    ed.insert(5, " world")
    ed.delete(0, 6)
    assert ed.text == "world"
    assert ed.undo() and ed.text == "Hello world"
    assert ed.undo() and ed.text == "Hello"
    assert ed.redo() and ed.text == "Hello world"
    assert ed.can_undo and ed.can_redo
    ed.insert(0, ">> ")
    assert not ed.can_redo and ed.redo() is False
    assert ed.text == ">> Hello world"
    while ed.undo():
        pass
    assert ed.text == "" and not ed.can_undo


def test_editor_validation():
    ed = ex.TextEditor("abc")
    with pytest.raises(IndexError):
        ed.insert(4, "x")
    with pytest.raises(IndexError):
        ed.delete(2, 5)
    assert not ed.can_undo and ed.text == "abc"


def test_editor_batch():
    ed = ex.TextEditor("x")
    with ed.batch():
        ed.insert(1, "y")
        ed.insert(2, "z")
        with ed.batch():
            ed.delete(0, 1)
    assert ed.text == "yz"
    assert ed.undo() and ed.text == "x"
    assert not ed.can_undo
    assert ed.redo() and ed.text == "yz"


def test_editor_batch_rollback_on_error():
    ed = ex.TextEditor("abc")
    ed.insert(3, "d")
    with pytest.raises(ZeroDivisionError):
        with ed.batch():
            ed.insert(0, "!!!")
            ed.delete(0, 1)
            1 / 0
    assert ed.text == "abcd"
    assert ed.undo() and ed.text == "abc"


# --- Container ---------------------------------------------------------------------------

class Config:
    def __init__(self, debug: bool = False):
        self.debug = debug


class Repository:
    pass


class MemoryRepository(Repository):
    def __init__(self, config: Config):
        self.config = config


class Mailer:
    pass


class UserService:
    def __init__(self, repo: Repository, mailer: Mailer, retries: int = 3):
        self.repo, self.mailer, self.retries = repo, mailer, retries


def test_container_autowiring():
    c = ex.Container()
    c.register(Config, lambda: Config(debug=True), singleton=True)
    c.register(Repository, MemoryRepository)
    svc = c.resolve(UserService)
    assert isinstance(svc.repo, MemoryRepository)
    assert isinstance(svc.mailer, Mailer)  # unregistered class: auto-wired
    assert svc.retries == 3  # int can't be resolved, default kept
    assert svc.repo.config.debug is True
    assert c.resolve(Config) is c.resolve(Config)
    assert c.resolve(UserService) is not svc


def test_container_singleton_class():
    c = ex.Container()
    c.register(Mailer, singleton=True)
    assert c.resolve(Mailer) is c.resolve(Mailer)


def test_container_missing_dependency():
    class NeedsPort:
        def __init__(self, port: int):
            self.port = port

    c = ex.Container()
    with pytest.raises(ex.ResolutionError, match="port"):
        c.resolve(NeedsPort)
    assert issubclass(ex.ResolutionError, LookupError)


class A:
    def __init__(self, b: "B"):
        self.b = b


class B:
    def __init__(self, a: A):
        self.a = a


def test_container_cycle():
    with pytest.raises(ex.ResolutionError, match="cycle"):
        ex.Container().resolve(A)


def test_container_override():
    c = ex.Container()
    c.register(Repository, MemoryRepository)
    fake = Repository()
    with c.override(Repository, fake):
        assert c.resolve(UserService).repo is fake
    assert isinstance(c.resolve(UserService).repo, MemoryRepository)


# --- Middleware -----------------------------------------------------------------------------

def test_pipeline_order():
    trace = []

    def make(name):
        def mw(req, call_next):
            trace.append(f"{name}-in")
            resp = call_next({**req, "path": req["path"] + f"/{name}"})
            trace.append(f"{name}-out")
            resp["seen"].append(name)
            return resp

        return mw

    def handler(req):
        trace.append("handler")
        return {"path": req["path"], "seen": []}

    app = ex.build_pipeline(handler, [make("a"), make("b"), make("c")])
    resp = app({"path": ""})
    assert trace == ["a-in", "b-in", "c-in", "handler", "c-out", "b-out", "a-out"]
    assert resp == {"path": "/a/b/c", "seen": ["c", "b", "a"]}


def test_pipeline_short_circuit_and_empty():
    def auth(req, call_next):
        if not req.get("user"):
            return {"status": 401}
        return call_next(req)

    handler = lambda req: {"status": 200}
    app = ex.build_pipeline(handler, [auth])
    assert app({}) == {"status": 401}
    assert app({"user": "ada"}) == {"status": 200}
    assert ex.build_pipeline(handler, [])({}) == {"status": 200}
