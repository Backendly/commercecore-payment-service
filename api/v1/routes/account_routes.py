from fastapi import APIRouter, Depends, Request
from db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..schema.transaction_schema import (
    ConnectedAccountResponse,
)
from ..crud.account_crud import (
    create_connected_account,
    continue_onboarding,
    login_link,
)
from utils import validate_developer
from typing import Dict, Any


router = APIRouter(tags=["Connected Accounts"], prefix="/api/v1")


@router.post("/connected-accounts", status_code=201)
async def connected_account(
    data: Request,
    session: AsyncSession = Depends(get_db),
    validated_developer: Dict[str, Any] = Depends(validate_developer),
):
    """create connected accounts"""
    data_response = await create_connected_account(
        data=data, session=session, validated_developer=validated_developer
    )
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
    data: Request,
    session: AsyncSession = Depends(get_db),
    validated_developer: Dict[str, Any] = Depends(validate_developer),
):
    """continue onboarding"""
    data_response = await continue_onboarding(
        data=data, session=session, validated_developer=validated_developer
    )
    links = {
        "self": str(data.url),
    }

    meta = {"status_code": 201}
    onboarding_url = data_response["onboarding_url"]
    del data_response["onboarding_url"]
    links["onboarding_url"] = onboarding_url
    return ConnectedAccountResponse(links=links, meta=meta, data=data_response)


@router.post("/connected-accounts/login", status_code=201)
async def connected_account_login(
    data: Request,
    session: AsyncSession = Depends(get_db),
    validated_developer: Dict[str, Any] = Depends(validate_developer),
):
    """login link"""
    data_response = await login_link(
        data=data, session=session, validated_developer=validate_developer
    )
    links = {
        "self": str(data.url),
    }

    meta = {"status_code": 201}
    return ConnectedAccountResponse(links=links, meta=meta, data=data_response)
