# Project 02 — Web Access Log Analyzer (CLI)

Build a command-line tool that streams a web-server access log and prints a
report. Combines **regex, dataclasses, generators, `collections`, `statistics`,
`datetime`, and `argparse`**.

A sample log is included: `sample_access.log`. When you're done:

```bash
python projects/02_log_analyzer/exercises.py projects/02_log_analyzer/sample_access.log --top 3
```

## Log format

```
203.0.113.9 - - [10/Oct/2026:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326 0.012
└─ ip                └─ timestamp                 └─ method path proto      │    │    └─ duration (s)
                                                                    status ─┘    └─ bytes ("-" means 0)
```

Timestamp format for `datetime.strptime`: `"%d/%b/%Y:%H:%M:%S %z"`.

## Specification

### `LogEntry` — frozen dataclass
`ip: str, timestamp: datetime, method: str, path: str, status: int, size: int, duration: float`
- `is_error` property → `status >= 400`

### `parse_line(line) -> LogEntry | None`
Use a **compiled regex with named groups**. Return `None` for lines that don't match
(or have an unparseable timestamp). Query strings are stripped from the path
(`/search?q=x` → `/search`).

### `read_entries(lines) -> Iterator[LogEntry]`
A generator yielding parsed entries, silently skipping bad lines. (Counting
skipped lines is the `Analyzer`'s job — see below.)

### `Analyzer`
Built with `Analyzer(lines)`; it must consume the input **in a single pass**
(the tests give it a one-shot generator).

| Attribute / method | Meaning |
|---|---|
| `total` | number of valid entries |
| `skipped` | number of non-empty lines that failed to parse |
| `status_counts()` | `Counter` of status codes |
| `top_paths(n)` | `[(path, count), ...]` most requested, ties alphabetical |
| `error_rate()` | fraction of entries with `is_error` (0.0 if no entries) |
| `requests_per_hour()` | `{"2026-10-10 13:00": count, ...}` sorted by hour |
| `top_ips(n)` | like `top_paths` but for IPs |
| `percentile(p)` | duration percentile using nearest-rank: sort durations, index `ceil(p/100 * N) - 1` (p in 1..100); `0.0` when empty |
| `bytes_served()` | total size |
| `report(top=5)` | multi-line string; must contain lines `Total requests: N`, `Error rate: 12.5%` (1 decimal), `p95 latency: 0.123s` (3 decimals), and a `Top paths:` section listing `  /path  count` |

### `main(argv=None) -> int`
`argparse` CLI: positional `logfile`, optional `--top N` (default 5). Prints the
report and returns `0`. If the file doesn't exist, print an error to **stderr**
and return `1`.

Run: `python academy.py check p2`
