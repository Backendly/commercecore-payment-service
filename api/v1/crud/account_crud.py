from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from services.stripe_config import stripe
from fastapi import Request, HTTPException, Depends
from datetime import datetime
from typing import Dict
from db.session import redis_instance
import os


async def create_connected_account(
    data: Request,
    session: AsyncSession,
    validated_developer: Dict[str, Any],
):
    """Creates a connected account"""
    data = await data.json()
    developer_id = (
        validated_developer["developer_id"]
        if type(validated_developer) == dict
        else validated_developer
    )
    email = data["email"]
    public_key = os.getenv("STRIPE_PUBLIC_KEY")

    try:
        account = stripe.Account.create(
            country="US",
            email=email,
            controller={
                "fees": {"payer": "application"},
                "losses": {"payments": "application"},
                "stripe_dashboard": {"type": "express"},
            },
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
                "bank_transfer_payments": {"requested": True},
                "link_payments": {"requested": True},
            },
            metadata={"developer_id": developer_id},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the connected account.{e}",
        )

    full_onboard_url = stripe.AccountLink.create(
        account=account["id"],
        refresh_url="http://localhost:8000",
        return_url="http://localhost:8000",
        type="account_onboarding",
    )

    timestamp = datetime.fromtimestamp(full_onboard_url["expires_at"])
    date = f"{timestamp.hour}"
    return {
        "onboarding_url": full_onboard_url.url,
        "account_id": account["id"],
        "public_key": public_key,
        "message": f"Connected account created successfully onboarding link expires in {date} hours"
        f" use the 'onboarding_url' to complete the onboarding",
    }


async def continue_onboarding(
    data: Request,
    session: AsyncSession,
    validated_developer: Dict[str, Any] | str | None,
):
    """Continues the onboarding process"""
    data_collected = await data.json()
    account_id = data_collected.get("account_id")
    try:
        onboarding = stripe.AccountLink.create(
            account=account_id,
            refresh_url="http://localhost:8000",
            return_url="http://localhost:8000",
            type="account_onboarding",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the onboarding link.{e}",
        )

    timestamp = datetime.fromtimestamp(onboarding["expires_at"])
    date = f"{timestamp.hour}"
    return {
        "onboarding_url": onboarding.url,
        "message": f"Onboarding link expires in {date} hours use the"
        f" 'onboarding_url' to complete the onboarding",
    }


async def login_link(
    data: Request, session: AsyncSession, validated_developer: Dict[str, Any]
):
    """Creates a login link"""
    data = await data.json()
    account_id = data["account_id"]

    try:
        login_link = stripe.Account.create_login_link(account=account_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the login link.{e}",
        )
    redis_instance().set("account_id", account_id)
    return {"login_url": login_link.url}


async def delete_connected_account(
    account_id: str,
    data: Request,
    session: AsyncSession,
    validated_developer: Dict[str, Any],
):
    developer_id = (
        validated_developer.get("developer_id")
        if type(validated_developer) == dict
        else validated_developer
    )
    account = stripe.Account.retrieve(account_id)
    if (
        not account.get("metadata")
        or account["metadata"].get("developer_id") != developer_id
    ):
        raise HTTPException(status_code=401, detail="Not the Owner of account")

    stripe.Account.delete(account_id)


async def get_connected_account(
    account_id: str,
    data: Request,
    session: AsyncSession,
    validated_developer: Dict[str, Any],
):
    developer_id = (
        validated_developer.get("developer_id")
        if type(validated_developer) == dict
        else validated_developer
    )
    account = stripe.Account.retrieve(account_id)
    if (
        not account.get("metadata")
        or account["metadata"].get("developer_id") != developer_id
    ):
        raise HTTPException(status_code=401, detail="Not the Owner of account")
    return {
        "account_id": account_id,
        "metadata": account["metadata"],
        "email": account["email"],
        "capabilities": account["capabilities"],
        "created": account["created"],
        "dashboard_name": account["settings"]["dashboard"]["display_name"],
    }
