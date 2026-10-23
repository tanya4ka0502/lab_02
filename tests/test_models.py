from datetime import datetime, timezone
from src.streamstats.models import Event, Level, LogStatistics


def make(ts, lvl, src):
    return Event(datetime.fromisoformat(ts), Level(lvl), src, "m")


def test_add_basic():
    s = LogStatistics()
    s.add(make("2024-01-01T00:00:00+00:00", "INFO", "api"))
    s.add(make("2024-01-02T00:00:00+00:00", "ERROR", "db"))
    assert s.total == 2
    assert s.by_level[Level.INFO] == 1
    assert s.by_level[Level.ERROR] == 1
    assert s.by_source["api"] == 1
    assert s.by_source["db"] == 1
    assert s.error_sources == {"db": 1}


def test_first_last_are_min_max():
    s = LogStatistics()
    s.add(make("2024-01-15T00:00:00+00:00", "INFO", "a"))
    s.add(make("2024-01-01T00:00:00+00:00", "INFO", "a"))
    s.add(make("2024-01-31T00:00:00+00:00", "INFO", "a"))
    assert s.first_timestamp == datetime(2024, 1, 1, tzinfo=timezone.utc)
    assert s.last_timestamp == datetime(2024, 1, 31, tzinfo=timezone.utc)


def test_error_sources_ignores_info_and_warning():
    s = LogStatistics()
    s.add(make("2024-01-01T00:00:00+00:00", "INFO", "api"))
    s.add(make("2024-01-01T00:00:00+00:00", "WARNING", "api"))
    s.add(make("2024-01-01T00:00:00+00:00", "ERROR", "api"))
    s.add(make("2024-01-01T00:00:00+00:00", "CRITICAL", "db"))
    assert s.error_sources == {"api": 1, "db": 1}
