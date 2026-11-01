from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import pandas as pd


def vazio_para_nulo(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    df = df.copy()

    for col in colunas:
        df[col] = df[col].str.strip().replace("", pd.NA)

    return df


def limpar_data(texto: str, formatos: list[str]) -> date | None:
    """Converter texto em date tentando cada formato, na ordem recebida"""
    if texto is None or pd.isna(texto):
        return None

    texto = texto.strip()

    for formato in formatos:
        try:

            return datetime.strptime(texto, formato).date()

        except ValueError:
            continue

    return None


def limpar_valor(texto: str | None) -> Decimal | None:
    """Converte texto monetário (com ou sem 'R$') em Decimal com 2 casas."""
    if texto is None or pd.isna(texto):
        return None

    valor = texto.replace("R$", "").strip()

    if "," in valor:
        # Formato brasileiro: ponto é milhar, virgula é decimal
        valor = valor.replace(".", "").replace(",", ".")

    # Sem virgula: o ponto (se houver) jé é o separador decimal

    try:

        return Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    except InvalidOperation:
        return None


def limpar_nome(texto: str | None) -> str | None:
    """Normaliza espaços e caixa do nome; devolve None se não houver nome."""
    if texto is None or pd.isna(texto) or not isinstance(texto, str):
        return None

    nome = " ".join(texto.split()).title()

    return nome or None

"""
PS D:\GitHub\etl-planilhas> docker compose run --rm app pytest -q tests/unit/test_clean.py
[+] run 1/1
 ✔ Container etl-planilhas-db-1 Running                                              0.0s
Container etl-planilhas-db-1 Waiting
Container etl-planilhas-db-1 Healthy
Container etl-planilhas-app-run-165eb2b4dde1 Creating
Container etl-planilhas-app-run-165eb2b4dde1 Created
............................                                                      [100%]
28 passed in 0.81s

"""