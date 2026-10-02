import random
from faker import Faker
import pandas as pd
import csv
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
            "valor_unitario": Decimal(valor_unitario).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
            "valor_total": Decimal(valor_total).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
        }

        pedidos.append(pedido)

    return pedidos


def injetar_defeitos(pedidos: list[dict]) -> tuple[list[dict], dict[str, int]]:
    """Recebe os pedidos limpos, devolve (pedidos_sujos, contagem_de_defeitos). Sem I/O."""


def salvar_csv(pedidos: list[dict], caminho: str) -> None:
    """Só escreve. Latin-1, separador ';'."""


def salvar_xlsx(pedidos: list[dict], caminho: str) -> None:
    """Só escreve. Título extra + segunda aba com lixo."""


def main() -> None:
    limpos = gerar_pedidos_limpos(500)
    sujos, defeitos = injetar_defeitos(limpos)

    salvar_csv(sujos, "data/sample/vendas_sujo.csv")
    salvar_xlsx(sujos, "data/sample/vendas_sujo.xlsx")

    print(defeitos)
