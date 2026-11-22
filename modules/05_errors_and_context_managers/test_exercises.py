import types

import pytest

from academy_loader import load

ex = load(__file__)


class Boom(Exception):
    """Test-only exception (NotImplementedError would match RuntimeError)."""


# --- Inventory & exception hierarchy -------------------------------------------

def test_exception_hierarchy():
    assert issubclass(ex.UnknownItem, ex.InventoryError)
    assert issubclass(ex.OutOfStock, ex.InventoryError)
    e = ex.OutOfStock("apple", requested=5, available=2)
    assert str(e) == "cannot take 5 'apple' (only 2 left)"
    assert (e.item, e.requested, e.available) == ("apple", 5, 2)
    u = ex.UnknownItem("pear")
    assert str(u) == "unknown item: 'pear'" and u.item == "pear"


def test_inventory_take():
    inv = ex.Inventory({"apple": 3})
    assert inv.take("apple", 2) == 1
    assert inv.take("apple") == 0
    with pytest.raises(ex.UnknownItem):
        inv.take("pear")


def test_inventory_out_of_stock_leaves_stock_unchanged():
    inv = ex.Inventory({"apple": 3})
    with pytest.raises(ex.OutOfStock) as info:
        inv.take("apple", 5)
    assert info.value.available == 3
    assert inv.stock == {"apple": 3}
    with pytest.raises(ex.InventoryError):
        inv.take("apple", 4)


def test_inventory_misc():
    inv = ex.Inventory({"apple": 3})
    with pytest.raises(ValueError):
        inv.take("apple", 0)
    s = inv.stock
    s["apple"] = 999
    assert inv.stock == {"apple": 3}, "stock must return a copy"


# --- parse_config --------------------------------------------------------------

def test_parse_config_ok():
    text = "# settings\nport = 8080\n\n workers=4 \n"
    assert ex.parse_config(text) == {"port": 8080, "workers": 4}


def test_parse_config_missing_equals():
    with pytest.raises(ex.ConfigError, match="line 2: missing '='"):
        ex.parse_config("a = 1\nbroken line\n")


def test_parse_config_chains_cause():
    with pytest.raises(ex.ConfigError, match="line 1: invalid integer") as info:
        ex.parse_config("port = eighty")
    assert isinstance(info.value.__cause__, ValueError)


# --- ExceptionGroup ------------------------------------------------------------

def test_validate_users_ok():
    assert ex.validate_users([{"name": "a", "age": 3}]) is None


def test_validate_users_groups_all_errors():
    users = [
        {"name": "ok", "age": 30},
        {"name": "", "age": 5},
        {"name": "x", "age": "old"},
        {"age": -1},
    ]
    with pytest.raises(ExceptionGroup) as info:
        ex.validate_users(users)
    messages = [str(e) for e in info.value.exceptions]
    assert messages == [
        "user 1: name required",
        "user 2: age must be int",
        "user 3: name required",
        "user 3: age must be >= 0",
    ]
    type_errors, rest = info.value.split(TypeError)
    assert len(type_errors.exceptions) == 1
    assert all(isinstance(e, ValueError) for e in rest.exceptions)


# --- Timer -----------------------------------------------------------------------

def test_timer():
    ticks = iter([10.0, 13.5])
    with ex.Timer(clock=lambda: next(ticks)) as t:
        pass
    assert t.elapsed == pytest.approx(3.5)


def test_timer_records_on_error_and_does_not_suppress():
    ticks = iter([0.0, 2.0])
    timer = ex.Timer(clock=lambda: next(ticks))
    with pytest.raises(ZeroDivisionError):
        with timer:
            1 / 0
    assert timer.elapsed == pytest.approx(2.0)


# --- temporary_attr ----------------------------------------------------------------

def test_temporary_attr_restores():
    obj = types.SimpleNamespace(debug=False)
    with ex.temporary_attr(obj, "debug", True) as o:
        assert o is obj and obj.debug is True
    assert obj.debug is False


def test_temporary_attr_deletes_new_attr_even_on_error():
    obj = types.SimpleNamespace()
    with pytest.raises(Boom):
        with ex.temporary_attr(obj, "flag", 1):
            assert obj.flag == 1
            raise Boom
    assert not hasattr(obj, "flag")


# --- collect_errors ------------------------------------------------------------------

def test_collect_errors():
    log = []
    with ex.collect_errors(log, KeyError, IndexError):
        {}["missing"]
    with ex.collect_errors(log, KeyError, IndexError):
        [][1]
    assert [type(e) for e in log] == [KeyError, IndexError]
    with pytest.raises(ZeroDivisionError):
        with ex.collect_errors(log, KeyError):
            1 / 0
    assert len(log) == 2


def test_collect_errors_default_exception():
    log = []
    with ex.collect_errors(log):
        int("x")
    assert isinstance(log[0], ValueError)


# --- Transaction ----------------------------------------------------------------------

def test_transaction_commit():
    data = {"a": 1, "gone": 0}
    original = data
    with ex.Transaction(data) as tx:
        tx["a"] = 2
        tx["b"] = 3
        del tx["gone"]
        assert data == {"a": 1, "gone": 0}, "changes must not leak before commit"
    assert data is original
    assert data == {"a": 2, "b": 3}


def test_transaction_rollback():
    data = {"a": 1, "nested": {"x": 1}}
    with pytest.raises(Boom):
        with ex.Transaction(data) as tx:
            tx["a"] = 100
            tx["nested"]["x"] = 999
            raise Boom
    assert data == {"a": 1, "nested": {"x": 1}}
