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


def ler_excel(
    caminho: str,
    nome_aba: str,
    linhas_antes_do_cabecalho: int = 0,
) -> pd.DataFrame:

    df = pd.read_excel(
        caminho,
        sheet_name=nome_aba,
        header=linhas_antes_do_cabecalho,
        dtype=str,
        keep_default_na=False,
    )
    df["linha_origem"] = df.index + linhas_antes_do_cabecalho + 2

    return df
