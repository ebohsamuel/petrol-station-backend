from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime, ForeignKey
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.branch import Branch
    from app.models.products import Products


class StockDelivery(Base):
    __tablename__ = "stock_delivery"

    id: Mapped[int] = mapped_column(primary_key=True)

    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    quantity: Mapped[int] = mapped_column()
    supplier_name: Mapped[str] = mapped_column()

    supplied_date: Mapped[date] = mapped_column(DateTime)

    product: Mapped[Products] = relationship("Products", back_populates="stock_deliveries")
    branch: Mapped[Branch] = relationship("Branch", back_populates="stock_deliveries")