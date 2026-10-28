from typing import List, Optional

from app.db import database
from app.services import scoring
from app.models.loan import applications, borrowers, predictions


async def borrower_exists(borrower_id: int) -> bool:
    query = borrowers.select().where(borrowers.c.id == borrower_id)
    return await database.fetch_one(query) is not None


async def list_applications(
    status: Optional[str], province: Optional[str], limit: int, after: Optional[int]
) -> List[dict]:
    query = applications.select()
    if province is not None:
        query = query.where(
            applications.c.borrower_id.in_(
                borrowers.select().with_only_columns([borrowers.c.id]).where(
                    borrowers.c.province == province
                )
            )
        )
    if status is not None:
        query = query.where(applications.c.status == status)
    if after is not None:
        query = query.where(applications.c.id > after)
    query = query.order_by(applications.c.id).limit(limit)
    return await database.fetch_all(query)


async def list_for_borrower(borrower_id: int):
    query = (
        applications.select()
        .where(applications.c.borrower_id == borrower_id)
        .order_by(applications.c.id)
    )
    return await database.fetch_all(query)


async def get_application(application_id: int):
    query = applications.select().where(applications.c.id == application_id)
    return await database.fetch_one(query)


async def create_application(borrower_id: int, amount_usd: int, term_months: int):
    query = applications.insert().values(
        borrower_id=borrower_id, amount_usd=amount_usd, term_months=term_months
    )
    application_id = await database.execute(query)
    return await get_application(application_id)


async def update_status(application_id: int, status: str):
    query = (
        applications.update()
        .where(applications.c.id == application_id)
        .values(status=status)
    )
    await database.execute(query)
    return await get_application(application_id)


async def create_prediction(application) -> dict:
    probability = scoring.score(application["amount_usd"], application["term_months"])
    query = predictions.insert().values(
        application_id=application["id"],
        default_probability=probability,
        model_version=scoring.model_version(),
    )
    prediction_id = await database.execute(query)
    return await database.fetch_one(
        predictions.select().where(predictions.c.id == prediction_id)
    )
