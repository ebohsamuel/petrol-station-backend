from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime, ForeignKey
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.customers import Customers
    from app.models.products import Products
    

class ProductCollectionRequest(Base):
    __tablename__ = "product_collection_requests"

    id: Mapped[int] = mapped_column(primary_key=True)

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    quantity: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column(default="pending") # pending or approved
    plate_number: Mapped[str] = mapped_column(nullable=True) # null for issues that don't concern plate number

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    customer: Mapped[Customers] = relationship("Customers", back_populates="product_collection_requests")
    product: Mapped[Products] = relationship("Products", back_populates="product_collection_requests")