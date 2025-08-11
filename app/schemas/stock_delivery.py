from pydantic import BaseModel, ConfigDict
from datetime import date


class StockDeliveryCreate(BaseModel):
    branch_id: int
    product_id: int
    quantity: int
    supplier_name: str
    unit_cost: float
    supplied_date: date


class ProductStockDelivery(BaseModel):
    product_name: str

    model_config = ConfigDict(from_attributes=True)


class BranchStockDelivery(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class StockDeliveryResponse(BaseModel):
    id: int
    quantity: int
    supplier_name: str
    unit_cost: float
    supplied_date: date
    product: ProductStockDelivery
    branch: BranchStockDelivery

    model_config = ConfigDict(from_attributes=True)


class StockDeliveryUpdate(BaseModel):
    id: int
    quantity: int
    supplier_name: str
    unit_cost: float
    supplied_date: date
    product_name: str
    branch_name: str
