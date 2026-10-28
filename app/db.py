import os

from databases import Database

# No default credentials: the real URL is supplied at runtime. Without it the
# API still starts (so /docs works) and data endpoints answer 503.
DATABASE_URL = os.getenv("DATABASE_URL")

database = Database(DATABASE_URL or "postgresql://localhost:5432/loans")


async def ensure_connected() -> bool:
    if database.is_connected:
        return True
    if not DATABASE_URL:
        return False
    try:
        await database.connect()
    except Exception:
        return False
    return True
