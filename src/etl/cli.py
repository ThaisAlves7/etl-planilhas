import os
from pathlib import Path

import typer
from sqlalchemy import create_engine

from etl.config import carregar_config
from etl.load.tables import metadata
from etl.pipeline import executar

app = typer.Typer(help="Pipeline ETL de planilha de vendas")


@app.callback()
def principal() -> None:
    """Pipeline ETL de planilhas de vendas."""


def _engine():
    url = os.environ.get("DATABASE_URL")

    if not url:
        typer.echo("Erro: defina a variável de ambiente DATABASE_URL", err=True)
        raise typer.Exit(1)

    return create_engine(url)


@app.command("init-db")
def init_db() -> None:
    """Cria as tabelas no banco."""
    engine = _engine()
    metadata.create_all(engine)
    engine.dispose()
    typer.echo("Tabelas criadas.")


@app.command()
def run(
    arquivo: Path = typer.Argument(
        ..., exists=True, dir_okay=False, help="CSV a processar."
    ),
    config: Path = typer.Option(
        Path("config/vendas.yaml"),
        "--config",
        "-c",
        exists=True,
        dir_okay=False,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Reprocessa mesmo que já tenha sido processado.",
    ),
) -> None:
    """Processa uma planilha de vendas."""

    engine = _engine()

    try:
        cfg = carregar_config(str(config))
        resultado = executar(str(arquivo), engine, cfg, force=force)

    except Exception as e:
        linha = f"{type(e).__name__}: {e}".splitlines()[0][:300]
        typer.echo(f"Erro: {linha}", err=True)
        raise typer.Exit(1) from e

    finally:
        engine.dispose()

    if resultado.status == "ignorado":
        typer.echo("Arquivo já processado. Use --force para reprocessar.")

        return

    typer.echo(
        f"{resultado.lidas} lidas, {resultado.validas} válidas, "
        f"{resultado.rejeitadas} rejeitadas, "
        f"{resultado.inseridas} inseridas, {resultado.atualizadas} atualizadas"
    )
