import pandas as pd
from sqlalchemy import insert
from sqlalchemy.engine import Engine

from etl.load.tables import rejected_rows


def gravar_rejeicoes(
    engine: Engine, run_id: int, rejeitadas: pd.DataFrame, bruto: pd.DataFrame
) -> int:
    if rejeitadas.empty:
        return 0

    por_linha = bruto.set_index("linha_origem")
    registros = []

    for r in rejeitadas.itertuples(index=False):
        registros.append(
            {
                "run_id": run_id,
                "linha_origem": int(r.linha_origem),
                "numero_pedido": (
                    None if pd.isna(r.numero_pedido) else str(r.numero_pedido)
                ),
                "motivo_rejeicao": r.motivo_rejeicao,
                "payload": por_linha.loc[r.linha_origem].to_dict(),
            }
        )

    with engine.begin() as conn:
        conn.execute(insert(rejected_rows), registros)

    return len(registros)
