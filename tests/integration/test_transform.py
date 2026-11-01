from pathlib import Path

import pytest

from etl.extract.leitores import ler_csv
from etl.transform.clean import limpar_pedidos
from etl.transform.schema import separar

AMOSTRA = Path(__file__).parents[2] / "data" / "sample"
FORMATOS = ["%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y", "%Y/%m/%d"]


def test_csv_sujo_passa_por_clean_e_schema_sem_rejeicoes():
    bruto = ler_csv(str(AMOSTRA / "vendas_sujos.csv"))

    validas, rejeitadas = separar(limpar_pedidos(bruto, FORMATOS))

    assert len(validas) == 200
    assert rejeitadas.empty


@pytest.mark.parametrize(
    "coluna, valor_ruim",
    [
        ("quantidade", ""),
        ("data_pedido", "32/13/2026"),
        ("valor_unitario", "abc"),
    ],
)
def test_dado_irrecuperavel_e_rejeitado_sem_derrubar_o_pipeline(coluna, valor_ruim):
    bruto = ler_csv(str(AMOSTRA / "vendas_limpos.csv")).head(3).copy()
    bruto.loc[0, coluna] = valor_ruim

    validas, rejeitadas = separar(limpar_pedidos(bruto, FORMATOS))

    assert len(validas) == 2
    assert bruto.loc[0, "numero_pedido"] in set(rejeitadas["numero_pedido"])
    assert "campo_obrigatorio_ausente" in set(rejeitadas["motivo_rejeicao"])
