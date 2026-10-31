import os

import pytest
from sqlalchemy import create_engine
from starlette.testclient import TestClient

from app.db import DATABASE_URL, IS_SQLITE
from app.services import scoring
from main import app

AUTH = {"Authorization": "Bearer test-token"}


@pytest.fixture(autouse=True)
def stub_scoring(monkeypatch):
    """CI has no MLflow servers; SCORING_STUB=1 swaps in canned answers."""
    if os.getenv("SCORING_STUB") != "1":
        return

    async def load():
        scoring._version = "stub-v0"

    async def model_version():
        return "stub-v0"

    async def ping():
        return True

    async def score(features):
        return 0.1

    for fn in (load, model_version, ping, score):
        monkeypatch.setattr(scoring, fn.__name__, fn)


@pytest.fixture
def client():
    with TestClient(app) as c:
        c.headers.update(AUTH)
        yield c
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        if IS_SQLITE:
            conn.exec_driver_sql("DELETE FROM predictions")
            conn.exec_driver_sql("DELETE FROM applications")
        else:
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
