from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

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


def limpar_inteiro(texto: str | None) -> int | None:
    """Converte texto em inteiro; devolve None se não houver inteiro."""
    if texto is None or pd.isna(texto):
        return None

    try:
        return int(texto.strip())

    except ValueError:
        return None


def limpar_pedidos(df: pd.DataFrame, formatos_data: list[str]) -> pd.DataFrame:
    df = df.copy()  # O bruto precisa ficar intacto

    # 1) Vazio -> Nulo nas colunas de texto
    df = vazio_para_nulo(
        df, ["numero_pedido", "cliente_nome", "cliente_email", "produto"]
    )

    # 2) Cada coluna recebe sua função de limpeza
    df["data_pedido"] = df["data_pedido"].apply(lambda x: limpar_data(x, formatos_data))
    df["cliente_nome"] = df["cliente_nome"].apply(limpar_nome)
    df["quantidade"] = df["quantidade"].apply(limpar_inteiro).astype("Int64")
    df["valor_unitario"] = df["valor_unitario"].apply(limpar_valor)
    df["valor_total"] = df["valor_total"].apply(limpar_valor)

    return df
