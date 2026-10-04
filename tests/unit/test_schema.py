from datetime import date
from decimal import Decimal

import pandas as pd

from etl.transform.schema import separar


def _df_exemplo() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "numero_pedido": ["1", "2", "3"],
            "data_pedido": [date(2026, 1, 10)] * 3,
            "cliente_nome": ["Ana Souza", "Bia Lima", "Caio Reis"],
            "cliente_email": ["ana@example.com", "bia#example.com", "caio@example.com"],
            "produto": ["SSD", "Cooler", "Gabinete"],
            "quantidade": [2, 1, 0],
            "valor_unitario": [Decimal("10.00"), Decimal("5.00"), Decimal("7.00")],
            "valor_total": [Decimal("20.00"), Decimal("5.00"), Decimal("99.00")],
        }
    )


def test_separar_divide_validas_e_rejeitadas():
    validas, rejeitadas = separar(_df_exemplo())

    assert list(validas["numero_pedido"]) == ["1"]

    pares = set(
        zip(
            rejeitadas["numero_pedido"],
            rejeitadas["motivo_rejeicao"],
        )
    )
    assert pares == {
        ("2", "email_invalido"),
        ("3", "quantidade_invalida"),
        ("3", "total_inconsistente"),
    }
