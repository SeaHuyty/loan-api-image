import os
from pathlib import Path

from databases import Database
from sqlalchemy import create_engine

from app.models.loan import borrowers, metadata

# Set DATABASE_URL to a postgresql:// URL to use Postgres (its schema comes from init.sql).
# Without it the API stores everything in a SQLite file in the loan-api folder.
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{Path(__file__).resolve().parent.parent / 'loans.db'}"
IS_SQLITE = DATABASE_URL.startswith("sqlite")

database = Database(DATABASE_URL)

SEED_BORROWERS = [
    {"id": 1042, "name": "Sokha Chan", "province": "Kampong Cham"},
    {"id": 1043, "name": "Dara Phan", "province": "Phnom Penh"},
    {"id": 1044, "name": "Srey Mom", "province": "Siem Reap"},
]


def create_sqlite_schema():
    """Create the tables and the demo borrowers in the SQLite file (Postgres uses init.sql)."""
    engine = create_engine(DATABASE_URL)
    metadata.create_all(engine)
    with engine.begin() as conn:
        for borrower in SEED_BORROWERS:
            if conn.execute(borrowers.select().where(borrowers.c.id == borrower["id"])).first() is None:
                conn.execute(borrowers.insert().values(**borrower))
    engine.dispose()


async def ensure_connected() -> bool:
    if database.is_connected:
        return True
    try:
        if IS_SQLITE:
            create_sqlite_schema()
        await database.connect()
    except Exception:
        return False
    return True
