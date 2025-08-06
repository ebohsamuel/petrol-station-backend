from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from app.utils.employee import get_active_employee_access
from app.schemas.employee import EmployeeAccess
from app.schemas.product import ProductCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud.product import create_product


CREATE_BRANCH_ACCESS = ["admin"]

router = APIRouter()


@router.post("/register-product")
async def register_product(
        data: ProductCreate,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.role not in CREATE_BRANCH_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    product_data = await create_product(data, db)

    response = JSONResponse(content={"detail": "registration successful"})
    return response
