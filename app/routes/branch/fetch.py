from fastapi import APIRouter, Depends, status, HTTPException
from app.crud.branch import get_branch_records
from app.utils.employee import get_active_employee_access
from app.schemas.employee import EmployeeAccess
from app.schemas.branch import BranchResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db


GENERAL_EMPLOYEE_ACCESS = ["employee"]


router = APIRouter()


@router.get("/branches", response_model=list[BranchResponse])
async def get_branches(
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_active_employee_access)
):
    if employee_access.employee not in GENERAL_EMPLOYEE_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    branch_data = await get_branch_records(db)

    return branch_data
