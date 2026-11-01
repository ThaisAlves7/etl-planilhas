from pathlib import Path

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
