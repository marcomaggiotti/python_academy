import dataclasses
import inspect
from datetime import datetime, timezone
from pathlib import Path

import pytest

from academy_loader import load

ex = load(__file__)

SAMPLE = Path(__file__).with_name("sample_access.log")

LINES = [
    '10.0.0.1 - - [10/Oct/2026:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326 0.012',
    '10.0.0.2 - - [10/Oct/2026:13:59:01 +0000] "POST /api/login HTTP/1.1" 401 120 0.250',
    '10.0.0.1 - - [10/Oct/2026:14:01:00 +0000] "GET /search?q=py HTTP/1.1" 200 5000 0.040',
    "complete garbage",
    "",
    '10.0.0.3 - - [10/Oct/2026:14:30:00 +0000] "GET /index.html HTTP/2.0" 304 - 0.001',
    '10.0.0.1 - - [99/Foo/2026:14:30:00 +0000] "GET /bad-date HTTP/1.1" 200 1 0.001',
    '10.0.0.2 - - [10/Oct/2026:15:00:00 +0000] "GET /search HTTP/1.1" 500 300 1.500',
]


def test_parse_line_valid():
    e = ex.parse_line(LINES[0])
    assert e == ex.LogEntry(
        ip="10.0.0.1",
        timestamp=datetime(2026, 10, 10, 13, 55, 36, tzinfo=timezone.utc),
        method="GET",
        path="/index.html",
        status=200,
        size=2326,
        duration=0.012,
    )
    assert not e.is_error
    with pytest.raises(dataclasses.FrozenInstanceError):
        e.status = 1


def test_parse_line_details():
    assert ex.parse_line(LINES[1]).is_error
    assert ex.parse_line(LINES[2]).path == "/search"
    assert ex.parse_line(LINES[5]).size == 0


@pytest.mark.parametrize("line", [LINES[3], LINES[4], LINES[6]])
def test_parse_line_invalid(line):
    assert ex.parse_line(line) is None


def test_regex_uses_named_groups():
    assert ex.LINE_RE.groupindex, "use named groups: (?P<name>...)"


def test_read_entries():
    gen = ex.read_entries(LINES)
    assert inspect.isgenerator(gen)
    assert [e.ip for e in gen] == ["10.0.0.1", "10.0.0.2", "10.0.0.1", "10.0.0.3", "10.0.0.2"]


@pytest.fixture
def analyzer():
    return ex.Analyzer(line for line in LINES)  # one-shot generator on purpose


def test_counts(analyzer):
    assert analyzer.total == 5
    assert analyzer.skipped == 2
    assert analyzer.status_counts() == {200: 2, 401: 1, 304: 1, 500: 1}
    assert analyzer.bytes_served() == 2326 + 120 + 5000 + 0 + 300


def test_tops(analyzer):
    assert analyzer.top_paths(2) == [("/index.html", 2), ("/search", 2)]
    assert analyzer.top_paths(10)[-1] == ("/api/login", 1)
    assert analyzer.top_ips(1) == [("10.0.0.1", 2)]
    assert analyzer.top_ips(2) == [("10.0.0.1", 2), ("10.0.0.2", 2)]


def test_error_rate(analyzer):
    assert analyzer.error_rate() == pytest.approx(2 / 5)
    assert ex.Analyzer([]).error_rate() == 0.0


def test_requests_per_hour(analyzer):
    per_hour = analyzer.requests_per_hour()
    assert per_hour == {"2026-10-10 13:00": 2, "2026-10-10 14:00": 2, "2026-10-10 15:00": 1}
    assert list(per_hour) == sorted(per_hour)


def test_percentile(analyzer):
    # sorted durations: 0.001, 0.012, 0.040, 0.250, 1.500
    assert analyzer.percentile(50) == 0.040
    assert analyzer.percentile(95) == 1.500
    assert analyzer.percentile(20) == 0.001
    assert analyzer.percentile(100) == 1.500
    assert ex.Analyzer([]).percentile(95) == 0.0


def test_report(analyzer):
    text = analyzer.report(top=2)
    assert "Total requests: 5" in text
    assert "Error rate: 40.0%" in text
    assert "p95 latency: 1.500s" in text
    assert "Top paths:" in text
    after = text.split("Top paths:", 1)[1]
    assert "/index.html" in after and "/search" in after


def test_main_on_sample(capsys):
    assert ex.main([str(SAMPLE), "--top", "3"]) == 0
    out = capsys.readouterr().out
    assert "Total requests: 240" in out
    assert "Top paths:" in out


def test_main_missing_file(capsys, tmp_path):
    assert ex.main([str(tmp_path / "nope.log")]) == 1
    captured = capsys.readouterr()
    assert captured.err.strip() and not captured.out.strip()
