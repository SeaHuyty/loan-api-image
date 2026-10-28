from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    MetaData,
    func,
)

metadata = MetaData()

borrowers = Table(
    "borrowers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("province", String(100), nullable=False),
)

applications = Table(
    "applications",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("borrower_id", Integer, ForeignKey("borrowers.id"), nullable=False),
    Column("amount_usd", Integer, nullable=False),
    Column("term_months", Integer, nullable=False),
    Column("status", String(20), nullable=False, server_default="pending"),
    Column("submitted_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)

predictions = Table(
    "predictions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("application_id", Integer, ForeignKey("applications.id"), nullable=False),
    Column("default_probability", Float, nullable=False),
    Column("model_version", String(20), nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)
