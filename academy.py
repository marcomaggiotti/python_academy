#!/usr/bin/env python3
"""Python Academy command-line helper.

Usage:
    python academy.py list                 # list modules and projects
    python academy.py progress             # run every test suite, show a scoreboard
    python academy.py check 03             # run tests for module 03 (use p1, p2 for projects)
    python academy.py check 03 -k vector   # extra args are passed through to pytest
    python academy.py verify               # run all tests against the reference solutions
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SECTIONS = ("modules", "projects")


def units() -> list[Path]:
    found = []
    for section in SECTIONS:
        base = ROOT / section
        if base.is_dir():
            found += sorted(p for p in base.iterdir() if (p / "exercises.py").exists())
    return found


def title_of(unit: Path) -> str:
    lesson = unit / "LESSON.md"
    if lesson.exists():
        first = lesson.read_text(encoding="utf-8").splitlines()[0]
        return first.lstrip("# ").strip()
    return unit.name


def find(prefix: str) -> Path:
    """Resolve "3"/"03" -> module 03, "p1"/"p01" -> project 01, or any name fragment."""
    all_units = units()
    section = "modules"
    if (m := re.fullmatch(r"[pP](\d+)", prefix)):
        section, prefix = "projects", m.group(1)
    if prefix.isdigit():
        number = f"{int(prefix):02d}_"
        matches = [u for u in all_units if u.parent.name == section and u.name.startswith(number)]
    else:
        matches = [u for u in all_units if prefix in u.name]
    if not matches:
        sys.exit(f"No module or project matches {prefix!r}. Try: python academy.py list")
    if len(matches) > 1:
        names = ", ".join(f"{m.parent.name}/{m.name}" for m in matches)
        sys.exit(f"{prefix!r} is ambiguous: {names}")
    return matches[0]


def run_pytest(target: Path, extra: list[str], solution: bool = False, quiet: bool = False):
    env = dict(os.environ)
    if solution:
        env["ACADEMY_MODE"] = "solution"
    cmd = [sys.executable, "-m", "pytest", str(target), *extra]
    if quiet:
        cmd += ["-p", "no:cacheprovider", "--tb=no", "-rN"]
        return subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    return subprocess.run(cmd, cwd=ROOT, env=env)


def summarize(output: str) -> tuple[int, int]:
    passed = sum(int(n) for n in re.findall(r"(\d+) passed", output))
    failed = sum(int(n) for n in re.findall(r"(\d+) (?:failed|error)", output))
    return passed, failed


def bar(done: int, total: int, width: int = 20) -> str:
    filled = round(width * done / total) if total else 0
    return "█" * filled + "░" * (width - filled)


def cmd_list() -> None:
    current = None
    for unit in units():
        if unit.parent.name != current:
            current = unit.parent.name
            print(f"\n{current.upper()}")
        print(f"  {unit.name:<34} {title_of(unit)}")
    print()


def cmd_progress(solution: bool = False) -> None:
    grand_pass = grand_total = 0
    print()
    for unit in units():
        result = run_pytest(unit, [], solution=solution, quiet=True)
        passed, failed = summarize(result.stdout)
        total = passed + failed
        grand_pass += passed
        grand_total += total
        mark = "✅" if total and not failed else "  "
        print(f"{mark} {unit.name:<34} {bar(passed, total)} {passed:>3}/{total:<3}")
    print(f"\n   {'TOTAL':<34} {bar(grand_pass, grand_total)} {grand_pass:>3}/{grand_total:<3}\n")


def main(argv: list[str]) -> None:
    if not argv or argv[0] in {"-h", "--help", "help"}:
        print(__doc__)
        return
    command, *rest = argv
    if command == "list":
        cmd_list()
    elif command == "progress":
        cmd_progress()
    elif command == "verify":
        cmd_progress(solution=True)
    elif command == "check":
        if not rest:
            sys.exit("Usage: python academy.py check <module-number-or-name> [pytest args]")
        unit = find(rest[0])
        print(f"→ {unit.parent.name}/{unit.name}: {title_of(unit)}\n")
        sys.exit(run_pytest(unit, rest[1:] or ["-v"]).returncode)
    else:
        sys.exit(f"Unknown command {command!r}.\n{__doc__}")


if __name__ == "__main__":
    main(sys.argv[1:])
