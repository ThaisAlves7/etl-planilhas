from decimal import Decimal

import pandas as pd
import pandera.pandas as pa
from pandera.errors import SchemaErrors

REGEX_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

schema = pa.DataFrameSchema(
    {
        "numero_pedido": pa.Column(str, nullable=False, unique=True),
        "cliente_email": pa.Column(
            str,
            nullable=False,
            checks=pa.Check(lambda s: s.str.match(REGEX_EMAIL), name="email_invalido"),
        ),
        "quantidade": pa.Column(
            int, pa.Check(lambda s: s > 0, name="quantidade_invalida")
        ),
        "valor_unitario": pa.Column(object, nullable=False),
        "valor_total": pa.Column(object, nullable=False),
    },
    checks=pa.Check(
        lambda df: df["valor_total"] == df["quantidade"] * df["valor_unitario"],
        name="total_inconsistente",
    ),
)

df = pd.DataFrame(
    {
        "numero_pedido": ["", "2", "3"],
        "cliente_email": [None, "bia@example.com", "bia#example.com"],
        "quantidade": [2, 0, 0],
        "valor_unitario": [Decimal("10.00"), Decimal("7.00"), Decimal("7.00")],
        "valor_total": [None, Decimal("99.00"), Decimal("99.00")],
    }
)

try:
    schema.validate(df, lazy=True)
    print("tudo válido\n")

except SchemaErrors as e:
    falhas = e.failure_cases
    por_linha = falhas[["index", "check"]].drop_duplicates().sort_values("index")

    print(por_linha)
