from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AdjustPrice(BaseModel):
    product_id: int
    price: float


class PriceHistoryResponse(BaseModel):
    price: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
