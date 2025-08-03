from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from app.utils.employee import get_active_employee_access
from app.schemas.employee import EmployeeAccess, EmployeeCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.employee import create_employee
from app.database import get_db
from app.models import Branch


CREATE_EMPLOYEE_ACCESS = ["admin", "manager"]

router = APIRouter()


@router.post("/register-employee")
async def register_new_employee(
        applicant_data: EmployeeCreate,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):

    if employee_access.role not in CREATE_EMPLOYEE_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    if employee_access.role == "manager":
        employee_branch_access_by_id = employee_access.employee_access
        employee_branch_access_by_name = await db.execute(
            select(Branch.name)
            .where(Branch.id.in_(employee_branch_access_by_id))
        )
        employee_branch_access_by_name_in_set = {b.name for b in employee_branch_access_by_name}

        applicant_given_access = applicant_data.branch_access
        applicant_given_access_by_branch_names = {b.name for b in (applicant_given_access or [])}

        employee_applicant_access_diff = (
                applicant_given_access_by_branch_names - employee_branch_access_by_name_in_set
        )
        if employee_applicant_access_diff:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="you don't have permission to give access beyond your assigned branch"
            )

    new_employee = await create_employee(data=applicant_data, db=db)

    # a background task to handle sending email activation link to new employee email will enter here

    response = JSONResponse(content={"detail": "employee registered successfully"})
    return response
