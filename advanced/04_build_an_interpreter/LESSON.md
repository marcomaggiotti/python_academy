# Advanced 04 — Build an Interpreter

You'll build a small calculator language with variables and functions. It's
the classic three-stage pipeline:

```
"x = 2 * (3 + y)"  ──tokenize──▶  [NAME x] [= ] [NUMBER 2] [* ] [( ] ...
                    ──parse─────▶  Assign("x", BinOp("*", Num(2), BinOp("+", Num(3), Var("y"))))
                    ──evaluate──▶  value (and the environment is updated)
```

## 1. Tokenizer

Walk the string with an index. Emit `Token(kind, value, pos)`. Skip whitespace.
Numbers can be `12`, `3.5`, `.5`. Names are `[A-Za-z_][A-Za-z0-9_]*`.
Two-character operators (`**`) must be matched before one-character ones (`*`).
Finish with an `END` token so the parser never runs off the end.

(A regex with named alternatives plus `re.finditer`/`match` at the current
position is an elegant alternative.)

## 2. Recursive-descent parsing

Each grammar rule becomes one method. **Precedence comes from nesting**: lower
precedence rules call higher precedence ones.

```
statement := NAME "=" expr | expr
expr      := term (("+" | "-") term)*                 # left-associative: loop
term      := unary (("*" | "/" | "%") unary)*
unary     := "-" unary | "+" unary | power
power     := primary ("**" unary)?                    # right-associative: recurse
primary   := NUMBER | NAME | NAME "(" args? ")" | "(" expr ")"
args      := expr ("," expr)*
```

Notice that `unary` sits *above* `power`, so `-2 ** 2 == -4` (like Python), and the
right side of `**` is a `unary`, so `2 ** -1` works.

A parser needs only two helpers:

```python
def peek(self): return self.tokens[self.i]
def expect(self, kind, value=None):  # consume a token or raise ParseError
```

## 3. AST & evaluation

Represent nodes as small frozen dataclasses. Evaluate with `match`:

```python
match node:
    case Num(value): return value
    case BinOp(op, left, right): return OPS[op](ev(left), ev(right))
```

## 4. Good errors

Every error should carry the **position** in the source, so the user sees:

```
1 + * 2
    ^ unexpected '*'
```

---

Run: `python academy.py check a4`. The answers, with explanations, are in `solution.py`.
