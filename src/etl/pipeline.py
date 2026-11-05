from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.engine import Engine

from etl.extract.arquivo import calcular_hash
from etl.extract.leitores import ler_csv
from etl.load.loader import carregar_vendas
from etl.load.rejeicoes import gravar_rejeicoes
from etl.load.runs import (
    falhar_execucao,
    finalizar_execucao,
    iniciar_execucao,
    ja_processado,
)
from etl.transform.clean import limpar_pedidos
from etl.transform.schema import separar


@dataclass(frozen=True)
class ResultadoExecucao:
    status: str  # "sucesso" ou "ignorado"
    run_id: int | None
    lidas: int = 0
    validas: int = 0
    rejeitadas: int = 0
    inseridas: int = 0
    atualizadas: int = 0


def executar(
    caminho: str,
    engine: Engine,
    formatos_data: list[str],
    *,
    force: bool = False,
) -> ResultadoExecucao:
    arquivo_hash = calcular_hash(caminho)

    if ja_processado(engine, arquivo_hash) and not force:
        return ResultadoExecucao(status="ignorado", run_id=None)

    run_id = iniciar_execucao(engine, Path(caminho).name, arquivo_hash)
    
    try:
        bruto = ler_csv(caminho)
        limpo = limpar_pedidos(bruto, formatos_data)
        validas, rejeitadas = separar(limpo)

        gravar_rejeicoes(engine, run_id, rejeitadas, bruto)
        inseridas, atualizadas = carregar_vendas(validas, engine)

        lidas = len(bruto)
        n_validas = len(validas)
        n_rejeitadas = lidas - n_validas
        finalizar_execucao(
            engine,
            run_id,
            lidas=lidas,
            validas=n_validas,
            rejeitadas=n_rejeitadas,
            inseridas=inseridas,
            atualizadas=atualizadas,
        )
    except Exception as erro:
        mensagem = f"{type(erro).__name__}: {erro}".splitlines()[0][:300]
        falhar_execucao(engine, run_id, mensagem)
        raise

    return ResultadoExecucao(
        status="sucesso",
        run_id=run_id,
        lidas=lidas,
        validas=n_validas,
        rejeitadas=n_rejeitadas,
        inseridas=inseridas,
        atualizadas=atualizadas,
    )
