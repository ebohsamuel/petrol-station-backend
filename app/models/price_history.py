from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime, ForeignKey, Index, desc
from datetime import datetime, timezone

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.products import Products


class PriceHistory(Base):
    __tablename__ = "price_history"
    __table_args__ = (
        Index("ix_product_created_at", "product_id", desc("created_at")),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    price: Mapped[float] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda:datetime.now(timezone.utc))

    product: Mapped["Products"] = relationship("Products", back_populates="price_history")
