from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime, timezone
from sqlalchemy import DateTime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.sales import Sale
    from app.models.product_collection_request import ProductCollectionRequest
    from app.models.payment import Payment


class Customers(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    phone_number: Mapped[str] = mapped_column(nullable=True)
    address: Mapped[str] = mapped_column(nullable=True)
    photo: Mapped[str] = mapped_column(nullable=True)  # image link is saved here while the actual file is saved in
    # Cloudinary
    customer_total_collection: Mapped[float] = mapped_column(default=0.0)  # what of goods collected. update is done
    # by adding new collection to the present value
    customer_total_payment: Mapped[float] = mapped_column(default=0.0)  # total amount a customer paid in to their
    # wallet. update is done by adding new payment to the previous payment
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    sales: Mapped[list["Sale"]] = relationship("Sale", back_populates="customer")
    product_collection_requests: Mapped[list["ProductCollectionRequest"]] = relationship("ProductCollectionRequest", back_populates="customer")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="customer")
