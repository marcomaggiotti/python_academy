"""Reference solution for Project 02."""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime

LINE_RE = re.compile(
    r"(?P<ip>\S+) \S+ \S+ "
    r"\[(?P<timestamp>[^\]]+)\] "
    r'"(?P<method>[A-Z]+) (?P<path>\S+) [^"]*" '
    r"(?P<status>\d{3}) "
    r"(?P<size>\d+|-) "
    r"(?P<duration>\d+(?:\.\d+)?)\s*$"
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

    @property
    def is_error(self):
        return self.status >= 400


def parse_line(line):
    match = LINE_RE.match(line.strip())
    if not match:
        return None
    g = match.groupdict()
    try:
        ts = datetime.strptime(g["timestamp"], TIMESTAMP_FORMAT)
    except ValueError:
        return None
    return LogEntry(
        ip=g["ip"],
        timestamp=ts,
        method=g["method"],
        path=g["path"].split("?", 1)[0],
        status=int(g["status"]),
        size=0 if g["size"] == "-" else int(g["size"]),
        duration=float(g["duration"]),
    )


def read_entries(lines):
    for line in lines:
        entry = parse_line(line)
        if entry is not None:
            yield entry


def _top(counter, n):
    return sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


class Analyzer:
    def __init__(self, lines):
        self.total = 0
        self.skipped = 0
        self._status = Counter()
        self._paths = Counter()
        self._ips = Counter()
        self._hours = Counter()
        self._durations = []
        self._errors = 0
        self._bytes = 0
        for line in lines:
            if not line.strip():
                continue
            entry = parse_line(line)
            if entry is None:
                self.skipped += 1
                continue
            self.total += 1
            self._status[entry.status] += 1
            self._paths[entry.path] += 1
            self._ips[entry.ip] += 1
            self._hours[entry.timestamp.strftime("%Y-%m-%d %H:00")] += 1
            self._durations.append(entry.duration)
            self._errors += entry.is_error
            self._bytes += entry.size
        self._durations.sort()

    def status_counts(self):
        return Counter(self._status)

    def top_paths(self, n):
        return _top(self._paths, n)

    def top_ips(self, n):
        return _top(self._ips, n)

    def error_rate(self):
        return self._errors / self.total if self.total else 0.0

    def requests_per_hour(self):
        return dict(sorted(self._hours.items()))

    def percentile(self, p):
        if not self._durations:
            return 0.0
        index = max(math.ceil(p / 100 * len(self._durations)) - 1, 0)
        return self._durations[index]

    def bytes_served(self):
        return self._bytes

    def report(self, top=5):
        lines = [
            f"Total requests: {self.total}",
            f"Skipped lines: {self.skipped}",
            f"Bytes served: {self.bytes_served():,}",
            f"Error rate: {self.error_rate() * 100:.1f}%",
            f"p50 latency: {self.percentile(50):.3f}s",
            f"p95 latency: {self.percentile(95):.3f}s",
            "",
            "Status codes:",
            *(f"  {code}  {count}" for code, count in sorted(self._status.items())),
            "",
            "Top paths:",
            *(f"  {path}  {count}" for path, count in self.top_paths(top)),
            "",
            "Top IPs:",
            *(f"  {ip}  {count}" for ip, count in self.top_ips(top)),
            "",
            "Requests per hour:",
            *(f"  {hour}  {count}" for hour, count in self.requests_per_hour().items()),
        ]
        return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Analyze a web access log.")
    parser.add_argument("logfile")
    parser.add_argument("--top", type=int, default=5, help="how many top paths/IPs to show")
    args = parser.parse_args(argv)
    try:
        with open(args.logfile, encoding="utf-8") as f:
            analyzer = Analyzer(f)
    except FileNotFoundError:
        print(f"error: no such file: {args.logfile}", file=sys.stderr)
        return 1
    print(analyzer.report(top=args.top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
