import pytest

from app.models import Branch
from app.schemas import employee as emp_schema
from app.crud import employee as emp_crud
from app.utils.general import create_access_token


@pytest.mark.asyncio
async def test_profile_update(client, session):
    branch_data = Branch(name="station1", location="269 mm way")
    session.add(branch_data)
    await session.commit()

    new_employee_data = {
        "full_name": "employee2",
        "email": "p1@example.com",
        "password": "password1234",
        "confirmed_password": "password1234",
        "role": "manager",
        "branch_access": [{"name": "station1", "location": "269 mm way"}]
    }

    new_employee_data = emp_schema.EmployeeCreate(**new_employee_data)

    employee = await emp_crud.create_employee(new_employee_data, session)
    employee.is_active = True
    await session.commit()
    await session.refresh(employee, attribute_names=["employee_access"])

    data = {
        "sub": employee.email,
        "employeeId": employee.id,
        "role": employee.role,
        "employee_access": [eba.branch_id for eba in (employee.employee_access or [])],
        "employee": "employee"
    }

    access_token = create_access_token(data)
    client.cookies.set(name="access_token", value=f"Bearer {access_token}")

    employee_update_data = {
        "full_name": "employee1",
        "email": "p3@example.com",
    }

    response = await client.post("/employee/profile-update", json=employee_update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "update successful"


@pytest.mark.asyncio
async def test_profile_update_inactive_exception(client, session):
    branch_data = Branch(name="station1", location="269 mm way")
    session.add(branch_data)
    await session.commit()

    new_employee_data = {
        "full_name": "employee2",
        "email": "p1@example.com",
        "password": "password1234",
        "confirmed_password": "password1234",
        "role": "manager",
        "branch_access": [{"name": "station1", "location": "269 mm way"}]
    }

    new_employee_data = emp_schema.EmployeeCreate(**new_employee_data)

    employee = await emp_crud.create_employee(new_employee_data, session)

    data = {
        "sub": employee.email,
        "employeeId": employee.id,
        "role": employee.role,
        "employee_access": [eba.branch_id for eba in (employee.employee_access or [])],
        "employee": "employee"
    }

    access_token = create_access_token(data)
    client.cookies.set(name="access_token", value=f"Bearer {access_token}")

    employee_update_data = {
        "full_name": "employee1",
        "email": "p3@example.com",
    }

    response = await client.post("/employee/profile-update", json=employee_update_data)
    assert response.status_code == 412
    data = response.json()
    assert data["detail"] == "employee not active"
