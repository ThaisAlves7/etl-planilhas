from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from etl.load.tables import ingestion_runs, rejected_rows, vendas


def _vendas(**alteracoes):
    base = {
        "numero_pedido": "1",
        "data_pedido": date(2026, 1, 10),
        "cliente_nome": "Ana Souza",
        "cliente_email": "ana@example.com",
        "produto": "SSD",
        "quantidade": 2,
        "valor_unitario": Decimal("10.00"),
        "valor_total": Decimal("20.00"),
    }
    return {**base, **alteracoes}


def test_vendas_valida_e_gravando(db):
    with db.begin() as conn:
        conn.execute(vendas.insert().values(**_vendas()))
        assert conn.execute(select(func.count()).select_from(vendas)).scalar() == 1


@pytest.mark.parametrize(
    "alteracao",
    [{"quantidade": 0}, {"valor_unitario": Decimal("0")}, {"cliente_nome": None}],
)
def test_banco_recusa_venda_invalida(db, alteracao):
    with pytest.raises(IntegrityError):
        with db.begin() as conn:
            conn.execute(vendas.insert().values(**_vendas(**alteracao)))


def test_banco_recusa_status_invalido(db):
    with pytest.raises(IntegrityError):
        with db.begin() as conn:
            conn.execute(
                ingestion_runs.insert().values(
                    nome_arquivo="a.csv", arquivo_hash="abc", status="sucess"
                )
            )


def test_banco_recusa_rejeicao_sem_execucao(db):
    with pytest.raises(IntegrityError):
        with db.begin() as conn:
            conn.execute(
                rejected_rows.insert().values(
                    linha_origem=2, motivo_rejeicao="email_invalido", payload={}
                )
            )
