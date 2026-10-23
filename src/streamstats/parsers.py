import csv
import json
import logging
from datetime import datetime
from src.streamstats.errors import InvalidEventError, InvalidTimestampError
from src.streamstats.models import Event, Level
from src.streamstats.constants import FIELDS

logger = logging.getLogger("streamstats")


def make_event(data: dict, file: str, line_number: int) -> Event:
    """Принимает словарь с данными и проверяет поля
    Args:
        data - словарь с данными файлов
        file - имя файла
        line_number - номер строки
    Returns:
        Event - объект"""
    if not isinstance(data, dict):
        raise InvalidEventError("not an object", file, line_number)
    for f in FIELDS:
        if f not in data:
            raise InvalidEventError(f"missing field: {f}", file, line_number)
    timestamp = data["timestamp"]
    if not isinstance(timestamp, str):
        raise InvalidTimestampError("timestamp is not a string", file, line_number)
    timestamp = timestamp.strip()
    if timestamp.endswith("Z"):
        timestamp = timestamp[:-1] + "+00:00"
    try:
        timestamp = datetime.fromisoformat(timestamp)
    except ValueError:
        raise InvalidTimestampError(f"bad timestamp: {data['timestamp']}", file, line_number)
    level = data["level"]
    if not isinstance(level, str):
        raise InvalidEventError("level is not a string", file, line_number)
    try:
        level = Level(level.strip().upper())
    except ValueError:
        raise InvalidEventError(f"bad level: {data['level']}", file, line_number)
    source = data["source"]
    if not isinstance(source, str) or not source.strip():
        raise InvalidEventError("source is empty", file, line_number)
    message = data["message"]
    if not isinstance(message, str):
        raise InvalidEventError("message is not a string", file, line_number)
    return Event(timestamp, level, source, message)


def parse_csv(path: str, skip_invalid: bool, statistics) -> None:
    """Проверяет файлы csv
    Args:
        path - путь к файлу
        skip_invalid - булево значение, которое указывает, что делать с битыми строками
        statistics - объект dataclass
    Returns:
        None"""
    statistics.files.append(str(path))
    with open(path, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            return
        for field in FIELDS:
            if field not in reader.fieldnames:
                raise InvalidEventError(f"CSV header missing: {field}", str(path), 1)
        for line_number, row in enumerate(reader, start=2):
            if not row or all(value in (None, "") for value in row.values()):
                continue
            try:
                event = make_event(dict(row), str(path), line_number)
            except InvalidEventError as error:
                if skip_invalid:
                    logger.warning("%s", error)
                    statistics.skipped += 1
                    continue
                raise
            statistics.add(event)


def parse_jsonl(path: str, skip_invalid: bool, statistics) -> None:
    """Проверяет файлы jsonl
    Args:
        path - путь к файлу
        skip_invalid - булево значение, которое указывает, что делать с битыми строками
        statistics - объект dataclass
    Returns:
        None"""
    statistics.files.append(str(path))
    with open(path, encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                error = InvalidEventError("bad JSON", str(path), line_number)
                if skip_invalid:
                    logger.warning("%s", error)
                    statistics.skipped += 1
                    continue
                raise error
            try:
                event = make_event(data, str(path), line_number)
            except InvalidEventError as e:
                if skip_invalid:
                    logger.warning("%s", e)
                    statistics.skipped += 1
                    continue
                raise
            statistics.add(event)
