from fastapi import APIRouter, Depends, status, HTTPException
from app.crud.product import get_all_products
from app.utils.employee import get_active_employee_access
from app.schemas.employee import EmployeeAccess
from app.schemas.product import ProductResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db


GENERAL_EMPLOYEE_ACCESS = ["employee"]


router = APIRouter()


@router.get("/products", response_model=list[ProductResponse])
async def get_products(
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.employee not in GENERAL_EMPLOYEE_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    product_data = await get_all_products(db)

    return product_data
