import os

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext
from app.models import Employee
from app.schemas import employee


scheme = os.getenv("scheme")

pwd_context = CryptContext(schemes=scheme, deprecated="auto")


async def get_employee_by_id(id: int, db: AsyncSession):
    return await db.scalar(
        select(Employee)
        .where(Employee.id == id)
        .options(
            selectinload(Employee.user_access),
            selectinload(Employee.sales)
        )
    )


async def get_employee_by_email(email: str, db: AsyncSession):
    return await db.scalar(
        select(Employee)
        .where(Employee.email == email)
        .options(
            selectinload(Employee.user_access),
            selectinload(Employee.sales)
        )
    )


async def create_employee(data: employee.EmployeeCreate, db: AsyncSession):
    hashed_password = pwd_context.hash(data.password)
    data_dict = data.model_dump()
    data_dict.pop("password")
    employee_data = Employee(**data_dict, hashed_password=hashed_password)
    try:
        db.add(employee_data)
        await db.commit()
        await db.refresh(employee_data)
        return employee_data
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
    except ValueError as e:
        await db.rollback()
        raise


async def update_employee(data: employee.EmployeeUpdate, db: AsyncSession):
    employee_data = await get_employee_by_id(id=data.id, db=db)
    if not employee_data:
        raise HTTPException(status_code=404, detail="Employee not found")

    data_dict = data.model_dump(exclude_none=True, exclude={"id"})
    for key, value in data_dict.items():
        setattr(employee_data, key, value)

    try:
        await db.commit()
        await db.refresh(employee_data)
        return employee_data
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
    except ValueError as e:
        await db.rollback()
        raise
