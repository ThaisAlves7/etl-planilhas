from pathlib import Path

import pytest
from sqlalchemy import func, select

from etl.load.tables import ingestion_runs, rejected_rows, vendas
from etl.pipeline import executar

AMOSTRA = Path(__file__).parents[2] / "data" / "sample" / "vendas_sujos.csv"
FORMATOS = ["%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y", "%Y/%m/%d"]


def _contar(db, tabela):
    with db.begin() as conn:
        return conn.execute(select(func.count()).select_from(tabela)).scalar()


def test_primeira_execucao_carrega_o_arquivo_sujo_inteiro(db):
    r = executar(str(AMOSTRA), db, FORMATOS)

    assert r.status == "sucesso"
    assert (r.lidas, r.validas, r.rejeitadas) == (200, 200, 0)
    assert (r.inseridas, r.atualizadas) == (200, 0)
    assert _contar(db, vendas) == 200


def test_segunda_execucao_do_mesmo_arquivo_e_ignorada(db):
    executar(str(AMOSTRA), db, FORMATOS)
    r = executar(str(AMOSTRA), db, FORMATOS)

    assert r.status == "ignorado"
    assert _contar(db, vendas) == 200
    assert _contar(db, ingestion_runs) == 1  # nem registrou execução nova


def test_force_reprocessa_sem_duplicar(db):
    executar(str(AMOSTRA), db, FORMATOS)
    r = executar(str(AMOSTRA), db, FORMATOS, force=True)

    assert (r.inseridas, r.atualizadas) == (0, 200)
    assert _contar(db, vendas) == 200
    assert _contar(db, ingestion_runs) == 2


CSV_COM_ERROS = (
    "numero_pedido;data_pedido;cliente_nome;cliente_email;produto;quantidade;valor_unitario;valor_total\n"
    "1;2026-01-10;Ana Souza;ana@example.com;SSD;2;10.00;20.00\n"
    "2;2026-01-10;Bia Lima;bia#example.com;Cooler;1;5.00;5.00\n"
    "3;32/13/2026;Caio Reis;caio@example.com;Gabinete;1;7.00;7.00\n"
)


def test_linhas_invalidas_vao_para_a_quarentena(db, tmp_path):
    arquivo = tmp_path / "com_erros.csv"
    arquivo.write_text(CSV_COM_ERROS, encoding="latin-1")

    r = executar(str(arquivo), db, FORMATOS)

    assert (r.lidas, r.validas, r.rejeitadas, r.inseridas) == (3, 1, 2, 1)
    assert r.validas + r.rejeitadas == r.lidas
    assert _contar(db, vendas) == 1
    assert _contar(db, rejected_rows) == 2
    with db.begin() as conn:
        payload = conn.execute(
            select(rejected_rows.c.payload).where(rejected_rows.c.linha_origem == 4)
        ).scalar()
    assert payload["data_pedido"] == "32/13/2026"  # o texto como veio


def test_falha_registra_a_execucao_e_repassa_o_erro(db, tmp_path):
    arquivo = tmp_path / "quebrado.csv"
    arquivo.write_text("numero_pedido;produto\n1;SSD\n", encoding="latin-1")

    with pytest.raises(KeyError):
        executar(str(arquivo), db, FORMATOS)

    with db.begin() as conn:
        run = conn.execute(select(ingestion_runs)).one()
    assert run.status == "falha"
    assert run.mensagem_erro
    assert run.finalizado_em is not None
