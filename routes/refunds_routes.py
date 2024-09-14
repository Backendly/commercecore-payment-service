from schema.refunds_schema import RefundInDB, RefundReturnDetail
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from crud.refunds_crud import create_refund


router = APIRouter(tags=["Refunds"], prefix="/api/v1")


@router.post("/refunds", response_model=RefundReturnDetail)
async def request_refund(request: Request, session: AsyncSession = Depends(get_db)):
    """Request for refunds"""
    refund = await create_refund(request, session)
    links = {"self": request.url}
    meta = {"status": "success", "message": "Refund request created successfully"}

    return RefundReturnDetail(refund=refund, links=links, meta=meta)
