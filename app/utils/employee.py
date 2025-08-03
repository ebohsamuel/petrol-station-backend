from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import employee as emp_crud
from .general import ExpiredTokenException, SECRET_KEY, ALGORITHM
from app.schemas.employee import EmployeeAccess
import jwt
from ..database import get_db


async def authenticate_employee(db: AsyncSession, email: str, password: str):
    employee_data = await emp_crud.get_employee_by_email_for_access(email, db)
    if not employee_data:
        return False
    if not emp_crud.pwd_context.verify(password, employee_data.hashed_password):
        return False
    return employee_data


async def get_employee_access(
        access_token: str | None = Cookie(default=None),
        db: AsyncSession = Depends(get_db)
) -> EmployeeAccess:
    if access_token is None:
        raise ExpiredTokenException

    token = access_token[len("Bearer "):]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    employee = await emp_crud.get_employee_by_email_with_lazy_loading(payload.get("sub"), db)
    if not employee:
        raise ExpiredTokenException

    payload.pop("exp")
    # the payload for employees contains sub(email), employeeId, role, employee_access, and the word "employee"

    return EmployeeAccess(**payload)


async def get_active_employee_access(
        employee_access: EmployeeAccess = Depends(get_employee_access),
        db: AsyncSession = Depends(get_db)
) -> EmployeeAccess:

    employee_data = await emp_crud.get_employee_by_id_for_self_update(employee_access.employeeId, db)
    if not employee_data.is_active:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail="employee not active")
    return employee_access
