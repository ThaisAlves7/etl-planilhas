from datetime import date
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest

from etl.extract.leitores import ler_csv
from etl.transform.clean import (  # pyright: ignore[reportMissingImports]
    limpar_data,
    limpar_inteiro,
    limpar_nome,
    limpar_pedidos,
    limpar_valor,
    vazio_para_nulo,
)

FORMATOS = ["%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y", "%Y/%m/%d"]

AMOSTRA = Path(__file__).parents[2] / "data" / "sample"


def test_vazio_e_espacos_viram_nulo():
    df = pd.DataFrame({"nome": ["Ana", "", " "]})
    out = vazio_para_nulo(df, ["nome"])
    assert out["nome"].isna().tolist() == [False, True, True]


@pytest.mark.parametrize(
    "texto",
    ["05/03/2026", "05/03/26", "2026/03/05", "2026-03-05"],
)
def test_limpar_data_aceita_os_formatos_conhecidos(texto):
    assert limpar_data(texto, FORMATOS) == date(2026, 3, 5)


@pytest.mark.parametrize("texto", ["32/13/2026", "abc", "", None])
def test_limpar_data_devolve_none_quando_nao_e_data(texto):
    assert limpar_data(texto, FORMATOS) is None


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("R$ 1.234,50", Decimal("1234.50")),
        ("1.234,50", Decimal("1234.50")),
        ("1234,50", Decimal("1234.50")),
        ("R$ 1234,50", Decimal("1234.50")),
        ("19,75", Decimal("19.75")),
        ("1861.56", Decimal("1861.56")),  # como vêm as linhas não sujas
        (" 45.90 ", Decimal("45.90")),
    ],
)
def test_limpar_valor_aceita_os_formatos_conhecidos(texto, esperado):
    assert limpar_valor(texto) == esperado


@pytest.mark.parametrize("texto", ["abc", "R$", "", None, "12,3,4"])
def test_limpar_valor_devolve_none_quando_nao_e_numero(texto):
    assert limpar_valor(texto) is None


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("  maria   silva ", "Maria Silva"),
        ("DANIEL FONSECA", "Daniel Fonseca"),
        ("mArIa sIlVa", "Maria Silva"),
        ("Maria Silva", "Maria Silva"),
    ],
)
def test_limpar_nome_normaliza_espacos_e_caixa(texto, esperado):
    assert limpar_nome(texto) == esperado


@pytest.mark.parametrize("texto", ["", "   ", None])
def test_limpar_nome_devolve_none_quando_nao_ha_nome(texto):
    assert limpar_nome(texto) is None


def test_limpar_nome_usa_title_case_simples():
    # Decisão partículas também recebem inicial maiúscula, igual ao gabarito do gerador
    assert limpar_nome("  maria   silva ") == "Maria Silva"


@pytest.mark.parametrize(
    "texto, esperado",
    [("2", 2), (" 3 ", 3), ("2.5", None), ("abc", None), ("", None), (None, None)],
)
def test_limpar_inteiro(texto, esperado):
    assert limpar_inteiro(texto) == esperado


def test_limpar_pedidos_recupera_o_gabarito():
    sujo = limpar_pedidos(ler_csv(str(AMOSTRA / "vendas_sujos.csv")), FORMATOS)
    limpo = limpar_pedidos(ler_csv(str(AMOSTRA / "vendas_limpos.csv")), FORMATOS)

    pd.testing.assert_frame_equal(sujo, limpo)


def test_limpar_pedidos_aplica_todas_as_regras():
    bruto = pd.DataFrame(
        {
            "numero_pedido": ["1"],
            "data_pedido": ["05/03/26"],
            "cliente_nome": ["  maria   SILVA "],
            "cliente_email": ["ana@example.com"],
            "produto": ["SSD"],
            "quantidade": ["2"],
            "valor_unitario": ["R$ 10,00"],
            "valor_total": ["R$ 20,00"],
        }
    )

    limpo = limpar_pedidos(bruto, formatos_data=FORMATOS)

    assert bruto.loc[0, "data_pedido"] == "05/03/26"  # O bruto continua intacto

    assert limpo.loc[0, "data_pedido"] == date(2026, 3, 5)
    assert limpo.loc[0, "cliente_nome"] == "Maria Silva"
    assert limpo.loc[0, "quantidade"] == 2
    assert limpo.loc[0, "valor_unitario"] == Decimal("10.00")
    assert limpo.loc[0, "valor_total"] == Decimal("20.00")

    assert str(limpo["quantidade"].dtype) == "Int64"
    assert bruto.loc[0, "data_pedido"] == "05/03/26"  # o bruto continua como veio
