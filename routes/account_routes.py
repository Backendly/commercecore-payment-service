from fastapi import APIRouter, Depends, Request
from db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from schema.transaction_schema import (
    ConnectedAccountResponse,
)
from crud.transaction_crud import (
    create_connected_account,
    continue_onboarding,
)


router = APIRouter(tags=["Connected Accounts"], prefix="/api/v1")


@router.post("/connected-accounts", status_code=201)
async def connected_account(data: Request, session: AsyncSession = Depends(get_db)):
    """create connected accounts"""
    data_response = await create_connected_account(data=data, session=session)
    onboarding_url = data_response["onboarding_url"]
    del data_response["onboarding_url"]
    links = {
        "self": str(data.url),
        "onboarding_url": onboarding_url,
    }

    meta = {"status_code": 201}

    return ConnectedAccountResponse(links=links, meta=meta, data=data_response)


@router.post("/connected-accounts/onboarding", status_code=201)
async def connected_account_onboarding(
    data: Request, session: AsyncSession = Depends(get_db)
):
    """continue onboarding"""
    data_response = await continue_onboarding(data=data, session=session)
    links = {
        "self": str(data.url),
    }

    meta = {"status_code": 201}

    return ConnectedAccountResponse(links=links, meta=meta, data=data_response)
