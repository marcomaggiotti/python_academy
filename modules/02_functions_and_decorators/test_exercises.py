import pytest

from academy_loader import load

ex = load(__file__)


def test_make_counter_independent():
    a, b = ex.make_counter(), ex.make_counter(10, 5)
    assert [a(), a(), a()] == [1, 2, 3]
    assert [b(), b()] == [15, 20]
    assert a() == 4


def test_make_averager():
    avg = ex.make_averager()
    assert avg(10) == 10.0
    assert avg(20) == 15.0
    assert avg(0) == 10.0


def test_make_multipliers_late_binding():
    assert [f(10) for f in ex.make_multipliers(4)] == [0, 10, 20, 30]


def test_compose():
    inc = lambda x: x + 1
    dbl = lambda x: x * 2
    assert ex.compose(inc, dbl)(5) == 11
    assert ex.compose(dbl, inc)(5) == 12
    assert ex.compose()(7) == 7


def test_count_calls():
    @ex.count_calls
    def hello(name):
        """Say hi."""
        return f"hi {name}"

    assert hello.calls == 0
    assert hello("a") == "hi a"
    hello("b")
    assert hello.calls == 2
    assert hello.__name__ == "hello"
    assert hello.__doc__ == "Say hi."


def test_retry_succeeds_eventually():
    attempts = []

    @ex.retry(3, exceptions=(ConnectionError,))
    def flaky():
        attempts.append(1)
        if len(attempts) < 3:
            raise ConnectionError
        return "ok"

    assert flaky() == "ok"
    assert len(attempts) == 3


def test_retry_gives_up():
    attempts = []

    @ex.retry(2, exceptions=(ConnectionError,))
    def always_fails():
        attempts.append(1)
        raise ConnectionError("down")

    with pytest.raises(ConnectionError):
        always_fails()
    assert len(attempts) == 2


def test_retry_other_exceptions_propagate_immediately():
    attempts = []

    @ex.retry(5, exceptions=(ConnectionError,))
    def bad():
        attempts.append(1)
        raise KeyError("nope")

    with pytest.raises(KeyError):
        bad()
    assert len(attempts) == 1


def test_memoize():
    calls = []

    @ex.memoize
    def add(a, b=0):
        calls.append((a, b))
        return a + b

    assert add(1, b=2) == 3
    assert add(1, b=2) == 3
    assert add(1, 2) == 3  # different call shape -> may be a separate entry
    assert calls.count((1, 2)) <= 2
    assert len(add.cache) >= 1
    add.cache_clear()
    assert len(add.cache) == 0
    add(1, b=2)
    assert calls.count((1, 2)) >= 2


def test_memoize_kwargs_order_irrelevant():
    calls = []

    @ex.memoize
    def f(**kw):
        calls.append(kw)
        return sorted(kw)

    f(a=1, b=2)
    f(b=2, a=1)
    assert len(calls) == 1


def test_timed_with_fake_clock():
    ticks = iter([100.0, 102.5, 200.0, 201.0])

    @ex.timed(clock=lambda: next(ticks))
    def work(x):
        if x < 0:
            raise ValueError
        return x * 2

    assert work(4) == 8
    assert work.last_duration == pytest.approx(2.5)
    with pytest.raises(ValueError):
        work(-1)
    assert work.last_duration == pytest.approx(1.0)
    assert work.__name__ == "work"


def test_validate_types():
    @ex.validate_types
    def greet(name: str, times: int = 1) -> str:
        return name * times

    assert greet("ab", 2) == "abab"
    assert greet(name="x") == "x"
    with pytest.raises(TypeError):
        greet("bob", times="2")
    with pytest.raises(TypeError):
        greet(5)


@pytest.mark.parametrize(
    "expr, expected",
    [("3 * 4", 12.0), ("10 / 4", 2.5), ("2 ** 10", 1024.0), ("7 - 10", -3.0), ("1.5 + 1", 2.5)],
)
def test_calculator(expr, expected):
    assert ex.calculator(expr) == expected


@pytest.mark.parametrize("expr", ["3 % 4", "3 *", "hello"])
def test_calculator_errors(expr):
    with pytest.raises(ValueError):
        ex.calculator(expr)


def test_pipeline():
    assert ex.pipeline([3, 1, 2], sorted, lambda xs: [x * 10 for x in xs]) == [10, 20, 30]
    assert ex.pipeline([1, 2]) == [1, 2]
