from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    Table,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB

metadata = MetaData()

vendas = Table(
    "vendas",
    metadata,
    Column("numero_pedido", Text, primary_key=True),
    Column("data_pedido", Date, nullable=False),
    Column("cliente_nome", Text, nullable=False),
    Column("cliente_email", Text, nullable=False),
    Column("produto", Text, nullable=False),
    Column("quantidade", Integer, nullable=False),
    Column("valor_unitario", Numeric(10, 2), nullable=False),
    Column("valor_total", Numeric(10, 2), nullable=False),
    # Regras no banco de dados para validação do preenchimento
    CheckConstraint("quantidade > 0", name="ck_vendas_quantidade"),
    CheckConstraint("valor_unitario > 0", name="ck_vendas_valor_unitario"),
)

ingestion_runs = Table(
    "ingestion_runs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("nome_arquivo", Text, nullable=False),
    Column("arquivo_hash", Text, nullable=False, index=True),
    Column("status", Text, nullable=False, server_default="em_andamento"),
    Column("linhas_lidas", Integer, nullable=False, server_default=text("0")),
    Column("linhas_validas", Integer, nullable=False, server_default=text("0")),
    Column("linhas_rejeitadas", Integer, nullable=False, server_default=text("0")),
    Column("linhas_inseridas", Integer, nullable=False, server_default=text("0")),
    Column("linhas_atualizadas", Integer, nullable=False, server_default=text("0")),
    Column("mensagem_erro", Text),  # Preenchida quando status = 'falha'
    Column(
        "iniciado_em",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    ),
    Column("finalizado_em", DateTime(timezone=True)),
    CheckConstraint(
        "status IN ('em_andamento', 'sucesso', 'falha')", name="ck_runs_status"
    ),
)

rejected_rows = Table(
    "rejected_rows",
    metadata,
    Column("id", Integer, primary_key=True),
    # Ligação da Foreign Key
    Column(
        "run_id",
        Integer,
        ForeignKey("ingestion_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("linha_origem", Integer, nullable=False),
    Column("numero_pedido", Text),
    Column("motivo_rejeicao", Text, nullable=False, index=True),
    Column("payload", JSONB, nullable=False),
    Column(
        "criado_em",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    ),
)
