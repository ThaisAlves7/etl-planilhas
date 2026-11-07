from sqlalchemy import select

from etl.load.runs import (
    falhar_execucao,
    finalizar_execucao,
    iniciar_execucao,
    ja_processado,
)
from etl.load.tables import ingestion_runs

CONTADORES = {
    "lidas": 200,
    "validas": 190,
    "rejeitadas": 10,
    "inseridas": 190,
    "atualizadas": 0,
}


def _run(db, run_id):
    with db.begin() as conn:
        return conn.execute(
            select(ingestion_runs).where(ingestion_runs.c.id == run_id)
        ).one()


def test_iniciar_cria_execucao_em_andamento(db):
    run = _run(db, iniciar_execucao(db, "vendas.csv", "abc"))
    assert run.status == "em_andamento"
    assert run.finalizado_em is None


def test_finalizar_grava_contadores_e_encerra(db):
    run_id = iniciar_execucao(db, "vendas.csv", "abc")
    finalizar_execucao(db, run_id, **CONTADORES)
    run = _run(db, run_id)
    assert run.status == "sucesso"
    assert (run.linhas_lidas, run.linhas_rejeitadas, run.linhas_inseridas) == (
        200,
        10,
        190,
    )
    assert run.finalizado_em is not None


def test_falhar_guarda_a_mensagem_e_encerra(db):
    run_id = iniciar_execucao(db, "vendas.csv", "abc")
    falhar_execucao(db, run_id, "arquivo ilegível")
    run = _run(db, run_id)
    assert (run.status, run.mensagem_erro) == ("falha", "arquivo ilegível")
    assert run.finalizado_em is not None


def test_ja_processado_so_considera_execucoes_com_sucesso(db):
    assert not ja_processado(db, "abc")

    run_id = iniciar_execucao(db, "vendas.csv", "abc")
    assert not ja_processado(db, "abc")  # em andamento não conta

    falhar_execucao(db, run_id, "erro")
    assert not ja_processado(db, "abc")  # falha não conta

    segunda = iniciar_execucao(db, "vendas.csv", "abc")
    finalizar_execucao(db, segunda, **CONTADORES)
    assert ja_processado(db, "abc")  # sucesso conta
