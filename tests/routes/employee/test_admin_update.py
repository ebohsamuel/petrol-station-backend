import pytest

from app.models import Branch
from app.schemas import employee as emp_schema
from app.crud import employee as emp_crud
from app.utils.general import create_access_token


@pytest.mark.asyncio
async def test_admin_update(client, session):
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
    new_employee = await emp_crud.create_employee(new_employee_data, session)

    employee_admin_data = emp_schema.EmployeeCreate(
        full_name="employee1",
        email="test@example.com",
        password="password123",
        confirmed_password="password123",
        role="admin"
    )
    employee_admin = await emp_crud.create_employee(data=employee_admin_data, db=session)
    employee_admin.is_active = True
    await session.commit()
    await session.refresh(employee_admin, attribute_names=["employee_access"])

    data = {
        "sub": employee_admin.email,
        "employeeId": employee_admin.id,
        "role": employee_admin.role,
        "employee_access": [eba.branch_id for eba in (employee_admin.employee_access or [])],
        "employee": "employee"
    }

    access_token = create_access_token(data)
    client.cookies.set(name="access_token", value=f"Bearer {access_token}")

    employee_update_data = {
        "id": 1,
        "is_active": True,
        "role": "manager",
        "branch_access": [{"name": "station1", "location": "269 mm way"}]
    }

    response = await client.post("/employee/admin/update-employee", json=employee_update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "update successful"
