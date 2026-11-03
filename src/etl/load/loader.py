import pandas as pd

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine

from etl.load.tables import vendas

TAMANHO_LOTE = 1000


def carregar_vendas(df: pd.DataFrame, engine: Engine) -> None:
    registros = df[[c.name for c in vendas.columns]].to_dict("records")
    if not registros:
        return

    with engine.begin() as conn:
        for i in range(0, len(registros), TAMANHO_LOTE):
            lote = registros[i : i + TAMANHO_LOTE]

            stmt = insert(vendas).values(lote)
            stmt = stmt.on_conflict_do_update(
                index_elements=["numero_pedido"],
                set_={
                    c.name: stmt.excluded[c.name]
                    for c in vendas.columns
                    if not c.primary_key
                },
            )

            conn.execute(stmt)
