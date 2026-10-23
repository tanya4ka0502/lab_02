from pathlib import Path
import typer
from src.streamstats.analysis import analyze
from src.streamstats.errors import CliConfigError, InvalidEventError, StreamStatsError
from src.streamstats.constants import AVAILABLE_FORMATS
from src.streamstats.report import build_report, render_json

app = typer.Typer()


@app.command()
def analyze(
    inputs: list[Path] = typer.Argument(...),
    format: str = typer.Option(..., "--format"),
    output: str = typer.Option(None, "--output", "-o"),
    skip_invalid: bool = typer.Option(False, "--skip-invalid"),
) -> None:
    """Принимает команду пользователя, вызвает нужные функции из других файлов, обрабатывает ошибки.
    Args:
        inputs - список путей к файлам, которые нужно прочитать
        format - строка, обозначающая формат файлов
        output - путь к файлу для сохранения отчета
        skip_invalid - булево значение, которое указывает, что делать с битыми строками
    Returns:
        None"""
    if format.lower() not in AVAILABLE_FORMATS:
        typer.echo(f"streamstats: unsupported format {format}", err=True)
        raise typer.Exit(1)
    output_path = None
    if output:
        output_path = Path(output)
        if not output_path.parent.is_dir():
            typer.echo(f"streamstats: no such directory: {output_path.parent}", err=True)
            raise typer.Exit(1)
    try:
        statistics = analyze(inputs, format.lower(), skip_invalid=skip_invalid)
        text = render_json(build_report(statistics))
    except InvalidEventError as e:
        typer.echo(f"streamstats: {e}", err=True)
        raise typer.Exit(2)
    except (CliConfigError, StreamStatsError) as e:
        typer.echo(f"streamstats: {e}", err=True)
        raise typer.Exit(1)
    except FileNotFoundError as e:
        typer.echo(f"streamstats: {e}", err=True)
        raise typer.Exit(1)
    if output_path:
        output_path.write_text(text, encoding="utf-8")
    else:
        typer.echo(text, nl=False)


if __name__ == "__main__":
    app()
