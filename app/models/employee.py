from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user_branch_access import UserBranchAccess



class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True, index=True)
    phone: Mapped[str] = mapped_column(nullable=True)
    photo: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column() # can be admin, manager, sales, inventory
    is_active: Mapped[bool] = mapped_column(default=False)

    user_access: Mapped[list["UserBranchAccess"]] = relationship("UserBranchAccess", back_populates="employee")
