from etl.load.tables import ingestion_runs, rejected_rows, vendas


def test_vendas_tem_numero_pedido_como_chave():
    assert [c.name for c in vendas.primary_key.columns] == ["numero_pedido"]


def test_finalizado_em_fica_nulo_ate_o_fim_da_execucao():
    assert ingestion_runs.c.finalizado_em.nullable is True


def test_rejeicao_sempre_pertence_a_uma_execucao():
    assert rejected_rows.c.run_id.nullable is False


def test_linha_origem_e_inteiro():
    assert rejected_rows.c.linha_origem.type.python_type is int
