import random
import pandas as pd
import csv
import copy

from faker import Faker
from decimal import ROUND_HALF_UP, Decimal

fake = Faker("pt_BR")
Faker.seed(42)
random.seed(42)

fake_unique = fake.unique.numerify(text="#######")

headers = [
    "numero_pedido",
    "data_pedido",
    "cliente_nome",
    "cliente_email",
    "produto",
    "quantidade",
    "valor_unitario",
    "valor_total",
]

produtos = [
    "Placa de vídeo",
    "Memória RAM",
    "Processador",
    "Disco rígido",
    "Gabinete",
    "Fonte",
    "Cooler",
    "SSD",
    "Placa mãe",
]

FORMATOS_DATA_SUJA = [
    "%d/%m/%Y",
    "%d/%m/%y",
    "%Y/%m/%d",
    # "%m/%d/%Y",
]

FORMATOS_VALOR_SUJO = [
    ("R$ ", True),  # R$ 1.234,50
    ("", True),  # 1.234,50
    ("", False),  # 1234,50
    ("R$ ", False),  # R$ 1234,50
]

FORMATOS_NOME_SUJO = [
    "lower",  # maria silva
    "upper",  # MARIA SILVA
    "caixa_alternada",  # mArIa sIlVa,
    "espacos_sobrando",  # Maria   Silva,
]

DEFEITOS = {
    "data_formato_misto": 0.05,
    "valor_com_rs_virgula": 0.10,
    "nome_sujo": 0.15,
}


def gerar_pedidos_limpos(n: int) -> list[dict]:
    """Devolve n pedidos válidos. Sem I/O."""
    pedidos = []

    for _ in range(n):

        nome = fake.name()
        numero_pedido = fake.unique.numerify(text="#######")

        quantidade = random.randint(1, 20)
        valor_float = round(random.uniform(5.00, 500.00), 2)
        valor_unitario = Decimal(str(valor_float)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        valor_total = (Decimal(quantidade) * valor_unitario).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        pedido = {
            "numero_pedido": numero_pedido,
            "data_pedido": fake.date_between(start_date="-2y", end_date="today"),
            "cliente_nome": " ".join(nome.split()).title(),
            "cliente_email": fake.email().lower(),
            "produto": random.choice(produtos),
            "quantidade": quantidade,
            "valor_unitario": valor_unitario,
            "valor_total": valor_total,
        }

        pedidos.append(pedido)

    return pedidos


def _sujar_data(pedido: dict, rng: random.Random) -> str:
    formato = rng.choice(FORMATOS_DATA_SUJA)
    pedido["data_pedido"] = pedido["data_pedido"].strftime(formato)


def _formatar_brl(valor: Decimal, com_milhar: bool) -> str:
    if com_milhar:
        texto = f"{valor:,.2f}"
        return texto.replace(",", "X").replace(".", ",").replace("X", ".")  # 1,234.50

    return f"{valor:.2f}".replace(".", ",")  # 1234,50


def _sujar_valor(pedido: dict, rng: random.Random) -> None:
    prefixo, com_milhar = rng.choice(FORMATOS_VALOR_SUJO)

    for campo in ("valor_unitario", "valor_total"):
        pedido[campo] = prefixo + _formatar_brl(pedido[campo], com_milhar)


def _sujar_nome(pedido: dict, rng: random.Random) -> None:
    nome = pedido["cliente_nome"]
    formato = rng.choice(FORMATOS_NOME_SUJO)

    if formato == "lower":
        nome = nome.lower()

    elif formato == "upper":
        nome = nome.upper()

    elif formato == "caixa_alternada":
        nome = "".join(
            letra.upper() if rng.random() < 0.5 else letra.lower() for letra in nome
        )

    elif formato == "espacos_sobrando":
        separador = " " * rng.randint(2, 4)
        nome = (
            " " * rng.randint(1, 2)
            + separador.join(nome.split())
            + " " * rng.randint(0, 2)
        )

    pedido["cliente_nome"] = nome


APLICADORES = {
    "data_formato_misto": _sujar_data,
    "valor_com_rs_virgula": _sujar_valor,
    "nome_sujo": _sujar_nome,
}


def injetar_defeitos(
    pedidos: list[dict],
    seed: int = 42,
):
    rng = random.Random(seed)
    sujos = copy.deepcopy(pedidos)
    contagem: dict[str, int] = {}

    indices = list(range(len(sujos)))
    rng.shuffle(indices)
    inicio = 0

    # Obter os defeitos a serem usados para "sujar" os dados
    for nome, fracao in DEFEITOS.items():
        k = round(len(sujos) * fracao)
        bloco = indices[inicio : inicio + k]
        inicio += k

        # Chamar a função que vai realizar o "sujeira" dos dados
        aplicar = APLICADORES[nome]
        for i in bloco:
            aplicar(sujos[i], rng)

        contagem[nome] = len(bloco)

    return sujos, contagem


def salvar_csv(pedidos: list[dict], caminho: str) -> None:
    """Só escreve. Latin-1, separador ';'."""
    with open(caminho, "w", newline="", encoding="latin-1") as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter=";")
        writer.writeheader()
        writer.writerows(pedidos)


def main() -> None:
    limpos = gerar_pedidos_limpos(200)
    sujos, defeitos = injetar_defeitos(limpos)

    salvar_csv(limpos, "data/sample/vendas_limpos.csv")
    salvar_csv(sujos, "data/sample/vendas_sujos.csv")

    print(defeitos)


if __name__ == "__main__":
    main()
