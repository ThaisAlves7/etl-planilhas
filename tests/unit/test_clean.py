import pandas as pd
import pytest
from datetime import date

from etl.transform.clean import vazio_para_nulo, limpar_data

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