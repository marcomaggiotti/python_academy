import dataclasses
import inspect
from datetime import date

import pytest

from academy_loader import load

ex = load(__file__)


@pytest.mark.parametrize(
    "text, cents",
    [("12.50", 1250), ("-3", -300), ("1,234.56", 123456), ("0.005", 1), ("-0.005", -1), (" 7.1 ", 710)],
)
def test_parse_amount(text, cents):
    assert ex.parse_amount(text) == cents


@pytest.mark.parametrize("text", ["", "abc", "1.2.3", "nan"])
def test_parse_amount_invalid(text):
    with pytest.raises(ValueError):
        ex.parse_amount(text)


def test_transaction_properties():
    t = ex.Transaction(1, date(2026, 3, 9), "Coffee", -350, "food")
    assert t.is_expense and t.month == "2026-03"
    with pytest.raises(dataclasses.FrozenInstanceError):
        t.cents = 0


@pytest.fixture
def ledger():
    led = ex.Ledger()
    led.add("2026-01-31", "Salary", "3000", "Income")
    led.add(date(2026, 1, 5), "Groceries", "-82.40", "food")
    led.add("2026-02-02", "Rent", -120000, " Housing ")
    led.add("2026-02-14", "Dinner", "-45.5", "food")
    led.add("2026-01-05", "Coffee", "-3.50")
    return led


def test_add_returns_transactions_with_increasing_ids(ledger):
    tx = ledger.add("2026-03-01", "Book", "-15", "fun")
    assert tx.id == 6 and tx.cents == -1500 and tx.category == "fun"
    assert len(ledger) == 6


def test_add_normalises_and_validates(ledger):
    assert [t.category for t in ledger if t.description == "Rent"] == ["housing"]
    assert [t.category for t in ledger if t.description == "Coffee"] == ["uncategorized"]
    with pytest.raises(ValueError):
        ledger.add("2026-01-01", "   ", "1")
    with pytest.raises(ValueError):
        ledger.add("not-a-date", "x", "1")


def test_iteration_sorted_by_date_then_id(ledger):
    assert [t.description for t in ledger] == ["Groceries", "Coffee", "Salary", "Rent", "Dinner"]


def test_remove(ledger):
    ledger.remove(2)
    assert len(ledger) == 4
    with pytest.raises(KeyError):
        ledger.remove(2)


def test_balance(ledger):
    assert ledger.balance() == 300000 - 8240 - 120000 - 4550 - 350


def test_filter_is_generator(ledger):
    assert inspect.isgenerator(ledger.filter())
    jan = list(ledger.filter(start=date(2026, 1, 1), end=date(2026, 1, 31)))
    assert [t.description for t in jan] == ["Groceries", "Coffee", "Salary"]
    food = list(ledger.filter(category="FOOD"))
    assert [t.description for t in food] == ["Groceries", "Dinner"]
    assert [t.description for t in ledger.filter(start=date(2026, 2, 3), category="food")] == ["Dinner"]


def test_totals_by_category(ledger):
    totals = ledger.totals_by_category()
    assert totals == {"housing": -120000, "food": -12790, "uncategorized": -350, "income": 300000}
    assert list(totals) == ["housing", "food", "uncategorized", "income"]
    assert "income" not in ledger.totals_by_category(expenses_only=True)


def test_monthly_summary(ledger):
    assert ledger.monthly_summary() == {
        "2026-01": {"income": 300000, "expenses": -8590, "net": 291410},
        "2026-02": {"income": 0, "expenses": -124550, "net": -124550},
    }


def test_json_round_trip(ledger):
    ledger.remove(1)
    text = ledger.to_json()
    copy = ex.Ledger.from_json(text)
    assert list(copy) == list(ledger)
    assert copy.add("2026-05-05", "New", "1").id == 6


def test_import_csv():
    text = (
        "date,description,amount,category\n"
        "2026-04-01,Gym,-30,health\n"
        "2026-04-02,,-5,food\n"
        "2026-04-03,Refund,abc,misc\n"
        "bad-date,Thing,1,misc\n"
        "2026-04-04,Bonus,\"1,000.00\",income\n"
    )
    led = ex.Ledger()
    imported, errors = led.import_csv(text)
    assert imported == 2
    assert [line for line, _ in errors] == [3, 4, 5]
    assert all(isinstance(msg, str) and msg for _, msg in errors)
    assert led.balance() == -3000 + 100000
