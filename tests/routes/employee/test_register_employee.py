import pytest

from app.models import Branch
from app.schemas import employee as emp_schema
from app.crud import employee as emp_crud
from app.utils.general import create_access_token


@pytest.mark.asyncio
async def test_register_employee(client, session):
    branch_data = Branch(name="station1", location="269 mm way")
    session.add(branch_data)
    await session.commit()

    employee_data = emp_schema.EmployeeCreate(
        full_name="employee1",
        email="test@example.com",
        password="password123",
        confirmed_password="password123",
        role="admin"
    )
    employee = await emp_crud.create_employee(data=employee_data, db=session)
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

    new_employee_data = {
        "full_name": "employee2",
        "email": "p1@example.com",
        "password": "password1234",
        "confirmed_password": "password1234",
        "role": "manager",
        "branch_access": [{"name": "station1", "location": "269 mm way"}]
    }

    response = await client.post("/employee/register-employee", json=new_employee_data)
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "employee registered successfully"
