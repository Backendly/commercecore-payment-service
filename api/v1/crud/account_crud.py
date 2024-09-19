from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from services.stripe_config import stripe
from fastapi import Request, HTTPException, Depends
from datetime import datetime
from utils import validate_developer
from typing import Dict
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
    validated_developer: Dict[str, Any] | None = None,
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

    return {"login_url": login_link.url}
