from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, field_validator, ValidationInfo
from datetime import datetime


class CustomerBase(BaseModel):
    full_name: str
    email: str
    phone_number: str | None = None
    address: str | None = None
    photo: str | None = None


class CustomerCreate(CustomerBase):
    password: str
    confirmed_password: str

    @field_validator("confirmed_password")
    def check_password(cls, v, info: ValidationInfo):
        if "password" in info.data and v != info.data.get("password"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Passwords do not match")
        return v


class Customer(CustomerBase):
    id: int
    customer_total_collection: float
    customer_total_payment: float
    is_active: bool
    created_at: datetime


class CustomerResponse(CustomerBase):
    id: int
    customer_total_collection: float
    customer_total_payment: float
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class CustomerUpdate(CustomerBase):
    id: int


class CustomerPasswordReset(BaseModel):
    id: int
    old_password: str
    new_password: str
    confirmed_password: str

    @field_validator("confirmed_password")
    def check_password(cls, v, info: ValidationInfo):
        if "new_password" in info.data and v != info.data.get("new_password"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Passwords do not match")
        return v
