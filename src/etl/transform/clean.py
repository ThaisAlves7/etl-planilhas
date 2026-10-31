import pandas as pd


def vazio_para_nulo(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    df = df.copy()

    for col in colunas:
        df[col] = df[col].str.strip().replace("", pd.NA)

    return df
