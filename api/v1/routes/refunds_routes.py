from ..schema.refunds_schema import RefundInDB, RefundReturnDetail
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from ..crud.refunds_crud import create_refund
from typing import Dict, Any
from utils import validate_developer, validate_user
from redis_db.redis_db import redis_instance


router = APIRouter(tags=["Refunds"], prefix="/api/v1")


@router.post("/refunds", response_model=RefundReturnDetail)
async def request_refund(
    request: Request,
    session: AsyncSession = Depends(get_db),
    validated_developer: Dict[str, Any] = Depends(validate_developer),
    validated_user: Dict[str, Any] = Depends(validate_user),
):
    """Request for refunds"""
    refund = await create_refund(
        request,
        session,
        validated_developer=validated_developer,
        validated_user=validated_user,
    )
    links = {"self": request.url}
    meta = {"status": "success", "message": "Refund request created successfully"}

    return RefundReturnDetail(data=refund, links=links, meta=meta)
