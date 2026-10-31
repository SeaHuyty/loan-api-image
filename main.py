import logging
import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api import loan
from app.db import database, ensure_connected
from app.services import scoring

logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="Loan Application Service API",
    version="1.0.0",
    description="Submit and track microfinance loan applications.",
)


@app.on_event("startup")
async def startup():
    await scoring.load()
    if not await ensure_connected():
        logger.warning(
            "Database not connected (set DATABASE_URL); data endpoints return 503"
        )


@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    # Error schema in loan-api.yaml is {"detail": "<string>"}
    message = "; ".join(
        f"{'.'.join(str(p) for p in e['loc'] if p != 'body')}: {e['msg']}"
        for e in exc.errors()
    )
    return JSONResponse(status_code=422, content={"detail": message})


@app.get("/live", tags=["health"], summary="Process is up (no dependencies checked)")
async def live():
    return {"status": "ok"}


@app.get("/health", tags=["health"], summary="Service health")
async def health():
    database_ok = await ensure_connected()
    scoring_ok = await scoring.ping()
    try:
        version = await scoring.model_version()
    except scoring.ScoringUnavailable:
        version = None
    ok = database_ok and scoring_ok and version is not None
    return JSONResponse(
        status_code=200 if ok else 503,
        content={
            "status": "ok" if ok else "degraded",
            "database": database_ok,
            "scoring_server": scoring_ok,
            "model_version": version,
            "commit": os.getenv("RENDER_GIT_COMMIT"),  # set by Render; lets the pipeline see what is live
        },
    )


app.include_router(loan.router, prefix="/api/v1")