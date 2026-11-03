import pandas as pd

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine

from etl.load.tables import vendas


def carregar_vendas(df: pd.DataFrame, engine: Engine) -> None:
    registros = df[[c.name for c in vendas.columns]].to_dict("records")
    if not registros:
        return

    stmt = insert(vendas).values(registros)
    stmt = stmt.on_conflict_do_update(
        index_elements=["numero_pedido"],
        set_={
            c.name: stmt.excluded[c.name] for c in vendas.columns if not c.primary_key
        },
    )

    with engine.begin() as conn:
        conn.execute(stmt)
