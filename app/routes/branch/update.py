from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from app.utils.employee import get_employee_access
from app.schemas.employee import EmployeeAccess
from app.schemas.branch import BranchUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from dotenv import load_dotenv
from app.crud.branch import update_branch
import os

load_dotenv()

CREATE_BRANCH_ACCESS = os.getenv("CREATE_BRANCH_ACCESS")

router = APIRouter()


@router.post("/update-branch")
async def update_branch(
        data: BranchUpdate,
        db: AsyncSession = Depends(get_db),
        employee_access: EmployeeAccess = Depends(get_employee_access)
):
    if employee_access.role not in CREATE_BRANCH_ACCESS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access denied")

    branch_data = await update_branch(data, db)

    response = JSONResponse(content={"detail": "update successful"})
    return response
