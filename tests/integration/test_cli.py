from pathlib import Path

from sqlalchemy import func, inspect, select
from typer.testing import CliRunner

from etl.cli import app
from etl.load.tables import ingestion_runs, metadata, vendas

runner = CliRunner()
CONFIG = Path(__file__).parents[2] / "config" / "vendas.yaml"
AMOSTRA = Path(__file__).parents[2] / "data" / "sample" / "vendas_sujos.csv"


def _env(engine):
    return {"DATABASE_URL": engine.url.render_as_string(hide_password=False)}


def _contar(db, tabela):
    with db.begin() as conn:
        return conn.execute(select(func.count()).select_from(tabela)).scalar()


def _rodar(db, *extras):
    return runner.invoke(
        app, ["run", str(AMOSTRA), "--config", str(CONFIG), *extras], env=_env(db)
    )


def test_init_db_cria_as_tabelas(engine):
    metadata.drop_all(engine)

    r = runner.invoke(app, ["init-db"], env=_env(engine))

    assert r.exit_code == 0
    assert {"vendas", "ingestion_runs", "rejected_rows"} <= set(
        inspect(engine).get_table_names()
    )


def test_run_processa_o_arquivo_e_mostra_o_resumo(db):
    r = _rodar(db)

    assert r.exit_code == 0
    assert "200 lidas" in r.output
    assert _contar(db, vendas) == 200


def test_run_ignora_arquivo_ja_processado(db):
    _rodar(db)
    r = _rodar(db)

    assert r.exit_code == 0
    assert "já processado" in r.output
    assert _contar(db, ingestion_runs) == 1


def test_run_com_force_reprocessa_sem_duplicar(db):
    _rodar(db)
    r = _rodar(db, "--force")

    assert r.exit_code == 0
    assert "200 atualizadas" in r.output
    assert _contar(db, vendas) == 200


def test_run_com_arquivo_inexistente_sai_com_erro(db):
    r = runner.invoke(app, ["run", "nao_existe.csv"], env=_env(db))

    assert r.exit_code != 0
