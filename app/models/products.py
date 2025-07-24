from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime
from datetime import datetime, timezone

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.price_history import PriceHistory
    from app.models.sales import Sale
    from app.models.inventory import Inventory
    from app.models.product_collection_request import ProductCollectionRequest
    from app.models.stock_delivery import StockDelivery

class Products(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(index=True, unique=True, nullable=True)
    latest_price: Mapped[float] = mapped_column(nullable=True)  # updated when price changes. replace the present value with the new value to update record
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc))

    price_history: Mapped[list["PriceHistory"]] = relationship("PriceHistory", back_populates="product")
    sales: Mapped[list["Sale"]] = relationship("Sale", back_populates="product")
    inventories: Mapped[list["Inventory"]] = relationship("Inventory", back_populates="product")
    product_collection_requests: Mapped[list["ProductCollectionRequest"]] = relationship("ProductCollectionRequest", back_populates="product")
    stock_deliveries: Mapped[list["StockDelivery"]] = relationship("StockDelivery", back_populates="product")