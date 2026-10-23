from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Level(str, Enum):
    """Уровни важности"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class Event:
    """Модель одного события"""

    timestamp: datetime
    level: Level
    source: str
    message: str


@dataclass
class LogStatistics:
    """Статистика"""

    total: int = 0
    by_level: Counter = field(default_factory=Counter)
    by_source: Counter = field(default_factory=Counter)
    error_sources: Counter = field(default_factory=Counter)
    first_timestamp: datetime = None
    last_timestamp: datetime = None
    skipped: int = 0
    files: list = field(default_factory=list)

    def add(self, event):
        self.total += 1
        self.by_level[event.level] += 1
        self.by_source[event.source] += 1
        if event.level in (Level.ERROR, Level.CRITICAL):
            self.error_sources[event.source] += 1
        if self.first_timestamp is None or event.timestamp < self.first_timestamp:
            self.first_timestamp = event.timestamp
        if self.last_timestamp is None or event.timestamp > self.last_timestamp:
            self.last_timestamp = event.timestamp
