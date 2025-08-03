from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from app.utils.employee import get_active_employee_access
from app.schemas.employee import EmployeeAccess, EmployeePasswordReset
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.employee import reset_employee_password
from app.database import get_db


GENERAL_EMPLOYEE_ACCESS = ["employee"]


router = APIRouter()


@router.post("/password-reset")
async def employee_password_reset(
        data: EmployeePasswordReset,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.employee not in GENERAL_EMPLOYEE_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    data.id = employee_access.employeeId

    employee = await reset_employee_password(data, db)

    response = JSONResponse(content={"detail": "reset successful"})
    return response
