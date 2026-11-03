import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from etl.load.tables import metadata

BANCO_TESTE = "vendas_test"


@pytest.fixture(scope="session")
def engine():
    url = make_url(os.environ["DATABASE_URL"])

    # conecta no banco administrativo só para criar o banco de testes
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        existe = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :nome"),
            {"nome": BANCO_TESTE},
        ).scalar()
        if not existe:
            conn.execute(text(f"CREATE DATABASE {BANCO_TESTE}"))
    admin.dispose()

    eng = create_engine(url.set(database=BANCO_TESTE))
    metadata.drop_all(eng)
    metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def db(engine):
    # Entrega o engine com as tabelas vazias a cada teste
    with engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE vendas, rejected_rows, ingestion_runs RESTART IDENTITY CASCADE"
            )
        )
    return engine
