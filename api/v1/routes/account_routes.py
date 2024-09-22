from fastapi import APIRouter, Depends, Request, HTTPException
from db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.background import BackgroundTasks
from ..schema.transaction_schema import (
    ConnectedAccountResponse,
)

from ..crud.account_crud import (
    create_connected_account,
    continue_onboarding,
    login_link,
    delete_connected_account,
)
from utils import validate_developer
from typing import Dict, Any
from db.session import redis_instance

router = APIRouter(tags=["Connected Accounts"], prefix="/api/v1")


@router.post("/connected-accounts", status_code=201)
async def connected_account(
    background_tasks: BackgroundTasks,
    data: Request,
    session: AsyncSession = Depends(get_db),
):
    """create connected accounts"""
    developer_id = None
    client = redis_instance()
    if data.headers.get("X-Developer-Token"):
        if developer_id := client.get(data.headers.get("X-Developer-Token")):
            data_response = await create_connected_account(
                data=data, session=session, validated_developer=developer_id
            )
            onboarding_url = data_response["onboarding_url"]
            del data_response["onboarding_url"]
            links = {
                "self": str(data.url),
                "onboarding_url": onboarding_url,
            }

            meta = {"status_code": 201}

            return ConnectedAccountResponse(links=links, meta=meta, data=data_response)
        else:
            validated_developer = await validate_developer(
                data, background_tasks=background_tasks
            )
            data_response = await create_connected_account(
                data, session, validated_developer
            )
            onboarding_url = data_response["onboarding_url"]
            del data_response["onboarding_url"]
            links = {
                "self": str(data.url),
                "onboarding_url": onboarding_url,
            }

            meta = {"status_code": 201}

            return ConnectedAccountResponse(links=links, meta=meta, data=data_response)
    else:
        return HTTPException(status_code=401, detail="Unauthorized")


@router.post("/connected-accounts/onboarding", status_code=201)
async def connected_account_onboarding(
    background_tasks: BackgroundTasks,
    data: Request,
    session: AsyncSession = Depends(get_db),
):
    """continue onboarding"""
    if data.headers.get("X-Developer-Token"):
        developer_id = redis_instance().get(data.headers.get("X-Developer-Token"))
        if developer_id:
            data_response = await continue_onboarding(data=data, session=session)
            links = {
                "self": str(data.url),
            }

            meta = {"status_code": 201}
            onboarding_url = data_response["onboarding_url"]
            del data_response["onboarding_url"]
            links["onboarding_url"] = onboarding_url
            return ConnectedAccountResponse(links=links, meta=meta, data=data_response)
        else:
            validated_developer = await validate_developer(
                data, background_tasks=background_tasks
            )
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

    else:
        return HTTPException(status_code=401, detail="Unauthorized")


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


@router.delete("/connected-accounts/{id}", status_code=204)
async def connected_accounts_delete(
    id: str,
    data: Request,
    session: AsyncSession = Depends(get_db),
    validated_developer: Dict[str, Any] = Depends(validate_developer),
):
    """delete connected accounts"""
    await delete_connected_account(
        account_id=id,
        data=data,
        session=session,
        validated_developer=validated_developer,
    )
    return HTTPException(status_code=204, detail="Deleted")
