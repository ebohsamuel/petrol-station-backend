from sqlalchemy.exc import SQLAlchemyError
from app.models import StockDelivery, Inventory
from app.schemas.stock_delivery import StockDeliveryUpdate
from app.utils.employee import get_active_employee_access
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, and_
from datetime import datetime, timezone
from app.schemas.employee import EmployeeAccess
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.product import get_product_by_name
from app.crud.branch import get_branch_by_name
from app.database import get_db


CREATE_BRANCH_ACCESS = ["admin"]

router = APIRouter()


@router.post("/update-stock-delivery")
async def update_stock_delivery(
        data: StockDeliveryUpdate,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.role not in CREATE_BRANCH_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    delivery = await db.scalar(
        select(StockDelivery)
        .where(
            StockDelivery.id == data.id
        )
    )
    if not delivery:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="delivery data not found")
    if delivery.supplied_date < datetime.now(timezone.utc).date():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="delivery data has been locked")

    # getting the parameters necessary to effectively update the inventory table
    old_product_id = delivery.product_id
    old_branch_id = delivery.branch_id
    old_quantity = delivery.quantity

    new_branch_name = data.branch_name
    new_product_name = data.product_name
    new_quantity = data.quantity

    # Map new_branch_name and new_product_name to IDs
    new_branch = await get_branch_by_name(new_branch_name, db)
    if not new_branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    new_product = await get_product_by_name(new_product_name, db)
    if not new_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if branch/product actually changed
    branch_changed = old_branch_id != new_branch.id
    product_changed = old_product_id != new_product.id
    quantity_changed = old_quantity != new_quantity

    # for when Branch or Product Changed
    if branch_changed or product_changed:
        # Decrement old
        old_inv = await db.scalar(
            select(Inventory)
            .where(
                and_(
                    Inventory.branch_id == old_branch_id,
                    Inventory.product_id == old_product_id
                )
            )
        )
        if old_inv:
            old_inv.quantity -= old_quantity
            if old_inv.quantity < 0:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="inventory can't be less than 0"
                )  # Avoid negatives

        # Increment new
        new_inv = await db.scalar(
            select(Inventory)
            .where(
                and_(
                    Inventory.branch_id == new_branch.id,
                    Inventory.product_id == new_product.id
                )
            )
        )
        if new_inv:
            new_inv.quantity += new_quantity
        else:
            new_inv = Inventory(
                branch_id=new_branch.id,
                product_id=new_product.id,
                quantity=new_quantity
            )
            db.add(new_inv)
    # Only Quantity Changed (same branch & product)
    elif quantity_changed:
        inv = await db.scalar(
            select(Inventory)
            .where(
                and_(
                    Inventory.branch_id == old_branch_id,
                    Inventory.product_id == old_product_id
                )
            )
        )
        if inv:
            quantity_diff = new_quantity - old_quantity
            inv.quantity += quantity_diff

    # updating the stock delivery record
    data_dict = data.model_dump(exclude={"id", "branch_name", "product_name"})
    data_dict.update({"branch_id": new_branch.id, "product_id": new_product.id})

    for key, value in data_dict.items():
        setattr(delivery, key, value)
    try:
        await db.commit()
        return {"detail": "delivery note and inventory successfully updated"}
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
    except ValueError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
