from pydantic import BaseModel, ConfigDict


class EmployeeBase(BaseModel):
    full_name: str
    email: str
    phone: str | None = None
    photo: str | None = None
    role: str


class EmployeeCreate(EmployeeBase):
    password: str


class EmployeeResponse(EmployeeBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class EmployeeUpdate(EmployeeResponse):
    pass
