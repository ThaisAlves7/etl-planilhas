from datetime import date, timedelta
import csv

from scripts.gerar_dados_faker import gerar_pedidos_limpos
from scripts.gerar_dados_faker import salvar_csv, salvar_xlsx


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
