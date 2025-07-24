from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime, ForeignKey, Index
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.products import Products
    from app.models.customers import Customers
    from app.models.branch import Branch

# this table registers the goods collected by registered customers and those of walk in customers
class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = (
        Index("ix_customer_sales_time", "customer_id", "sales_time"),
        Index("ix_branch_sales_time", "branch_id", "sales_time")
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=True) # None = walk-in
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))

    plate_number: Mapped[str] = mapped_column(nullable=True) # null for issues that don't concern plate number

    total_price: Mapped[float] = mapped_column()
    quantity: Mapped[int] = mapped_column()
    
    sales_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    product: Mapped["Products"] = relationship("Products", back_populates="sales")
    customer: Mapped["Customers"] = relationship("Customers", back_populates="sales")
    branch: Mapped["Branch"] = relationship("Branch", back_populates="sales")
