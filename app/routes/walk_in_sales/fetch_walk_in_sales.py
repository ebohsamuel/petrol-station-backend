from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from app.schemas.walk_in_sales import WalkInSalesResponse
from app.schemas.employee import EmployeeAccess
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Sale, Products
from app.database import get_db
from app.utils.employee import get_active_employee_access
from fastapi import APIRouter, Depends, status, HTTPException
from datetime import datetime


CREATE_BRANCH_ACCESS = {"admin"}

router = APIRouter()


@router.get("/get-walk-in-sales-records", response_model=list[WalkInSalesResponse])
async def get_walk_in_sales_records(
        branch_id: int,
        limit: int = 10,
        last_id: int | None = None,
        last_sales_time: datetime | None = None,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    # check if the employee is admin, and if not, we check if the employee has a branch access
    if employee_access.role not in CREATE_BRANCH_ACCESS:
        if branch_id not in employee_access.employee_access:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    query = (
        select(Sale)
        .where(Sale.branch_id == branch_id)
        .options(
            selectinload(Sale.product).load_only(Products.product_name)
        )
        .limit(limit)
        .order_by(desc(Sale.sales_time), desc(Sale.id))
    )

    if last_id and last_sales_time:
        query = query.where(
            or_(
                Sale.sales_time < last_sales_time,
                and_(
                    Sale.sales_time == last_sales_time,
                    Sale.id < last_id
                )
            )
        )

    stmt = await db.scalars(query)

    return stmt.all()


@router.get("/get-total-walk-in-sales-records")
async def get_total_walk_in_sales_records(
        branch_id: int,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    # check if the employee is admin, and if not, we check if the employee has a branch access
    if employee_access.role not in CREATE_BRANCH_ACCESS:
        if branch_id not in employee_access.employee_access:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    total_count = await db.scalar(select(func.count()).where(Sale.branch_id == branch_id))

    return {"detail": total_count}
