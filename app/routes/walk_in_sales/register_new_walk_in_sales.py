from sqlalchemy import select, and_
from app.schemas.walk_in_sales import WalkInSalesCreate
from app.schemas.employee import EmployeeAccess
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Sale, Inventory
from app.database import get_db
from app.utils.employee import get_active_employee_access
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import SQLAlchemyError


CREATE_BRANCH_ACCESS = ["admin"]

router = APIRouter()


@router.post("/register-new-walk-in-sales")
async def register_new_walk_in_sales(
        walk_in_sale: WalkInSalesCreate,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.role not in CREATE_BRANCH_ACCESS:
        if walk_in_sale.branch_id not in employee_access.employee_access:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    # check if the product and branch id combination is in the inventory table
    inventory_check = await db.scalar(
        select(Inventory)
        .where(
            and_(
                Inventory.product_id == walk_in_sale.product_id,
                Inventory.branch_id == walk_in_sale.branch_id
            )
        )
    )
    if not inventory_check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="product not in the inventory of the branch")

    if inventory_check.quantity < walk_in_sale.quantity:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="stock level not sufficient to complete the transaction"
        )

    inventory_check.quantity -= walk_in_sale.quantity

    walk_in_sale.employee_id = employee_access.employeeId
    sale_record = Sale(**walk_in_sale.model_dump(exclude_none=True))
    db.add(sale_record)
    try:
        await db.commit()
        return {"detail": "walk in sales record entered successfully"}
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
    except ValueError as e:
        await db.rollback()
        raise
