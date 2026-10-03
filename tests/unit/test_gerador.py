import pytest

import csv
import datetime
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from scripts.gerar_dados_faker import (
    gerar_pedidos_limpos,
    injetar_defeitos,
    salvar_csv,
    salvar_xlsx,
    FORMATOS_DATA_SUJA,
)


def _ler_data_suja(texto: str):
    for formato in FORMATOS_DATA_SUJA:

        try:
            return datetime.datetime.strptime(texto, formato).date()

        except ValueError:
            continue

    return None


def _ler_valor_sujo(texto: str) -> Decimal:
    texto = texto.replace("R$", "").strip()
    texto = texto.replace(".", "").replace(",", ".")

    return Decimal(texto).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _limpar_nome(texto: str) -> str:
    return " ".join(texto.split()).title()


def test_valor_total_bate_com_quantidade_vezes_unitario():
    for p in gerar_pedidos_limpos(200):
        assert p["valor_total"] == p["quantidade"] * p["valor_unitario"]


def test_numero_pedido_e_unico():
    pedidos = gerar_pedidos_limpos(200)
    assert len(pedidos) == len(set(p["numero_pedido"] for p in pedidos))


def test_data_pedido_nao_e_futura_e_esta_na_janela():
    hoje = date.today()

    for p in gerar_pedidos_limpos(200):
        assert isinstance(p["data_pedido"], date)
        assert hoje - timedelta(days=366 * 2) <= p["data_pedido"] <= hoje


def test_salvar_pedidos_limpos(tmp_path):
    pedidos = gerar_pedidos_limpos(200)
    caminho = tmp_path / "vendas_limpos.csv"

    salvar_csv(pedidos, caminho)

    with open(caminho, "r", newline="", encoding="latin-1") as f:
        linhas = list(
            csv.DictReader(f, delimiter=";"),
        )

    assert len(linhas) == len(pedidos)
    assert linhas[0]["numero_pedido"] == pedidos[0]["numero_pedido"]
    assert linhas[0]["cliente_nome"] == pedidos[0]["cliente_nome"]


@pytest.mark.parametrize("seed", range(20))
def test_datas_sujas_sao_recuperaveis_e_contagem_bate(seed):
    limpos = gerar_pedidos_limpos(200)
    sujos, contagem = injetar_defeitos(limpos, seed=seed)

    qtde_sujas = 0

    for limpo, sujo in zip(limpos, sujos):
        if isinstance(sujo["data_pedido"], str):
            qtde_sujas += 1

            assert _ler_data_suja(sujo["data_pedido"]) == limpo["data_pedido"]

    assert qtde_sujas == contagem["data_formato_misto"]


def test_valores_sujos_sao_recuperaveis_e_contagem_bate():
    limpos = gerar_pedidos_limpos(200)
    sujos, contagem = injetar_defeitos(limpos)

    qtde_sujas = 0

    for limpo, sujo in zip(limpos, sujos):
        if isinstance(sujo["valor_unitario"], str):
            qtde_sujas += 1

            assert _ler_valor_sujo(sujo["valor_unitario"]) == limpo["valor_unitario"]
            assert _ler_valor_sujo(sujo["valor_total"]) == limpo["valor_total"]

    assert qtde_sujas == contagem["valor_com_rs_virgula"]


def test_nomes_sujos_sao_recuperaveis_e_contagem_bate():
    limpos = gerar_pedidos_limpos(200)
    sujos, contagem = injetar_defeitos(limpos)

    qtde_sujas = 0
    for limpo, sujo in zip(limpos, sujos):
        if sujo["cliente_nome"] != limpo["cliente_nome"]:
            qtde_sujas += 1

            assert _limpar_nome(sujo["cliente_nome"]) == limpo["cliente_nome"]

    assert qtde_sujas == contagem["nome_sujo"]


def test_injetar_defeitos_e_reprodutivel():
    limpos = gerar_pedidos_limpos(100)

    assert injetar_defeitos(limpos, seed=1) == injetar_defeitos(limpos, seed=1)
