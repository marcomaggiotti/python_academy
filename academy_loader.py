"""Loads the module under test for each exercise folder.

Tests call ``load(__file__)``. By default this returns *your* ``exercises.py``.
Set the environment variable ``ACADEMY_MODE=solution`` to run the same tests
against the reference ``solution.py`` instead (useful to confirm the tests
themselves are correct, or to peek at a passing implementation).
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType


def load(test_file: str) -> ModuleType:
    folder = Path(test_file).resolve().parent
    mode = os.environ.get("ACADEMY_MODE", "exercise")
    target = folder / ("solution.py" if mode == "solution" else "exercises.py")
    name = f"academy_{folder.name}_{target.stem}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, target)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
