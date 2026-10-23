import pytest
from src.streamstats import parsers
from src.streamstats.errors import InvalidEventError
from src.streamstats.models import LogStatistics
from src.streamstats.report import build_report


def write_file(path, text):
    path.write_text(text, encoding="utf-8")
    return str(path)


def make_json_line(ts, lvl, src, msg="m"):
    return f'{{"timestamp":"{ts}","level":"{lvl}","source":"{src}","message":"{msg}"}}\n'


def test_parse_csv_valid(tmp_path):
    path = write_file(
        tmp_path / "ok.csv",
        "timestamp,level,source,message\n"
        "2024-01-01T00:00:00Z,INFO,api,ok\n"
        "2024-01-02T00:00:00Z,ERROR,db,boom\n",
    )
    statistics = LogStatistics()
    parsers.parse_csv(path, skip_invalid=False, statistics=statistics)
    report = build_report(statistics)
    assert report["total"] == 2
    assert report["by_source"] == {"api": 1, "db": 1}
    assert report["files"] == [path]


def test_parse_csv_empty_file(tmp_path):
    path = write_file(tmp_path / "empty.csv", "")
    statistics = LogStatistics()
    parsers.parse_csv(path, skip_invalid=False, statistics=statistics)
    assert build_report(statistics)["total"] == 0


def test_parse_csv_missing_column(tmp_path):
    path = write_file(tmp_path / "bad_header.csv", "timestamp,level\n2024-01-01T00:00:00Z,INFO\n")
    statistics = LogStatistics()
    with pytest.raises(InvalidEventError, match="CSV header missing: source"):
        parsers.parse_csv(path, skip_invalid=False, statistics=statistics)


def test_parse_csv_bad_timestamp(tmp_path):
    path = write_file(tmp_path / "bad_ts.csv", "timestamp,level,source,message\nnope,INFO,a,m\n")
    statistics = LogStatistics()
    with pytest.raises(InvalidEventError, match="bad timestamp: nope"):
        parsers.parse_csv(path, skip_invalid=False, statistics=statistics)


def test_parse_csv_skip_invalid(tmp_path, caplog):
    path = write_file(
        tmp_path / "skip.csv",
        "timestamp,level,source,message\nnope,INFO,a,m\n2024-01-01T00:00:00Z,INFO,a,ok\n",
    )
    statistics = LogStatistics()
    parsers.parse_csv(path, skip_invalid=True, statistics=statistics)
    report = build_report(statistics)
    assert report["total"] == 1
    assert report["skipped"] == 1
    assert "bad timestamp: nope" in caplog.text


def test_parse_jsonl_valid(tmp_path):
    path = write_file(
        tmp_path / "ok.jsonl",
        make_json_line("2024-01-01T00:00:00Z", "INFO", "a")
        + make_json_line("2024-01-02T00:00:00Z", "ERROR", "b"),
    )
    statistics = LogStatistics()
    parsers.parse_jsonl(path, skip_invalid=False, statistics=statistics)
    report = build_report(statistics)
    assert report["total"] == 2
    assert report["by_level"]["ERROR"] == 1


def test_parse_jsonl_bad_json_raises(tmp_path):
    path = write_file(tmp_path / "bad.jsonl", "{oops}\n")
    statistics = LogStatistics()
    with pytest.raises(InvalidEventError) as exc_info:
        parsers.parse_jsonl(path, skip_invalid=False, statistics=statistics)
    error_msg = str(exc_info.value)
    assert "bad JSON" in error_msg, f"Получено: {error_msg!r}"
    assert ":1" in error_msg, f"Получено: {error_msg!r}"


def test_parse_jsonl_skip_invalid(tmp_path, caplog):
    path = write_file(
        tmp_path / "skip.jsonl", "{oops}\n" + make_json_line("2024-01-01T00:00:00Z", "INFO", "a")
    )
    statistics = LogStatistics()
    parsers.parse_jsonl(path, skip_invalid=True, statistics=statistics)
    report = build_report(statistics)
    assert report["total"] == 1
    assert report["skipped"] == 1
    assert "bad JSON" in caplog.text


def test_parse_jsonl_missing_field(tmp_path):
    path = write_file(
        tmp_path / "miss.jsonl", '{"timestamp":"2024-01-01T00:00:00Z","level":"INFO"}\n'
    )
    statistics = LogStatistics()
    with pytest.raises(InvalidEventError, match="missing field: source"):
        parsers.parse_jsonl(path, skip_invalid=False, statistics=statistics)
