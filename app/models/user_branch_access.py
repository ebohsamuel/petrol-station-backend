from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.branch import Branch
    from app.models.employee import Employee


class UserBranchAccess(Base):
    __tablename__ = "user_branch_access"

    id: Mapped[int] = mapped_column(primary_key=True)

    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))

    branch: Mapped["Branch"] = relationship("Branch", back_populates="user_access")
    employee: Mapped["Employee"] = relationship("Employee", back_populates="user_access")
