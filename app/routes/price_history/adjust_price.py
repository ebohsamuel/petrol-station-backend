from fastapi import APIRouter, Depends, status, HTTPException
from app.utils.employee import get_active_employee_access
from app.schemas.employee import EmployeeAccess
from app.schemas.price_history import AdjustPrice
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.product import get_product_by_id
from app.models import PriceHistory
from app.database import get_db


CREATE_BRANCH_ACCESS = ["admin"]

router = APIRouter()


@router.post("/adjust-product-price")
async def adjust_product_price(
        data: AdjustPrice,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.role not in CREATE_BRANCH_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    product = await get_product_by_id(id=data.product_id, db=db)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.latest_price = data.price

    price_history = PriceHistory(product=product, price=data.price)

    db.add_all(instances=[product, price_history])
    await db.commit()

    return {"detail": "new price registered"}
