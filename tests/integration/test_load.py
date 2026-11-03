from datetime import date
from decimal import Decimal

import pandas as pd
from sqlalchemy import func, select

from etl.load.loader import carregar_vendas  # pyright: ignore[reportMissingImports]
from etl.load.tables import vendas


def _df(valor_total="20.00"):
    return pd.DataFrame(
        {
            "numero_pedido": ["1", "2", "3"],
            "data_pedido": [date(2026, 1, 10)] * 3,
            "cliente_nome": ["Ana Souza", "Bia Lima", "Caio Reis"],
            "cliente_email": ["ana@example.com", "bia@example.com", "caio@example.com"],
            "produto": ["SSD", "Cooler", "Gabinete"],
            "quantidade": pd.array([2, 2, 2], dtype="Int64"),
            "valor_unitario": [Decimal("10.00")] * 3,
            "valor_total": [Decimal(valor_total)] * 3,
        }
    )


def _contar(db):
    with db.begin() as conn:
        return conn.execute(select(func.count()).select_from(vendas)).scalar()


def test_carregar_o_mesmo_arquivo_duas_vezes_nao_duplica(db):
    carregar_vendas(_df(), db)
    carregar_vendas(_df(), db)

    assert _contar(db) == 3


def test_reprocessar_atualiza_a_linha_existente(db):
    carregar_vendas(_df(valor_total="20.00"), db)
    carregar_vendas(_df(valor_total="25.00"), db)

    with db.begin() as conn:
        total = conn.execute(
            select(vendas.c.valor_total).where(vendas.c.numero_pedido == "1")
        ).scalar()

    assert total == Decimal("25.00")


def test_carrega_arquivo_grande_em_lotes(db):
    n = 10_000
    df = pd.DataFrame(
        {
            "numero_pedido": [str(i) for i in range(n)],
            "data_pedido": [date(2026, 1, 10)] * n,
            "cliente_nome": ["Ana Souza"] * n,
            "cliente_email": ["ana@example.com"] * n,
            "produto": ["SSD"] * n,
            "quantidade": pd.array([2] * n, dtype="Int64"),
            "valor_unitario": [Decimal("10.00")] * n,
            "valor_total": [Decimal("20.00")] * n,
        }
    )

    carregar_vendas(df, db)

    assert _contar(db) == n
