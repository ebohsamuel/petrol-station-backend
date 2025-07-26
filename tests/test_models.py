import asyncio

import pytest

from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.models import *


#Test creating a branch
@pytest.mark.asyncio
async def test_create_branch(session):
    branch_data = Branch(name="Buvel", location="MM way")
    session.add(branch_data)
    await asyncio.sleep(0)
    await session.commit()
    await session.refresh(branch_data)

    result = await session.scalar(select(Branch).where(Branch.id == branch_data.id))
    assert result.name == "Buvel"
    assert result.location == "MM way"


@pytest.mark.asyncio
async def test_create_employee(session):
    employee_data = Employee(
        full_name="Samuel Eboh",
        email="example@gmail.com",
        role="admin",
        phone="08137908237",
        photo="https://www.something,com"
    )

    session.add(employee_data)
    await asyncio.sleep(0)
    await session.commit()
    await session.refresh(employee_data)

    result = await session.scalar(select(Employee).where(Employee.email == employee_data.email))

    assert result.full_name == "Samuel Eboh"


@pytest.mark.asyncio
async def test_employee_and_user_branch_access_relationship(session):
    employee_data = Employee(full_name="Samuel Eboh", email="example1@gmail.com", role="admin")
    branch_data = Branch(name="nipco", location="MM way")
    useraccess = UserBranchAccess(branch=branch_data, employee=employee_data)

    session.add_all([branch_data, employee_data, useraccess])
    await session.commit()

    await session.refresh(employee_data)
    await session.refresh(branch_data)
    await session.refresh(useraccess)

    employee_result = await session.scalar(
        select(Employee).options(selectinload(Employee.user_access))
    )
    branch_result = await session.scalar(
        select(Branch).options(selectinload(Branch.user_access))
    )
    useraccess_result = await session.scalar(
        select(UserBranchAccess).options(
            selectinload(UserBranchAccess.branch),
            selectinload(UserBranchAccess.employee)
        )
    )

    assert employee_result.user_access[0].branch_id == branch_data.id
    assert branch_result.user_access[0].employee_id == employee_data.id
    assert useraccess_result.employee.full_name == employee_data.full_name
    assert useraccess_result.branch.name == branch_data.name



