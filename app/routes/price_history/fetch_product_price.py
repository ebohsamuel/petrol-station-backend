from fastapi import APIRouter, Depends, status, HTTPException
from app.models import PriceHistory
from app.crud.product import get_product_by_id
from app.utils.employee import get_active_employee_access
from app.schemas.employee import EmployeeAccess
from app.schemas.price_history import PriceHistoryResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db


GENERAL_EMPLOYEE_ACCESS = ["employee"]

router = APIRouter()


@router.get("/get-price-history", response_model=list[PriceHistoryResponse])
async def get_price_history(
        product_id: int,
        limit: int = 10,
        offset: int = 0,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.employee not in GENERAL_EMPLOYEE_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    product = await get_product_by_id(id=product_id, db=db)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    stmt = await db.scalars(
        select(PriceHistory)
        .where(PriceHistory.product_id == product_id)
        .limit(limit)
        .offset(offset)
        .order_by(desc(PriceHistory.created_at))
    )

    price_history = stmt.all()

    return price_history


@router.get("/get-product-latest-price")
async def get_product_latest_price(
        product_id: int,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.employee not in GENERAL_EMPLOYEE_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    product = await get_product_by_id(id=product_id, db=db)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"latest_price": product.latest_price}
