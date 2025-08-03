import pytest
from app.schemas import employee as emp_schema
from app.crud import employee as emp_crud
from app.utils.general import create_access_token
from app.models import Branch


@pytest.mark.asyncio
async def test_update_branch(client, session):
    branch_data = Branch(name="Buvel", location="MM way")
    session.add(branch_data)
    await session.commit()

    employee_data = emp_schema.EmployeeCreate(
        full_name="Test Tenant",
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

    branch = {
        "id": 1,
        "name": "station1",
        "location": "269 mm way"
    }

    response = await client.post("/employee/update-branch", json=branch)
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "update successful"


@pytest.mark.asyncio
async def test_update_branch_admin_exception(client, session):
    branch_data = Branch(name="Buvel", location="MM way")
    session.add(branch_data)
    await session.commit()

    employee_data = emp_schema.EmployeeCreate(
        full_name="Test Tenant",
        email="test@example.com",
        password="password123",
        confirmed_password="password123",
        role="manager"
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

    branch = {
        "id": 1,
        "name": "station1",
        "location": "269 mm way"
    }

    response = await client.post("/employee/update-branch", json=branch)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "access denied"
