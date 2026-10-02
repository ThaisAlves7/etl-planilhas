from scripts.dados_faker import gerar_pedidos_limpos


# class TestGeradorDePedidos:


def test_valor_total_bate_com_quantidade_vezes_unitario():
    for p in gerar_pedidos_limpos(200):
        assert p["valor_total"] == p["quantidade"] * p["valor_unitario"]


def test_numero_pedido_e_unico():
    pedidos = gerar_pedidos_limpos(200)
    assert len(pedidos) == len(set(p["numero_pedido"] for p in pedidos))


def test_data_pedido_e_valida():
    pedidos = gerar_pedidos_limpos(200)
    for p in pedidos:
        assert p["data_pedido"] is not None
