from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.employee_branch_access import EmployeeBranchAccess
    from app.models.sales import Sale


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column(nullable=True)
    photo: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column() # can be admin, manager, sales, inventory
    is_active: Mapped[bool] = mapped_column(default=False)

    employee_access: Mapped[list["EmployeeBranchAccess"]] = relationship("EmployeeBranchAccess", back_populates="employee")
    sales: Mapped[list["Sale"]] = relationship("Sale", back_populates="employee")
