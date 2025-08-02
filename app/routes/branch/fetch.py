from fastapi import APIRouter, Depends, status, HTTPException
from app.crud.branch import get_branches
from app.utils.employee import get_employee_access
from app.schemas.employee import EmployeeAccess
from app.schemas.branch import BranchResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from dotenv import load_dotenv
import os

load_dotenv()

GENERAL_EMPLOYEE_ACCESS = os.getenv("GENERAL_EMPLOYEE_ACCESS")


router = APIRouter()


@router.get("/branches", response_model=BranchResponse)
async def get_branches(
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_employee_access)
):
    if employee_access.employee not in GENERAL_EMPLOYEE_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    branch_data = await get_branches(db)

    return branch_data
