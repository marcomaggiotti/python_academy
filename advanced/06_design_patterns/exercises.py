"""Advanced 06: Design Patterns, the Pythonic Way.

Run: python academy.py check a6
"""

from __future__ import annotations

import typing
import weakref
from contextlib import contextmanager
from typing import Any, Callable, Iterator


# --- Challenge 1: event bus with weak references ---------------------------------------

class EventBus:
    """
        bus = EventBus()
        unsubscribe = bus.subscribe("order.created", handler)
        bus.subscribe("*", audit_log)          # "*" receives EVERY event
        bus.publish("order.created", payload)  -> number of handlers called
        unsubscribe()                          # idempotent

    - Handlers are called as handler(topic, payload), topic subscribers first (in
      subscription order), then "*" subscribers.
    - BOUND METHODS are held weakly (weakref.WeakMethod): if their object is garbage
      collected, they silently disappear. Plain functions/lambdas are held strongly.
    - Subscribing the same handler twice to the same topic has no extra effect.
    - If a handler raises, the remaining handlers still run; afterwards publish
      raises an ExceptionGroup("handler errors", [...]) with all the errors.
    - bus.subscriber_count(topic) -> number of live subscribers for that exact topic.
    """

    def __init__(self) -> None:
        raise NotImplementedError


# --- Challenge 2: command pattern with undo / redo ----------------------------------------

class TextEditor:
    """
        ed = TextEditor()
        ed.insert(0, "Hello")       # ed.text == "Hello"
        ed.insert(5, " world")      # "Hello world"
        ed.delete(0, 6)             # "world"
        ed.undo()                   # "Hello world"
        ed.redo()                   # "world"
        ed.can_undo, ed.can_redo    # bool properties

    - A new edit after undo() clears the redo history.
    - insert/delete positions out of range -> IndexError (and nothing is recorded).
    - undo()/redo() with nothing to do -> return False (True when something happened).
    - `with ed.batch():` groups all edits inside into ONE undo step. If the block
      raises, the edits made inside are rolled back and the exception propagates.
      Batches may be nested (only the outermost one creates the undo step).
    """

    def __init__(self, text: str = "") -> None:
        raise NotImplementedError


# --- Challenge 3: a dependency-injection container ----------------------------------------------

class ResolutionError(LookupError):
    pass


class Container:
    """
        c = Container()
        c.register(Config, lambda: Config(debug=True), singleton=True)
        c.register(Repository, SqlRepository)       # an implementation class as factory
        service = c.resolve(UserService)            # auto-wired!

    - register(key, factory=None, *, singleton=False): factory defaults to `key`
      itself. A factory may be any callable; if it's a class, its __init__'s
      type-hinted parameters are resolved from the container (auto-wiring).
      Parameters with default values are left to their defaults if the type
      can't be resolved.
    - resolve(key): unregistered CLASSES can still be auto-wired (treated as
      non-singleton registrations of themselves).
    - singleton=True: the same instance on every resolve.
    - Missing dependency (e.g. a parameter typed `int`) -> ResolutionError naming it.
    - Dependency cycles (A needs B needs A) -> ResolutionError mentioning "cycle".
    - c.override(key, instance) as a context manager: inside, resolve(key) returns
      `instance`; restored afterwards (great for tests).
    """

    def __init__(self) -> None:
        raise NotImplementedError


# --- Challenge 4: middleware chain -----------------------------------------------------------

Handler = Callable[[dict], dict]
Middleware = Callable[[dict, Handler], dict]


def build_pipeline(handler: Handler, middlewares: list[Middleware]) -> Handler:
    """Return a callable request -> response where middlewares[0] is the OUTERMOST.
    Each middleware is called as mw(request, call_next) and may modify the request,
    short-circuit (return without calling call_next), or modify the response.

        def add_header(req, call_next):
            resp = call_next(req); resp["x-powered-by"] = "py"; return resp
    """
    raise NotImplementedError
