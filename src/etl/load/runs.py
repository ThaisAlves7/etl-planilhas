from etl.load.tables import ingestion_runs
from sqlalchemy.engine import Engine
from sqlalchemy import func, insert, update


def iniciar_execucao(engine: Engine, nome_arquivo: str, arquivo_hash: str) -> int:
    stmt = (
        insert(ingestion_runs)
        .values(nome_arquivo=nome_arquivo, arquivo_hash=arquivo_hash)
        .returning(ingestion_runs.c.id)
    )
    with engine.begin() as conn:
        return conn.execute(stmt).scalar_one()


def finalizar_execucao(
    engine: Engine,
    run_id: int,
    *,
    lidas: int,
    validas: int,
    rejeitadas: int,
    inseridas: int,
    atualizadas: int,
) -> None:
    stmt = (
        update(ingestion_runs)
        .where(ingestion_runs.c.id == run_id)
        .values(
            status="sucesso",
            linhas_lidas=lidas,
            linhas_validas=validas,
            linhas_rejeitadas=rejeitadas,
            linhas_inseridas=inseridas,
            linhas_atualizadas=atualizadas,
            finalizado_em=func.now(),
        )
    )
    with engine.begin() as conn:
        return conn.execute(stmt).scalar_one()


def falhar_execucao():
    return


def ja_processado():
    return
