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
    return create_engine(os.environ["DATABASE_URL"])


@app.command("init-db")
def init_db() -> None:
    """Cria as tabelas no banco."""
    engine = _engine()
    metadata.create_all(engine)
    engine.dispose()


@app.command()
def run(
    arquivo: Path = typer.Argument(
        ..., exists=True, dir_okay=False, help="CSV a processar."
    ),
    config: Path = typer.Option(Path("config/vendas.yaml"), "--config", "-c"),
    force: bool = typer.Option(
        False, "--force", help="Reprocessa mesmo que já tenha sido processado."
    ),
) -> None:
    """Processa uma planilha de vendas."""
    cfg = carregar_config(str(config))
    engine = _engine()
    try:
        resultado = executar(str(arquivo), engine, cfg, force=force)
    finally:
        engine.dispose()

    if resultado.status == "ignorado":
        typer.echo("já processado")
        return

    typer.echo(
        f"{resultado.lidas} lidas, {resultado.validas} válidas, "
        f"{resultado.rejeitadas} rejeitadas, "
        f"{resultado.inseridas} inseridas, {resultado.atualizadas} atualizadas"
    )
