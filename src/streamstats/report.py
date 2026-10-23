import json
from src.streamstats.models import Level


def build_report(statistics) -> dict:
    """Записывает данные в словарь
    Args:
        statistics - объект dataclass
    Returns:
        Словарь"""
    return {
        "total": statistics.total,
        "skipped": statistics.skipped,
        "files": list(statistics.files),
        "by_level": {level.value: statistics.by_level.get(level, 0) for level in Level},
        "by_source": dict(statistics.by_source.most_common()),
        "top_error_sources": [
            {"source": s, "count": c} for s, c in statistics.error_sources.most_common(5)
        ],
        "first_timestamp": statistics.first_timestamp.isoformat()
        if statistics.first_timestamp
        else None,
        "last_timestamp": statistics.last_timestamp.isoformat()
        if statistics.last_timestamp
        else None,
    }


def render_json(report: dict) -> json:
    """Превращает словарь в json
    Args:
        report - словарь, который возвращает функция build_report
    Returns:
        json-строка"""
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"
