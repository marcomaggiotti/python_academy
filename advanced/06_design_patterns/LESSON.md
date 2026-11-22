# Advanced 06 — Design Patterns, the Pythonic Way

Many classic "Gang of Four" patterns shrink to a few lines in Python, because
functions are first-class and duck typing replaces most interfaces. Four still
earn their keep in real codebases.

## 1. Observer / event bus, and memory leaks

A bus that keeps strong references to subscribers' bound methods keeps those
objects alive forever. `weakref.WeakMethod(obj.method)` refers to a bound method
without owning `obj`. Call it (`ref()`) to get the method back, or `None` if
`obj` has been garbage-collected.

```python
import weakref
ref = weakref.WeakMethod(listener.on_event)
if (method := ref()) is not None:
    method(payload)
```

Plain functions are usually module-level and long-lived, so strong refs are fine for them.

## 2. Command pattern: undo/redo

Each edit is an object with `do()` and `undo()`. Keep two stacks:

```
do(cmd):  cmd.do(); undo_stack.append(cmd); redo_stack.clear()
undo():   cmd = undo_stack.pop(); cmd.undo(); redo_stack.append(cmd)
redo():   cmd = redo_stack.pop(); cmd.do();   undo_stack.append(cmd)
```

A *composite* command (a list of commands, undone in reverse) gives you grouped
edits, so that a whole batch is undone in one step.

## 3. Dependency injection container

Instead of classes constructing their own collaborators, they declare them:

```python
class UserService:
    def __init__(self, repo: UserRepository, mailer: Mailer): ...
```

A container reads the type hints (`typing.get_type_hints(cls.__init__)`), resolves
each dependency recursively, and caches singletons. Detect cycles with a
"currently resolving" stack.

## 4. Middleware chains (chain of responsibility)

Used by every web framework: each middleware wraps the next handler.

```python
def timing(request, call_next):
    start = time.perf_counter()
    response = call_next(request)
    response["ms"] = ...
    return response
```

Build the chain by folding from the innermost handler outwards. Watch out for
the late-binding closure trap from Module 02.

---

Run: `python academy.py check a6`. The answers, with explanations, are in `solution.py`.
