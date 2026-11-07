from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import func, select

from etl.config import ConfigFonte, carregar_config
from etl.load.tables import ingestion_runs, rejected_rows, vendas
from etl.pipeline import executar

CONFIG = Path(__file__).parents[2] / "config" / "vendas.yaml"
CFG = carregar_config(str(CONFIG))

AMOSTRA = Path(__file__).parents[2] / "data" / "sample" / "vendas_sujos.csv"


def _contar(db, tabela):
    with db.begin() as conn:
        return conn.execute(select(func.count()).select_from(tabela)).scalar()


def test_primeira_execucao_carrega_o_arquivo_sujo_inteiro(db):
    r = executar(str(AMOSTRA), db, CFG)

    assert r.status == "sucesso"
    assert (r.lidas, r.validas, r.rejeitadas) == (200, 200, 0)
    assert (r.inseridas, r.atualizadas) == (200, 0)
    assert _contar(db, vendas) == 200


def test_segunda_execucao_do_mesmo_arquivo_e_ignorada(db):
    executar(str(AMOSTRA), db, CFG)
    r = executar(str(AMOSTRA), db, CFG)

    assert r.status == "ignorado"
    assert _contar(db, vendas) == 200
    assert _contar(db, ingestion_runs) == 1  # nem registrou execução nova


def test_force_reprocessa_sem_duplicar(db):
    executar(str(AMOSTRA), db, CFG)
    r = executar(str(AMOSTRA), db, CFG, force=True)

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

    r = executar(str(arquivo), db, CFG)

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
        executar(str(arquivo), db, CFG)

    with db.begin() as conn:
        run = conn.execute(select(ingestion_runs)).one()
    assert run.status == "falha"
    assert run.mensagem_erro
    assert run.finalizado_em is not None


def test_usa_encoding_e_delimitador_da_configuracao(db, tmp_path):
    arquivo = tmp_path / "utf8.csv"
    arquivo.write_text(
        "numero_pedido,data_pedido,cliente_nome,cliente_email,produto,quantidade,valor_unitario,valor_total\n"
        "1,2026-01-10,José Ângelo,jose@example.com,SSD,2,10.00,20.00\n",
        encoding="utf-8",
    )
    cfg = ConfigFonte(
        encoding="utf-8", delimitador=",", formatos_data=CFG.formatos_data
    )

    r = executar(str(arquivo), db, cfg)

    assert r.inseridas == 1
    with db.begin() as conn:
        nome = conn.execute(select(vendas.c.cliente_nome)).scalar()
    assert nome == "José Ângelo"


def test_executar_le_planilha_excel(db, tmp_path):
    arquivo = tmp_path / "vendas.xlsx"
    cabecalho = [
        "numero_pedido",
        "data_pedido",
        "cliente_nome",
        "cliente_email",
        "produto",
        "quantidade",
        "valor_unitario",
        "valor_total",
    ]
    linhas = [
        ["Relatório de vendas"] + [None] * 7,
        ["gerado hoje"] + [None] * 7,
        cabecalho,
        [
            "1",
            datetime(2026, 1, 10),
            "Ana Souza",
            "ana@example.com",
            "SSD",
            2,
            10.0,
            20.0,
        ],
    ]
    
    with pd.ExcelWriter(arquivo) as xl:
        pd.DataFrame(linhas).to_excel(
            xl, sheet_name="Vendas", header=False, index=False
        )
        pd.DataFrame([["lixo"]]).to_excel(
            xl, sheet_name="Outra", header=False, index=False
        )

    cfg = ConfigFonte(
        formatos_data=[*CFG.formatos_data, "%Y-%m-%d %H:%M:%S"],
        nome_aba="Vendas",
        linhas_antes_do_cabecalho=2,
    )

    r = executar(str(arquivo), db, cfg)

    assert (r.lidas, r.inseridas) == (1, 1)
