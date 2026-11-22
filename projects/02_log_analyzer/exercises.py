"""Project 02 — Web Access Log Analyzer (CLI).

Read LESSON.md for the full specification.
Run tests:  python academy.py check p2
Run the CLI: python projects/02_log_analyzer/exercises.py projects/02_log_analyzer/sample_access.log
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Iterator

LINE_RE = re.compile(
    r"TODO: replace me with a regex that uses named groups, one per field"
)
TIMESTAMP_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


@dataclass(frozen=True)
class LogEntry:
    ip: str
    timestamp: datetime
    method: str
    path: str
    status: int
    size: int
    duration: float

    # TODO: is_error property


def parse_line(line: str) -> LogEntry | None:
    raise NotImplementedError


def read_entries(lines: Iterable[str]) -> Iterator[LogEntry]:
    raise NotImplementedError


class Analyzer:
    def __init__(self, lines: Iterable[str]) -> None:
        raise NotImplementedError

    # TODO: status_counts, top_paths, error_rate, requests_per_hour, top_ips,
    #       percentile, bytes_served, report


def main(argv: list[str] | None = None) -> int:
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(main())
