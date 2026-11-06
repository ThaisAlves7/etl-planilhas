import pandas as pd
from sqlalchemy import literal_column
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine

from etl.load.tables import vendas

TAMANHO_LOTE = 1000


def carregar_vendas(df: pd.DataFrame, engine: Engine) -> tuple[int, int]:
    duplicados = df["numero_pedido"][df["numero_pedido"].duplicated()]
    if not duplicados.empty:
        exemplos = ", ".join(duplicados.unique()[:5])
        raise ValueError(f"numero_pedido repetido no arquivo: {exemplos}")

    registros = df[[c.name for c in vendas.columns]].to_dict("records")
    if not registros:
        return 0, 0

    inseridas = 0
    atualizadas = 0

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
            ).returning(literal_column("(xmax = 0)").label("inserida"))

            linhas = conn.execute(stmt).all()
            novas = sum(1 for linha in linhas if linha.inserida)

            inseridas += novas
            atualizadas += len(linhas) - novas

    return inseridas, atualizadas
