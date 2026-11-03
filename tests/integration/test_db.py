import os

from sqlalchemy import create_engine, text

from etl.load.tables import metadata


def test_conecta_no_postgres():
    engine = create_engine(os.environ["DATABASE_URL"])
    with engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_tabelas_do_pipeline_existem():
    assert {"vendas", "ingestion_runs", "rejected_rows"} <= set(metadata.tables)
