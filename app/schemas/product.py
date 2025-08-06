from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    product_name: str
    latest_price: float | None = None


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    id: int
    product_name: str


class ProductResponse(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
