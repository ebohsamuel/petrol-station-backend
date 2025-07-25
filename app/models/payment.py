from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Index
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.customers import Customers


# this table is use for recording registered customers payment done via paystack
class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_cusotmer_created_at", "customer_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float] = mapped_column()

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))

    paystack_ref: Mapped[str] = mapped_column(unique=True, index=True)
    status: Mapped[str] = mapped_column() # can be failed, pending,and success

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    customer: Mapped["Customers"] = relationship("Customers", back_populates="payments")