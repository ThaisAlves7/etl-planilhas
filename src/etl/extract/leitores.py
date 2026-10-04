import pandas as pd


def ler_csv(
    caminho: str,
    delimitador: str = ";",
    encoding: str = "latin-1",
) -> pd.DataFrame:
    df = pd.read_csv(
        caminho,
        sep=delimitador,
        encoding=encoding,
        dtype=str,  # tudo como texto: a limpeza converte depois
        keep_default_na=False,  # vazio chega como "", não como NaN
    )

    df["linha_origem"] = df.index + 2  # índice 0 = linha 2 (a linha 1 é o cabeçalho)
    return df
