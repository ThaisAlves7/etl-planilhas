from datetime import date, datetime

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
