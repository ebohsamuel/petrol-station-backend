from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.schemas.employee import EmployeeLogin
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.general import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.utils.employee import authenticate_employee
from app.database import get_db


router = APIRouter()


@router.post("/token")
async def generate_access_token(data: EmployeeLogin, db: AsyncSession = Depends(get_db)):
    email = data.email
    password = data.password

    employee_data = await authenticate_employee(db, email, password)
    if not employee_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="incorrect email or password")

    data = {
        "sub": email,
        "role": employee_data.role,
        "employee_access": [eba.branch_id for eba in (employee_data.employee_access or [])],
        "employee": "employee"
    }

    access_token = create_access_token(data)

    response = JSONResponse(content={"detail": "login successful"})
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="none",
        secure=False,  # set to true in production
        expires=60*ACCESS_TOKEN_EXPIRE_MINUTES
    )

    return response
