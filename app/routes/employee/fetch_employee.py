from fastapi import APIRouter, Depends, status, HTTPException
from app.utils.employee import get_active_employee_access
from app.schemas.employee import EmployeeAccess
from app.schemas.employee import EmployeeResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Employee
from app.database import get_db
from sqlalchemy import func, select

CREATE_EMPLOYEE_ACCESS = ["admin",]

router = APIRouter()


@router.get("/get-all-employees", response_model=list[EmployeeResponse])
async def get_all_employees(
        offset: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.role not in CREATE_EMPLOYEE_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    result = await db.scalars(
        select(Employee)
        .offset(offset=offset)
        .limit(limit=limit)
    )
    employees = result.all()

    return employees


@router.get("/get-total-employee")
async def total_employee_count(
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.role not in CREATE_EMPLOYEE_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")
    total_count = await db.scalar(select(func.count(Employee.id)))
    return {"total": total_count}
