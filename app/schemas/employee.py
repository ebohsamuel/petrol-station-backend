from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, field_validator, ValidationInfo
from app.schemas.branch import BranchBase


class EmployeeBase(BaseModel):
    full_name: str
    email: str
    phone: str | None = None
    photo: str | None = None
    role: str


class EmployeeCreate(EmployeeBase):
    password: str
    branch_access: list[BranchBase] | None = None
    confirmed_password: str

    @field_validator("confirmed_password")
    def check_password(cls, v, info: ValidationInfo):
        if "password" in info.data and v != info.data.get("password"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Passwords do not match")
        return v


class EmployeeResponse(EmployeeBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class EmployeeAdminUpdate(BaseModel):
    id: int
    is_active: bool
    role: str
    branch_access: list[BranchBase] | None = None


class EmployeeAccess(BaseModel):
    sub: str
    employeeId: int
    role: str
    employee_access: list[int] | None = None
    employee: str


class EmployeeSelfUpdate(BaseModel):
    id: int | None = None
    full_name: str
    email: str
    phone: str | None = None
    photo: str | None = None


class EmployeePasswordReset(BaseModel):
    id: int | None = None
    old_password: str
    new_password: str
    confirmed_password: str

    @field_validator("confirmed_password")
    def check_password(cls, v, info: ValidationInfo):
        if "new_password" in info.data and v != info.data.get("new_password"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Passwords do not match")
        return v


class EmployeeLogin(BaseModel):
    email: str
    password: str
