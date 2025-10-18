from sqlalchemy import select, and_
from app.schemas.walk_in_sales import WalkInSalesUpdate
from app.schemas.employee import EmployeeAccess
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Sale, Inventory
from app.database import get_db
from app.utils.employee import get_active_employee_access
from fastapi import APIRouter, Depends, status, HTTPException
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import SQLAlchemyError


CREATE_BRANCH_ACCESS = {"admin"}

router = APIRouter()


@router.post("/update-walk-in-sales")
async def update_walk_in_sales(
        walk_in_sale_update: WalkInSalesUpdate,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    # check if the employee is admin, and if not, we check if the employee is a manager with a branch access
    if employee_access.role not in CREATE_BRANCH_ACCESS:
        if walk_in_sale_update.branch_id not in employee_access.employee_access or employee_access.role != "manager":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    # first get the sales record from the db
    sale_record = await db.scalar(
        select(Sale)
        .where(Sale.id == walk_in_sale_update.id)
    )
    if not sale_record:
        raise HTTPException(status_code=404, detail="Sale record not found")

    sales_time = sale_record.sales_time
    if sales_time.tzinfo is None:
        sales_time = sales_time.replace(tzinfo=timezone.utc)

    # we check if the record has been in the db for more than 3 hours and if not we raise an exception
    time_diff = datetime.now(timezone.utc) - sales_time
    if time_diff > timedelta(hours=3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="sales data has been locked")

    # we get the product id in the db and the one being sent for update, and see if there are changes
    new_product_id = walk_in_sale_update.product_id
    old_product_id = sale_record.product_id

    product_changed = new_product_id != old_product_id

    if product_changed:
        # get the old inv record and add with_for_update() function to prevent race conditions
        old_inv = await db.scalar(
            select(Inventory)
            .where(
                and_(
                    Inventory.product_id == sale_record.product_id,
                    Inventory.branch_id == sale_record.branch_id
                )
            )
            .with_for_update()
        )
        # check if such a record exist
        if not old_inv:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="product not in the inventory of the branch"
            )
        # if the record exist we return back the qty that was initially deducted from it
        old_inv.quantity += sale_record.quantity

        # get the new inv record and add with_for_update() function to prevent race conditions
        new_inv = await db.scalar(
            select(Inventory)
            .where(
                and_(
                    Inventory.product_id == walk_in_sale_update.product_id,
                    Inventory.branch_id == sale_record.branch_id
                )
            )
            .with_for_update()
        )
        # check if such a record exist
        if not new_inv:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="product not in the inventory of the branch"
            )
        # check if the stock level in the inventory csn support the update
        if new_inv.quantity < walk_in_sale_update.quantity:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="stock level not sufficient to complete the transaction"
            )
        new_inv.quantity -= walk_in_sale_update.quantity

    # condition for when there is no product change in the update info
    elif not product_changed:
        inv = await db.scalar(
            select(Inventory)
            .where(
                and_(
                    Inventory.product_id == sale_record.product_id,
                    Inventory.branch_id == sale_record.branch_id
                )
            )
            .with_for_update()
        )
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="product not in the inventory of the branch"
            )

        if sale_record.quantity < walk_in_sale_update.quantity:
            if inv.quantity < (walk_in_sale_update.quantity - sale_record.quantity):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="stock level not sufficient to complete the transaction"
                )
        quantity_diff = sale_record.quantity - walk_in_sale_update.quantity
        inv.quantity += quantity_diff

    for key, value in walk_in_sale_update.model_dump(exclude_none=True, exclude={"id"}).items():
        setattr(sale_record, key, value)

    try:
        await db.commit()
        return {"detail": "sales note and inventory successfully updated"}
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
    except ValueError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
