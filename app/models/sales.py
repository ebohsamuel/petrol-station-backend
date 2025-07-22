from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime, ForeignKey
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.products import Products
    from app.models.customers import Customers
    from app.models.branch import Branch


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column()
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=True, index=True) # None = walk-in
    total_price: Mapped[float] = mapped_column()
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    sales_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    plate_number: Mapped[str] = mapped_column(nullable=True) # null for issues that don't concern plate number

    product: Mapped["Products"] = relationship("Products", back_populates="sales")
    customer: Mapped["Customers"] = relationship("Customers", back_populates="sales")
    branch: Mapped["Branch"] = relationship("Branch", back_populates="sales")
