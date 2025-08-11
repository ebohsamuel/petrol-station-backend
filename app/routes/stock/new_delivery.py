from sqlalchemy.exc import SQLAlchemyError
from app.models import StockDelivery, Inventory
from app.schemas.stock_delivery import StockDeliveryCreate
from app.schemas.inventory import InventoryCreate
from app.utils.employee import get_active_employee_access
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, and_
from app.schemas.employee import EmployeeAccess
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db


CREATE_BRANCH_ACCESS = ["admin"]

router = APIRouter()


@router.post("/register-new-delivery")
async def register_new_delivery(
        deliveries: list[StockDeliveryCreate],
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.role not in CREATE_BRANCH_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    for data in deliveries:
        # create a class object of the stock delivery table
        delivery = StockDelivery(**data.model_dump())
        db.add(delivery)

        # check if the product and branch id combination is in the inventory table
        inventory_check = await db.scalar(
            select(Inventory)
            .where(
                and_(
                    Inventory.product_id == data.product_id,
                    Inventory.branch_id == data.branch_id
                )
            )
        )

        # this condition is for when the returns none, and as a result, create a new inventory
        if not inventory_check:
            inventory_data = InventoryCreate(**data.model_dump())
            inventory = Inventory(**inventory_data.model_dump())
            db.add(inventory)
        else:
            inventory_check.quantity += data.quantity
    try:
        await db.commit()
        return {"detail": "new delivery successfully registered"}
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
    except ValueError as e:
        await db.rollback()
        raise
