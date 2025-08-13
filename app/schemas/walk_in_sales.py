from pydantic import BaseModel, ConfigDict
from datetime import datetime


class WalkInSalesBase(BaseModel):
    product_id: int
    branch_id: int
    employee_id: int | None = None  # will be updated in the api endpoint when entering new records
    plate_number: str | None = None
    total_price: float
    quantity: int


class WalkInSalesCreate(WalkInSalesBase):
    pass


class WalkInSalesProductResponse(BaseModel):
    product_name: str

    model_config = ConfigDict(from_attributes=True)


class WalkInSalesResponse(BaseModel):
    id: int
    product_id: int
    product: WalkInSalesProductResponse
    plate_number: str | None = None
    total_price: float
    quantity: int
    sales_time: datetime

    model_config = ConfigDict(from_attributes=True)


class WalkInSalesUpdate(BaseModel):
    id: int
    branch_id: int
    product_id: int
    plate_number: str | None = None
    total_price: float
    quantity: int
