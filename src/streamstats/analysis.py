from src.streamstats.models import LogStatistics
from src.streamstats.parsers import parse_csv, parse_jsonl
from src.streamstats.constants import AVAILABLE_FORMATS


def analyze(paths: list, format: str, skip_invalid: bool = False) -> LogStatistics:
    """Сортирует файлы
    Args:
        paths - список путей к файлам
        format - строка формата
        skip_invalid - булево значение, которое указывает, что делать с битыми строками
    Returns:
        statistics - объект dataclass
    """
    statistics = LogStatistics()
    for path in paths:
        # csv
        if format == AVAILABLE_FORMATS[0]:
            parse_csv(path, skip_invalid, statistics)
        # jsonl
        elif format == AVAILABLE_FORMATS[1]:
            parse_jsonl(path, skip_invalid, statistics)
    return statistics
