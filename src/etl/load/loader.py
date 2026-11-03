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
            "data_pedido": stmt.excluded["data_pedido"],
            "cliente_nome": stmt.excluded["cliente_nome"],
            "cliente_email": stmt.excluded["cliente_email"],
            "produto": stmt.excluded["produto"],
            "quantidade": stmt.excluded["quantidade"],
            "valor_unitario": stmt.excluded["valor_unitario"],
            "valor_total": stmt.excluded["valor_total"],
        },
    )

    with engine.begin() as conn:
        conn.execute(stmt)
