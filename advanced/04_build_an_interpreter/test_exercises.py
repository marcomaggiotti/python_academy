import math

import pytest

from academy_loader import load

ex = load(__file__)
Num, Var, UnaryOp, BinOp, Call, Assign = ex.Num, ex.Var, ex.UnaryOp, ex.BinOp, ex.Call, ex.Assign


# --- Tokenizer -------------------------------------------------------------------

def test_tokenize_kinds_and_values():
    toks = ex.tokenize("x = 2**-1.5")
    assert [t.kind for t in toks] == ["NAME", "EQUALS", "NUMBER", "OP", "OP", "NUMBER", "END"]
    assert [t.value for t in toks] == ["x", "=", 2.0, "**", "-", 1.5, ""]
    assert [t.pos for t in toks] == [0, 2, 4, 5, 7, 8, 11]


def test_tokenize_misc():
    toks = ex.tokenize("max(a_1, .5) % 3")
    assert [t.kind for t in toks] == ["NAME", "LPAREN", "NAME", "COMMA", "NUMBER", "RPAREN", "OP", "NUMBER", "END"]
    assert toks[4].value == 0.5
    assert ex.tokenize("") == [ex.Token("END", "", 0)]


@pytest.mark.parametrize("src, pos", [("1 + $", 4), ("2 & 3", 2), ("1.2.3", 0)])
def test_tokenize_errors(src, pos):
    with pytest.raises(ex.ParseError) as info:
        ex.tokenize(src)
    assert info.value.pos == pos
    assert isinstance(info.value, ex.CalcError)


# --- Parser ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "src, ast",
    [
        ("1 + 2 * 3", BinOp("+", Num(1.0), BinOp("*", Num(2.0), Num(3.0)))),
        ("1 - 2 - 3", BinOp("-", BinOp("-", Num(1.0), Num(2.0)), Num(3.0))),
        ("2 ** 3 ** 2", BinOp("**", Num(2.0), BinOp("**", Num(3.0), Num(2.0)))),
        ("-2 ** 2", UnaryOp("-", BinOp("**", Num(2.0), Num(2.0)))),
        ("2 ** -1", BinOp("**", Num(2.0), UnaryOp("-", Num(1.0)))),
        ("(1 + 2) * x", BinOp("*", BinOp("+", Num(1.0), Num(2.0)), Var("x"))),
        ("max(1, y, 3)", Call("max", (Num(1.0), Var("y"), Num(3.0)))),
        ("f()", Call("f", ())),
        ("a = -b", Assign("a", UnaryOp("-", Var("b")))),
        ("10 % 4 / 2", BinOp("/", BinOp("%", Num(10.0), Num(4.0)), Num(2.0))),
    ],
)
def test_parse(src, ast):
    assert ex.parse(src) == ast


@pytest.mark.parametrize(
    "src, pos",
    [("1 +", 3), ("1 2", 2), ("(1 + 2", 6), ("* 3", 0), ("max(1,)", 6), ("3 = x", 2)],
)
def test_parse_errors(src, pos):
    with pytest.raises(ex.ParseError) as info:
        ex.parse(src)
    assert info.value.pos == pos


# --- Unparse -----------------------------------------------------------------------

@pytest.mark.parametrize(
    "src, out",
    [
        ("1 + 2 * x", "(1 + (2 * x))"),
        ("-max(a, 2)", "-max(a, 2)"),
        ("y = 2 ** 3 ** 2", "y = (2 ** (3 ** 2))"),
        ("2.5 * (b - 1)", "(2.5 * (b - 1))"),
    ],
)
def test_unparse(src, out):
    assert ex.unparse(ex.parse(src)) == out


def test_unparse_round_trip():
    for src in ["1 - (2 - 3)", "-(2 ** 2)", "max(1, min(2, x)) / 4", "a = b * -c"]:
        ast = ex.parse(src)
        assert ex.parse(ex.unparse(ast)) == ast


# --- Interpreter --------------------------------------------------------------------

def test_interpreter_basic():
    it = ex.Interpreter()
    assert it.run("x = 4") == 4.0
    assert it.run("sqrt(x) * 2") == 4.0
    assert it.run("y = x ** 0.5 + -1") == 1.0
    assert it.run("_ * 10") == 10.0
    assert it.run("10 % 4") == 2.0
    assert it.run("-2 ** 2") == -4.0
    assert it.run("2 ** 3 ** 2") == 512.0
    assert {k: v for k, v in it.variables.items() if k != "_"} == {"x": 4.0, "y": 1.0}


def test_interpreter_builtins():
    it = ex.Interpreter()
    assert it.run("2 * pi") == pytest.approx(2 * math.pi)
    assert it.run("e") == pytest.approx(math.e)
    assert it.run("max(1, 7, 3) - min(4, 2)") == 5.0
    assert it.run("abs(-3) + round(2.6)") == 6.0
    assert "pi" not in it.variables


@pytest.mark.parametrize(
    "src",
    ["nope + 1", "1 / 0", "5 % 0", "sqrt(-1)", "sqrt(1, 2)", "unknown(3)", "pi = 3", "max()"],
)
def test_interpreter_errors(src):
    it = ex.Interpreter()
    with pytest.raises(ex.EvalError):
        it.run(src)


def test_failed_run_does_not_update_underscore():
    it = ex.Interpreter()
    it.run("5")
    with pytest.raises(ex.CalcError):
        it.run("1 / 0")
    assert it.run("_") == 5.0
