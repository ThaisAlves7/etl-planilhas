from etl.load.tables import ingestion_runs
from sqlalchemy.engine import Engine
from sqlalchemy import func, insert, select, update


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
        conn.execute(stmt)


def falhar_execucao(engine: Engine, run_id: int, mensagem_erro: str) -> None:
    stmt = (
        update(ingestion_runs)
        .where(ingestion_runs.c.id == run_id)
        .values(status="falha", mensagem_erro=mensagem_erro, finalizado_em=func.now())
    )
    with engine.begin() as conn:
        return conn.execute(stmt)


def ja_processado(engine: Engine, arquivo_hash: str) -> bool:
    stmt = (
        select(ingestion_runs.c.id)
        .where(
            ingestion_runs.c.arquivo_hash == arquivo_hash,
            ingestion_runs.c.status == "sucesso",
        )
        .limit(1)
    )
    with engine.begin() as conn:
        return conn.execute(stmt).first() is not None
