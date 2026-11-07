from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

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
            "linha_origem": [2, 3, 4],
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


@pytest.mark.parametrize(
    "campo, valor, motivo",
    [
        ("data_pedido", date(2999, 1, 1), "data_futura"),
        ("valor_unitario", Decimal("0.0"), "valor_unitario_invalido"),
        ("quantidade", -1, "quantidade_invalida"),
    ],
)
def test_cada_regra_rejeitada_com_o_motivo_certo(campo, valor, motivo):
    df = _df_exemplo().iloc[[0]].copy()  # pedido 1, válido
    df[campo] = valor
    _, rejeitadas = separar(df)
    assert motivo in set(rejeitadas["motivo_rejeicao"])


def test_rejeitadas_trazem_a_linha_de_origem():
    _, rejeitadas = separar(_df_exemplo())

    linhas = dict(zip(rejeitadas["numero_pedido"], rejeitadas["linha_origem"]))
    assert linhas["2"] == 3  # o pedido "2" está na linha 3 da planilha


def test_numero_pedido_repetido_e_rejeitado_com_motivo_proprio():
    base = _df_exemplo().iloc[[0]]
    df = pd.concat([base, base], ignore_index=True)

    _, rejeitadas = separar(df)

    assert set(rejeitadas["motivo_rejeicao"]) == {"numero_pedido_repetido"}
    assert len(rejeitadas) == 2  # as duas ocorrências
