import logging
import os

import httpx

logger = logging.getLogger("uvicorn.error")

SCORING_URL = os.getenv("SCORING_URL", "http://127.0.0.1:5001")
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "loan-default")
MODEL_ALIAS = os.getenv("MODEL_ALIAS", "champion")
MODEL_VERSION = os.getenv("MODEL_VERSION")  # set when there is no registry (hosted deploy)

FEATURES = ["amount_usd", "term_months", "monthly_income_usd", "previous_loans", "late_payments"]

_version = None


class ScoringUnavailable(Exception):
    pass


async def load():
    """Look up which registry version the alias points to (the scoring server serves that model)."""
    global _version
    if MODEL_VERSION:
        _version = MODEL_VERSION
        return
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(
                f"{TRACKING_URI}/api/2.0/mlflow/registered-models/alias",
                params={"name": MODEL_NAME, "alias": MODEL_ALIAS},
            )
            r.raise_for_status()
        _version = f"{MODEL_ALIAS}-v{r.json()['model_version']['version']}"
    except (httpx.HTTPError, KeyError) as exc:
        _version = None
        logger.warning("Could not read %s@%s from %s: %s", MODEL_NAME, MODEL_ALIAS, TRACKING_URI, exc)


async def model_version() -> str:
    if _version is None:
        await load()
    if _version is None:
        raise ScoringUnavailable("Model registry unavailable")
    return _version


async def ping() -> bool:
    """Is the MLflow scoring server answering?"""
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            return (await client.get(f"{SCORING_URL}/ping")).status_code == 200
    except httpx.HTTPError:
        return False


async def score(features: dict) -> float:
    """Probability of default from the MLflow scoring server."""
    body = {"dataframe_split": {"columns": FEATURES, "data": [[features[f] for f in FEATURES]]}}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(f"{SCORING_URL}/invocations", json=body)
            r.raise_for_status()
        return round(r.json()["predictions"][0][1], 4)  # column 1 = probability of default
    except (httpx.HTTPError, KeyError, IndexError) as exc:
        raise ScoringUnavailable(f"Scoring server error: {exc}") from exc
