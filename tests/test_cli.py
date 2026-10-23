import json
from typer.testing import CliRunner
from src.streamstats.__main__ import app

runner = CliRunner()


def _write(path, text):
    path.write_text(text, encoding="utf-8")
    return str(path)


def _line(ts, lvl, src):
    return f'{{"timestamp":"{ts}","level":"{lvl}","source":"{src}","message":"m"}}\n'


def test_cli_ok_writes_file(tmp_path):
    inp = _write(tmp_path / "in.jsonl", _line("2024-01-01T00:00:00Z", "INFO", "a"))
    out = tmp_path / "report.json"
    result = runner.invoke(app, ["analyze", inp, "--format", "jsonl", "--output", str(out)])
    assert result.exit_code == 0, f"exit={result.exit_code}, exc={result.exception!r}"
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["total"] == 1


def test_cli_prints_to_stdout(tmp_path):
    inp = _write(tmp_path / "in.jsonl", _line("2024-01-01T00:00:00Z", "INFO", "a"))
    result = runner.invoke(app, ["analyze", inp, "--format", "jsonl"])
    assert result.exit_code == 0, f"exit={result.exit_code}, exc={result.exception!r}"
    data = json.loads(result.stdout)
    assert data["total"] == 1


def test_cli_fails_with_code_2_on_bad_data(tmp_path):
    inp = _write(tmp_path / "bad.jsonl", "{bad\n")
    result = runner.invoke(app, ["analyze", inp, "--format", "jsonl"])
    assert result.exit_code == 2, f"exit={result.exit_code}, exc={result.exception!r}"
    assert "bad.jsonl:1" in result.stderr


def test_cli_fails_with_code_1_on_bad_format(tmp_path):
    inp = _write(tmp_path / "in.jsonl", "")
    result = runner.invoke(app, ["analyze", inp, "--format", "xml"])
    assert result.exit_code == 1, f"exit={result.exit_code}, exc={result.exception!r}"
    assert "unsupported format" in result.stderr


def test_cli_skips_invalid_with_flag(tmp_path):
    inp = _write(tmp_path / "skip.jsonl", "{bad\n" + _line("2024-01-01T00:00:00Z", "INFO", "a"))
    result = runner.invoke(app, ["analyze", inp, "--format", "jsonl", "--skip-invalid"])
    assert result.exit_code == 0, f"exit={result.exit_code}, exc={result.exception!r}"
    data = json.loads(result.stdout)
    assert data["total"] == 1
    assert data["skipped"] == 1
