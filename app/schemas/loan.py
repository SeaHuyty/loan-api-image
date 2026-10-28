from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from typing_extensions import Literal

Status = Literal["pending", "approved", "rejected"]


class ApplicationCreate(BaseModel):
    borrower_id: int = Field(..., example=1042)
    amount_usd: int = Field(..., ge=100, le=5000, example=1500)
    term_months: Literal[3, 6, 12, 18, 24] = Field(..., example=12)


class Application(ApplicationCreate):
    id: int
    status: Status
    submitted_at: datetime


class ApplicationPage(BaseModel):
    items: list[Application]
    next_cursor: Optional[str] = None


class StatusUpdate(BaseModel):
    status: Status


class Prediction(BaseModel):
    id: int
    application_id: int
    default_probability: float = Field(..., ge=0, le=1)
    model_version: str
    created_at: datetime


class Error(BaseModel):
    detail: str
