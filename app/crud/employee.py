import os
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext
from app.models import Employee, EmployeeBranchAccess, Branch
from app.schemas import employee


scheme = os.getenv("scheme")

pwd_context = CryptContext(schemes=scheme, deprecated="auto")


async def get_employee_by_id_for_admin_update(id: int, db: AsyncSession):
    return await db.scalar(
        select(Employee)
        .where(Employee.id == id)
        .options(
            selectinload(Employee.employee_access).selectinload(EmployeeBranchAccess.branch)
        )
    )


async def get_employee_by_id_for_self_update(id: int, db: AsyncSession):
    return await db.scalar(
        select(Employee)
        .where(Employee.id == id)
    )


async def get_employee_by_email_for_sales(email: str, db: AsyncSession):
    return await db.scalar(
        select(Employee)
        .where(Employee.email == email)
        .options(
            selectinload(Employee.sales)
        )
    )


async def get_employee_by_email_for_access(email: str, db: AsyncSession):
    return await db.scalar(
        select(Employee)
        .where(Employee.email == email)
        .options(
            selectinload(Employee.employee_access)
        )
    )


async def get_employee_by_email_with_lazy_loading(email: str, db: AsyncSession):
    return await db.scalar(
        select(Employee)
        .where(Employee.email == email)
    )


async def create_employee(data: employee.EmployeeCreate, db: AsyncSession):
    hashed_password = pwd_context.hash(data.password)

    # Create Employee object
    data_dict = data.model_dump(exclude={"password", "confirmed_password", "branch_access"}, exclude_none=True)
    employee_data = Employee(**data_dict, hashed_password=hashed_password)

    # Fetch Branch ORM objects
    employee_branch_access = []
    if data.branch_access:
        branch_names = [b.name for b in data.branch_access]
        branches = await db.scalars(select(Branch).where(Branch.name.in_(branch_names)))
        branch_map = {b.name: b for b in branches}

        for name in branch_names:
            if name not in branch_map:
                raise HTTPException(status_code=404, detail=f"Branch '{name}' not found")
            branch = branch_map.get(name)
            employee_branch_access.append(EmployeeBranchAccess(branch=branch, employee=employee_data))

    try:
        db.add_all([employee_data, *employee_branch_access])
        await db.commit()
        return employee_data
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
    except ValueError as e:
        await db.rollback()
        raise


async def employee_admin_update(data: employee.EmployeeAdminUpdate, db: AsyncSession):
    employee_data = await get_employee_by_id_for_admin_update(id=data.id, db=db)
    if not employee_data:
        raise HTTPException(status_code=404, detail="Employee not found")

    data_dict = data.model_dump(exclude_none=True, exclude={"id", "branch_access"})
    for key, value in data_dict.items():
        setattr(employee_data, key, value)

    # check if branch access needs updating
    # branch access from incoming data / pydantic
    branch_access = data.branch_access or []

    # branch access already stored in the database / orm
    db_branch_access = employee_data.employee_access or []

    # filter branches to add and remove by name
    incoming_branch_names = {branch.name for branch in branch_access}
    db_branch_names = {eba.branch.name for eba in db_branch_access}

    branches_to_add = incoming_branch_names - db_branch_names
    branches_to_remove = db_branch_names - incoming_branch_names

    # remove branches not needed
    employee_data.employee_access = [
        eba for eba in db_branch_access if eba.branch.name not in branches_to_remove
    ]

    # add needed branches
    branches = await db.scalars(select(Branch).where(Branch.name.in_(branches_to_add)))
    branch_map = {b.name: b for b in (branches or [])}

    for branch_name in branches_to_add:
        branch_data = branch_map.get(branch_name)
        if branch_data:
            employee_data.employee_access.append(EmployeeBranchAccess(branch=branch_data))
    try:
        await db.commit()
        return employee_data
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
    except ValueError as e:
        await db.rollback()
        raise


async def employee_self_update(data: employee.EmployeeSelfUpdate, db: AsyncSession):
    employee_data = await get_employee_by_id_for_self_update(id=data.id, db=db)
    if not employee_data:
        raise HTTPException(status_code=404, detail="Employee not found")

    data_dict = data.model_dump(exclude_none=True, exclude={"id"})
    for key, value in data_dict.items():
        setattr(employee_data, key, value)
    try:
        await db.commit()
        return employee_data
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
    except ValueError as e:
        await db.rollback()
        raise


async def reset_employee_password(data: employee.EmployeePasswordReset, db: AsyncSession):
    employee_data = await get_employee_by_id_for_self_update(id=data.id, db=db)
    if not employee_data:
        raise HTTPException(status_code=404, detail="Employee not found")

    hashed_password = pwd_context.hash(data.new_password)
    setattr(employee_data, "hashed_password", hashed_password)
    try:
        await db.commit()
        return employee_data
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
    except ValueError as e:
        await db.rollback()
        raise
