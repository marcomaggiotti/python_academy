"""Answers for Advanced 06, with explanations."""

from __future__ import annotations

import functools
import inspect
import typing
import weakref
from contextlib import contextmanager


# --- Challenge 1 -------------------------------------------------------------
# Every subscription is stored as a zero-arg "resolver" that returns the live
# callable or None. For bound methods the resolver is a WeakMethod; for plain
# functions it's a lambda that closes over the function (a strong reference).
# We also store an identity key so duplicates and unsubscribe can find it:
# (id(obj), func) for methods, the function itself otherwise.

class EventBus:
    def __init__(self):
        self._subs: dict[str, list[tuple[object, typing.Callable]]] = {}

    @staticmethod
    def _make_entry(handler):
        if inspect.ismethod(handler):
            ref = weakref.WeakMethod(handler)
            return (id(handler.__self__), handler.__func__), ref
        return handler, (lambda h=handler: h)

    def subscribe(self, topic, handler):
        key, resolver = self._make_entry(handler)
        entries = self._subs.setdefault(topic, [])
        if not any(k == key and r() is not None for k, r in entries):
            entries.append((key, resolver))

        def unsubscribe():
            current = self._subs.get(topic, [])
            self._subs[topic] = [(k, r) for k, r in current if k != key]

        return unsubscribe

    def _live(self, topic):
        entries = self._subs.get(topic, [])
        alive = [(k, r) for k, r in entries if r() is not None]
        self._subs[topic] = alive  # prune dead weak refs as we go
        return [r() for _, r in alive]

    def subscriber_count(self, topic):
        return len(self._live(topic))

    def publish(self, topic, payload=None):
        handlers = self._live(topic) + (self._live("*") if topic != "*" else [])
        errors = []
        for handler in handlers:
            try:
                handler(topic, payload)
            except Exception as exc:
                errors.append(exc)
        if errors:
            raise ExceptionGroup("handler errors", errors)
        return len(handlers)


# --- Challenge 2 -------------------------------------------------------------
# Commands record exactly what they need to reverse themselves. A batch is a
# composite command. While a batch is open, executed commands go into the
# batch instead of the undo stack.

class _Insert:
    def __init__(self, pos, text):
        self.pos, self.text = pos, text

    def do(self, s):
        return s[: self.pos] + self.text + s[self.pos:]

    def undo(self, s):
        return s[: self.pos] + s[self.pos + len(self.text):]


class _Delete:
    def __init__(self, pos, length):
        self.pos, self.length, self.removed = pos, length, ""

    def do(self, s):
        self.removed = s[self.pos: self.pos + self.length]
        return s[: self.pos] + s[self.pos + self.length:]

    def undo(self, s):
        return s[: self.pos] + self.removed + s[self.pos:]


class _Batch:
    def __init__(self):
        self.commands = []

    def do(self, s):
        for c in self.commands:
            s = c.do(s)
        return s

    def undo(self, s):
        for c in reversed(self.commands):
            s = c.undo(s)
        return s


class TextEditor:
    def __init__(self, text=""):
        self.text = text
        self._undo, self._redo = [], []
        self._batches = []  # stack of open batches

    def _execute(self, cmd):
        self.text = cmd.do(self.text)
        if self._batches:
            self._batches[-1].commands.append(cmd)
        else:
            self._undo.append(cmd)
            self._redo.clear()

    def insert(self, pos, text):
        if not 0 <= pos <= len(self.text):
            raise IndexError(f"position {pos} out of range")
        self._execute(_Insert(pos, text))

    def delete(self, pos, length):
        if pos < 0 or length < 0 or pos + length > len(self.text):
            raise IndexError("delete range out of bounds")
        self._execute(_Delete(pos, length))

    @property
    def can_undo(self):
        return bool(self._undo)

    @property
    def can_redo(self):
        return bool(self._redo)

    def undo(self):
        if not self._undo:
            return False
        cmd = self._undo.pop()
        self.text = cmd.undo(self.text)
        self._redo.append(cmd)
        return True

    def redo(self):
        if not self._redo:
            return False
        cmd = self._redo.pop()
        self.text = cmd.do(self.text)
        self._undo.append(cmd)
        return True

    @contextmanager
    def batch(self):
        batch = _Batch()
        self._batches.append(batch)
        try:
            yield self
        except BaseException:
            self._batches.pop()
            self.text = batch.undo(self.text)  # roll back what this batch did
            raise
        self._batches.pop()
        if batch.commands:
            if self._batches:              # nested: fold into the parent batch
                self._batches[-1].commands.append(batch)
            else:
                self._undo.append(batch)
                self._redo.clear()


# --- Challenge 3 -------------------------------------------------------------
# resolve() keeps a stack of keys currently being built. Seeing a key that is
# already on the stack means there's a cycle. Auto-wiring inspects the factory's
# signature and resolves each annotated parameter.

class ResolutionError(LookupError):
    pass


class Container:
    def __init__(self):
        self._registry = {}      # key -> (factory, singleton)
        self._singletons = {}
        self._overrides = {}
        self._resolving = []

    def register(self, key, factory=None, *, singleton=False):
        self._registry[key] = (factory or key, singleton)
        self._singletons.pop(key, None)

    @contextmanager
    def override(self, key, instance):
        missing = object()
        previous = self._overrides.get(key, missing)
        self._overrides[key] = instance
        try:
            yield instance
        finally:
            if previous is missing:
                del self._overrides[key]
            else:
                self._overrides[key] = previous

    def resolve(self, key):
        if key in self._overrides:
            return self._overrides[key]
        if key in self._singletons:
            return self._singletons[key]
        if key in self._resolving:
            chain = " -> ".join(getattr(k, "__name__", str(k)) for k in [*self._resolving, key])
            raise ResolutionError(f"dependency cycle: {chain}")
        if key in self._registry:
            factory, singleton = self._registry[key]
        elif isinstance(key, type) and key.__module__ != "builtins":
            factory, singleton = key, False
        else:
            raise ResolutionError(f"cannot resolve {getattr(key, '__name__', key)!r}")

        self._resolving.append(key)
        try:
            instance = self._build(factory)
        finally:
            self._resolving.pop()
        if singleton:
            self._singletons[key] = instance
        return instance

    def _build(self, factory):
        target = factory.__init__ if isinstance(factory, type) else factory
        try:
            hints = typing.get_type_hints(target)
        except Exception:
            hints = {}
        try:
            params = inspect.signature(factory).parameters
        except (TypeError, ValueError):
            return factory()
        kwargs = {}
        for name, param in params.items():
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue
            annotation = hints.get(name)
            if annotation is None:
                if param.default is param.empty:
                    raise ResolutionError(f"parameter {name!r} has no type hint")
                continue
            try:
                kwargs[name] = self.resolve(annotation)
            except ResolutionError as exc:
                if "cycle" in str(exc):
                    raise  # a cycle is always fatal, even when there's a default
                if param.default is param.empty:
                    owner = getattr(factory, "__name__", factory)
                    raise ResolutionError(f"cannot resolve parameter {name!r} of {owner}: {exc}") from exc
                # otherwise: leave it out, and the parameter's default value is used
        return factory(**kwargs)


# --- Challenge 4 -------------------------------------------------------------
# Fold from the inside out: start with the handler, and wrap it with each
# middleware from last to first. functools.partial binds the current `next_`
# early, which avoids the late-binding closure bug.

def build_pipeline(handler, middlewares):
    call = handler
    for mw in reversed(middlewares):
        call = functools.partial(lambda req, mw, nxt: mw(req, nxt), mw=mw, nxt=call)
    return call
