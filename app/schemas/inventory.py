from pydantic import BaseModel, ConfigDict


class InventoryCreate(BaseModel):
    branch_id: int
    product_id: int
    quantity: int


class ProductInventory(BaseModel):
    product_name: str

    model_config = ConfigDict(from_attributes=True)


class InventoryResponse(BaseModel):
    id: int
    quantity: int
    product: ProductInventory

    model_config = ConfigDict(from_attributes=True)
