from pathlib import Path

from sqlalchemy import select

from etl.config import carregar_config
from etl.load.tables import rejected_rows
from etl.pipeline import executar
from scripts.gerar_dados_faker import (
    gerar_pedidos_limpos,
    injetar_defeitos,
    injetar_rejeitaveis,
    salvar_csv,
)

CFG = carregar_config(str(Path(__file__).parents[2] / "config" / "vendas.yaml"))


def test_pipeline_rejeita_exatamente_o_que_foi_injetado(db, tmp_path):
    limpos = gerar_pedidos_limpos(300)
    com_rejeitaveis, esperadas = injetar_rejeitaveis(limpos)
    sujos, _ = injetar_defeitos(com_rejeitaveis)
    arquivo = tmp_path / "vendas.csv"
    salvar_csv(sujos, str(arquivo))

    executar(str(arquivo), db, CFG)

    with db.begin() as conn:
        linhas = conn.execute(
            select(rejected_rows.c.numero_pedido, rejected_rows.c.motivo_rejeicao)
        ).all()

    detectadas = {(l.numero_pedido, l.motivo_rejeicao) for l in linhas}
    injetadas = {(e["numero_pedido"], e["motivo_rejeicao"]) for e in esperadas}
    assert detectadas == injetadas
