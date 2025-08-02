from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from app.utils.employee import get_employee_access
from app.schemas.employee import EmployeeAccess
from app.schemas.branch import BranchCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud.branch import create_branch


CREATE_BRANCH_ACCESS = ["admin"]

router = APIRouter()


@router.post("/register-branch")
async def register_branch(
        data: BranchCreate,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_employee_access)
):
    if employee_access.role not in CREATE_BRANCH_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    branch_data = await create_branch(data, db)

    response = JSONResponse(content={"detail": "registration successful"})
    return response
