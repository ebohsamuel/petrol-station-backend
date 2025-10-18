from app.models import StockDelivery, Products, Branch
from app.schemas.stock_delivery import StockDeliveryResponse
from app.utils.employee import get_active_employee_access
from fastapi import APIRouter, Depends, status, HTTPException
from datetime import date
from sqlalchemy.orm import selectinload
from sqlalchemy import select, desc, and_, or_, func
from app.schemas.employee import EmployeeAccess
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

CREATE_BRANCH_ACCESS = {"admin"}

router = APIRouter()


@router.get("/get-stock-delivery-records", response_model=list[StockDeliveryResponse])
async def get_stock_delivery_records(
        limit: int = 10,
        last_id: int | None = None,
        last_supplied_date: date | None = None,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.role not in CREATE_BRANCH_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    query = (
        select(StockDelivery)
        .options(
            selectinload(StockDelivery.product).load_only(Products.product_name),
            selectinload(StockDelivery.branch).load_only(Branch.name)
        )
        .order_by(desc(StockDelivery.supplied_date), desc(StockDelivery.id))
        .limit(limit)
    )

    if last_id and last_supplied_date:
        query = query.where(
            or_(
                StockDelivery.supplied_date < last_supplied_date,
                and_(
                    StockDelivery.supplied_date == last_supplied_date,
                    StockDelivery.id < last_id
                )
            )
        )

    stmt = await db.scalars(query)
    return stmt.all()


@router.get("/get-total-delivery-record")
async def total_delivery_record(
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.role not in CREATE_BRANCH_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    stmt = await db.scalar(select(func.count(StockDelivery.id)))

    return {"detail": stmt}
