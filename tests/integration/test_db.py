import os

from sqlalchemy import create_engine, text


def test_conecta_no_postgres():
    engine = create_engine(os.environ["DATABASE_URL"])
    with engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1
