"""
A última regra é a mais interessante, porque é uma validação entre colunas
e o pandera resolve bem com checks no nível do DataFrame.

Agora o desafio para você: escreva scripts/gerar_dados_sujos.py com o
Faker (locale pt_BR), gerando uns 500 pedidos e salvando em CSV
(vendas_sujo.csv, encoding latin-1, separador ;) e em Excel
(vendas_sujo.xlsx). Injete estes problemas, cada um em uma pequena
porcentagem das linhas:

Datas em formatos misturados (2026-03-05, 05/03/2026, 5/3/26)
Valores com vírgula decimal e R$ na frente ("R$ 1.234,50")
Espaços sobrando e caixa bagunçada nos nomes (" maRIA silva ")
Pedidos duplicados (mesmo numero_pedido, às vezes com valor diferente)
Nulos em campos obrigatórios e e-mails inválidos
valor_total que não bate com quantidade × unitário
Quantidade negativa ou zero
No Excel: 2 linhas de título antes do cabeçalho e uma segunda aba com lixo

Uma dica de design: use uma seed fixa (Faker.seed(42), random.seed(42))
para que os dados sejam reproduzíveis, e guarde num dicionário quantos
defeitos de cada tipo você injetou. Mais adiante vamos comparar isso com
o que o pipeline detectou, e esse é o teste mais convincente de que a
validação funciona.

"""

import random
from faker import Faker
import pandas as pd
import csv
from decimal import ROUND_HALF_UP, Decimal

fake = Faker("pt_BR")
fake_unique = fake.unique
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


def gerar_dados_sujos(num_registros: int = 500) -> None:

    with open(
        "data/sample/vendas_sujo.csv",
        mode="w",
        newline="",
        encoding="latin-1",
    ) as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(headers)

        for _ in range(num_registros):
            # Gerar número do pedido de UNIQUE (chave única)
            numero_pedido = fake_unique.numerify(text="#######")

            data_pedido = fake.date_between(start_date="-2y", end_date="today")

            nome = fake.name()
            cliente_nome = " ".join(nome.split()).title()

            cliente_email = fake.email().lower()

            produto = fake.word().capitalize()

            quantidade = random.randint(1, 20)

            valor_float = round(random.uniform(5.00, 500.00), 2)
            valor_unitario = Decimal(str(valor_float)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            valor_total = (Decimal(quantidade) * valor_unitario).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            writer.writerow(
                [
                    numero_pedido,
                    data_pedido.strftime("%Y-%m-%d"),
                    cliente_nome,
                    cliente_email,
                    produto,
                    quantidade,
                    f"{valor_unitario:.2f}",
                    f"{valor_total:.2f}",
                ]
            )

        print("Arquivo 'vendas_sujo.csv' gerado com sucesso")


if __name__ == "__main__":
    gerar_dados_sujos(20)
