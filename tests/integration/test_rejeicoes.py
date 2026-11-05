import pandas as pd
from sqlalchemy import select

from etl.load.rejeicoes import gravar_rejeicoes
from etl.load.runs import iniciar_execucao
from etl.load.tables import rejected_rows


def _bruto():
    return pd.DataFrame(
        {
            "numero_pedido": ["1", "2"],
            "data_pedido": ["05/03/26", "32/13/2026"],
            "quantidade": ["2", "3"],
            "linha_origem": [2, 3],
        }
    )


def _ler_rejeicoes(db):
    with db.begin() as conn:
        return conn.execute(select(rejected_rows).order_by(rejected_rows.c.id)).all()


def test_grava_motivo_linha_e_texto_original(db):
    run_id = iniciar_execucao(db, "vendas.csv", "abc")
    rejeitadas = pd.DataFrame(
        {
            "linha_origem": [3, 3],
            "numero_pedido": ["2", "2"],
            "motivo_rejeicao": ["campo_obrigatorio_ausente", "total_inconsistente"],
        }
    )

    assert gravar_rejeicoes(db, run_id, rejeitadas, _bruto()) == 2

    linhas = _ler_rejeicoes(db)
    assert [l.motivo_rejeicao for l in linhas] == [
        "campo_obrigatorio_ausente",
        "total_inconsistente",
    ]
    assert all(l.run_id == run_id and l.linha_origem == 3 for l in linhas)
    assert linhas[0].payload["data_pedido"] == "32/13/2026"  # o texto como veio


def test_numero_pedido_ausente_vira_nulo(db):
    run_id = iniciar_execucao(db, "vendas.csv", "abc")
    rejeitadas = pd.DataFrame(
        {
            "linha_origem": [2],
            "numero_pedido": [pd.NA],
            "motivo_rejeicao": ["campo_obrigatorio_ausente"],
        }
    )

    gravar_rejeicoes(db, run_id, rejeitadas, _bruto())

    assert _ler_rejeicoes(db)[0].numero_pedido is None


def test_sem_rejeicoes_nao_grava_nada(db):
    run_id = iniciar_execucao(db, "vendas.csv", "abc")
    vazia = pd.DataFrame(columns=["linha_origem", "numero_pedido", "motivo_rejeicao"])

    assert gravar_rejeicoes(db, run_id, vazia, _bruto()) == 0
    assert _ler_rejeicoes(db) == []
