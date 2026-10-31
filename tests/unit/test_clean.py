from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

from etl.transform.clean import (  # pyright: ignore[reportMissingImports]
    vazio_para_nulo,
    limpar_data,
    limpar_valor,
)

FORMATOS = ["%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y", "%Y/%m/%d"]


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
