from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from app.utils.employee import get_active_employee_access
from app.schemas.employee import EmployeeAccess, EmployeeAdminUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.employee import employee_admin_update
from app.database import get_db


CREATE_EMPLOYEE_ACCESS = ["admin",]

router = APIRouter()


@router.post("/admin/update-employee")
async def admin_update_employee(
        data: EmployeeAdminUpdate,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.role not in CREATE_EMPLOYEE_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    employee = await employee_admin_update(data, db)

    response = JSONResponse(content={"detail": "update successful"})
    return response
