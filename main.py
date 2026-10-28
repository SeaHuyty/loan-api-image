import json
import logging
import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api import loan
from app.db import database, ensure_connected
from app.services import scoring

logger = logging.getLogger("uvicorn.error")

MODEL_PATH = os.getenv("MODEL_PATH", "model/credit_model.json")

app = FastAPI(
    title="Loan Application Service API",
    version="1.0.0",
    description="Submit and track microfinance loan applications.",
)


@app.on_event("startup")
async def startup():
    with open(MODEL_PATH) as f:
        scoring.load(json.load(f))
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


app.include_router(loan.router, prefix="/api/v1")
