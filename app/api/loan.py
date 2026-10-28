from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.loan import (
    Application,
    ApplicationCreate,
    ApplicationPage,
    Error,
    Prediction,
    Status,
    StatusUpdate,
)
from app.db import ensure_connected
from app.services import loan as service

bearer = HTTPBearer(auto_error=False)


def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
):
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication information is missing or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_db():
    if not await ensure_connected():
        raise HTTPException(status_code=503, detail="Database unavailable")


router = APIRouter(dependencies=[Depends(require_auth), Depends(require_db)])

UNAUTHORIZED = {401: {"model": Error, "description": "Authentication information is missing or invalid"}}


@router.get(
    "/applications",
    response_model=ApplicationPage,
    summary="List applications",
    tags=["applications"],
    responses={**UNAUTHORIZED},
)
async def list_applications(
    status: Optional[Status] = Query(None, description="Filter applications by their current status"),
    province: Optional[str] = Query(None, description="Filter applications by the borrower's province", example="Kampong Cham"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return per page"),
    after: Optional[int] = Query(None, description="Cursor for pagination indicating the last seen item ID", example="7781"),
):
    rows = await service.list_applications(status, province, limit + 1, after)
    page = rows[:limit]
    next_cursor = str(page[-1]["id"]) if len(rows) > limit else None
    return {"items": page, "next_cursor": next_cursor}


@router.post(
    "/applications",
    response_model=Application,
    status_code=201,
    summary="Submit a loan application",
    tags=["applications"],
    responses={**UNAUTHORIZED, 422: {"model": Error, "description": "The values break a business rule"}},
)
async def create_application(
    payload: ApplicationCreate, request: Request, response: Response
):
    if not await service.borrower_exists(payload.borrower_id):
        raise HTTPException(status_code=422, detail="borrower_id does not match any borrower")
    application = await service.create_application(**payload.dict())
    response.headers["Location"] = request.url_for(
        "get_application", application_id=application["id"]
    )
    return application


@router.get(
    "/applications/{application_id}",
    response_model=Application,
    summary="Get one application",
    tags=["applications"],
    responses={**UNAUTHORIZED, 404: {"model": Error, "description": "No application found with this identifier"}},
)
async def get_application(application_id: int = Path(..., description="Unique identifier of the loan application")):
    application = await service.get_application(application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.patch(
    "/applications/{application_id}",
    response_model=Application,
    summary="Update application status",
    tags=["applications"],
    responses={
        **UNAUTHORIZED,
        404: {"model": Error, "description": "No application found with this identifier"},
        409: {"model": Error, "description": "Application has already been decided and cannot be modified"},
        422: {"model": Error, "description": "Invalid status transition or business rule violation"},
    },
)
async def update_application_status(
    payload: StatusUpdate,
    application_id: int = Path(..., description="Unique identifier of the loan application to update"),
):
    application = await service.get_application(application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    if application["status"] != "pending":
        raise HTTPException(status_code=409, detail="Application has already been decided")
    if payload.status == "pending":
        raise HTTPException(status_code=422, detail="Application can only move from pending to approved or rejected")
    return await service.update_status(application_id, payload.status)


@router.get(
    "/borrowers/{borrower_id}/applications",
    response_model=List[Application],
    summary="List applications for a specific borrower",
    tags=["borrowers", "applications"],
    responses={**UNAUTHORIZED, 404: {"model": Error, "description": "No borrower found with this identifier"}},
)
async def list_borrower_applications(
    borrower_id: int = Path(..., description="Unique identifier of the borrower"),
):
    if not await service.borrower_exists(borrower_id):
        raise HTTPException(status_code=404, detail="Borrower not found")
    return await service.list_for_borrower(borrower_id)


@router.post(
    "/applications/{application_id}/predictions",
    response_model=Prediction,
    status_code=201,
    summary="Create a prediction for an application",
    tags=["predictions", "applications"],
    responses={**UNAUTHORIZED, 404: {"model": Error, "description": "No application found with this identifier"}},
)
async def create_prediction(
    application_id: int = Path(..., description="Unique identifier of the loan application to score"),
):
    application = await service.get_application(application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return await service.create_prediction(application)
