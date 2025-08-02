from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.sales import Sale
    from app.models.inventory import Inventory
    from app.models.stock_delivery import StockDelivery
    from app.models.employee_branch_access import EmployeeBranchAccess


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    location: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    sales: Mapped[list["Sale"]] = relationship("Sale", back_populates="branch")
    inventories: Mapped[list["Inventory"]] = relationship("Inventory", back_populates="branch")
    stock_deliveries: Mapped[list["StockDelivery"]] = relationship("StockDelivery", back_populates="branch")
    employee_access: Mapped[list["EmployeeBranchAccess"]] = relationship("EmployeeBranchAccess", back_populates="branch")
