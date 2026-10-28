import pytest
from sqlalchemy import create_engine
from starlette.testclient import TestClient

from app.db import DATABASE_URL
from main import app

AUTH = {"Authorization": "Bearer test-token"}


@pytest.fixture
def client():
    with TestClient(app) as c:
        c.headers.update(AUTH)
        yield c
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.exec_driver_sql("TRUNCATE predictions, applications RESTART IDENTITY CASCADE")
    engine.dispose()


@pytest.fixture
def make_application(client):
    def _make(**overrides):
        body = {"borrower_id": 1042, "amount_usd": 1500, "term_months": 12, **overrides}
        r = client.post("/api/v1/applications", json=body)
        assert r.status_code == 201, r.text
        return r.json()

    return _make
