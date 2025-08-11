from app.models import Inventory, Products
from app.schemas.inventory import InventoryResponse
from app.utils.employee import get_active_employee_access
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.schemas.employee import EmployeeAccess
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db


CREATE_BRANCH_ACCESS = ["admin"]

router = APIRouter()


@router.get("/get-inventory-records", response_model=list[InventoryResponse])
async def get_inventory_records(
        branch_id: int,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.role not in CREATE_BRANCH_ACCESS and branch_id not in employee_access.employee_access:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    stmt = await db.scalars(
        select(Inventory)
        .where(Inventory.branch_id == branch_id)
        .options(
            selectinload(Inventory.product).load_only(Products.product_name)
        )
        .order_by(desc(Inventory.updated_at))
    )
    return stmt.all()
