from datetime import datetime
from src.streamstats.analysis import analyze
from src.streamstats.models import Event, Level, LogStatistics
from src.streamstats.report import build_report


def write(path, text):
    path.write_text(text, encoding="utf-8")
    return str(path)


def line(ts, lvl, src):
    return f'{{"timestamp":"{ts}","level":"{lvl}","source":"{src}","message":"m"}}\n'


def test_analyze_merges_multiple_files(tmp_path):
    f1 = write(tmp_path / "a.jsonl", line("2024-01-01T00:00:00Z", "INFO", "x"))
    f2 = write(tmp_path / "b.jsonl", line("2024-01-02T00:00:00Z", "ERROR", "y"))
    stats = analyze([f1, f2], "jsonl")
    report = build_report(stats)
    assert report["total"] == 2
    assert report["files"] == [f1, f2]
    assert report["first_timestamp"].startswith("2024-01-01")
    assert report["last_timestamp"].startswith("2024-01-02")


def test_build_report_calculates_top_errors_correctly():
    stats = LogStatistics()
    stats.add(Event(datetime(2024, 1, 1), Level.ERROR, "api", "m"))
    stats.add(Event(datetime(2024, 1, 2), Level.ERROR, "api", "m"))
    stats.add(Event(datetime(2024, 1, 3), Level.CRITICAL, "db", "m"))
    stats.add(Event(datetime(2024, 1, 4), Level.INFO, "api", "m"))
    report = build_report(stats)
    assert report["total"] == 4
    assert report["by_level"]["ERROR"] == 2
    assert report["by_level"]["CRITICAL"] == 1
    assert report["by_level"]["INFO"] == 1
    top = report["top_error_sources"]
    assert len(top) == 2
    assert top[0] == {"source": "api", "count": 2}
    assert top[1] == {"source": "db", "count": 1}


def test_build_report_empty_stats():
    stats = LogStatistics()
    report = build_report(stats)
    assert report["total"] == 0
    assert report["first_timestamp"] is None
    assert report["last_timestamp"] is None
