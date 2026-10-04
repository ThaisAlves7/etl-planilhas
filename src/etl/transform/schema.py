from datetime import date
from decimal import Decimal

import pandas as pd
import pandera.pandas as pa
from pandera.errors import SchemaErrors


MOTIVOS = {"not_nullable": "campo_obrigatorio_ausente"}

REGEX_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

schema = pa.DataFrameSchema(
    {
        "numero_pedido": pa.Column(str, nullable=False, unique=True),
        "data_pedido": pa.Column(
            date,
            nullable=False,
            checks=pa.Check(
                lambda s: s <= date.today(),
                name="data_futura",
            ),
        ),
        "cliente_nome": pa.Column(
            str,
            nullable=False,
        ),
        "cliente_email": pa.Column(
            str,
            nullable=False,
            checks=pa.Check(
                lambda s: s.str.match(REGEX_EMAIL),
                name="email_invalido",
            ),
        ),
        "produto": pa.Column(
            str,
            nullable=False,
        ),
        "quantidade": pa.Column(
            int,
            pa.Check(
                lambda s: s > 0,
                name="quantidade_invalida",
            ),
        ),
        "valor_unitario": pa.Column(
            object,
            nullable=False,
            checks=pa.Check(
                lambda s: s > 0,
                name="valor_unitario_invalido",
            ),
        ),
        "valor_total": pa.Column(
            object,
            nullable=False,
        ),
    },
    checks=pa.Check(
        lambda df: df["valor_total"] == df["quantidade"] * df["valor_unitario"],
        name="total_inconsistente",
    ),
)


def separar(df):
    # # Devolve (validas, rejeitadas)
    try:
        schema.validate(df, lazy=True)

        return (
            df,
            pd.DataFrame(columns=["numero_pedido", "motivo_rejeicao"]),
        )

    except SchemaErrors as e:
        falhas = e.failure_cases

    estruturais = falhas[falhas["index"].isna()]
    if not estruturais.empty:
        raise ValueError(f"Problema estrutural nos dados:\n{estruturais}")

    pares = falhas[["index", "check"]].drop_duplicates().astype({"index": int})
    pares["motivo_rejeicao"] = pares["check"].map(lambda c: MOTIVOS.get(c, c))
    pares["numero_pedido"] = df.loc[pares["index"], "numero_pedido"].to_numpy()

    rejeitadas = pares[["numero_pedido", "motivo_rejeicao"]].reset_index(drop=True)
    validas = df[~df.index.isin(pares["index"])]

    return validas, rejeitadas
