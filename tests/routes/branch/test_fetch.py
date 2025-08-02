import pytest
from app.models import Branch
from app.schemas import employee as emp_schema
from app.crud import employee as emp_crud
from app.utils.general import create_access_token


@pytest.mark.asyncio
async def test_fetch_branch_records(client, session):
    branch_data = Branch(name="Buvel", location="MM way")
    session.add(branch_data)
    await session.commit()
    await session.refresh(branch_data)

    employee_data = emp_schema.EmployeeCreate(
        full_name="Test Tenant",
        email="test@example.com",
        password="password123",
        confirmed_password="password123",
        role="admin"
    )
    employee = await emp_crud.create_employee(data=employee_data, db=session)

    data = {
        "sub": employee.email,
        "role": employee.role,
        "employee_access": [eba.branch_id for eba in (employee.employee_access or [])],
        "employee": "employee"
    }

    access_token = create_access_token(data)
    client.cookies.set(name="access_token", value=f"Bearer {access_token}")

    response = await client.get("/employee/branches")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["location"] == "MM way"
    assert data[0]["id"] == 1
