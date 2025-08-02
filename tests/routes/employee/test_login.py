import pytest
from app.models import Branch
from app.schemas import branch as branch_schema, employee as emp_schema
from app.crud import employee as emp_crud


@pytest.mark.asyncio
async def test_login(client, session):
    branch = Branch(name="station1", location="269 mm way")
    session.add(branch)
    await session.commit()
    await session.refresh(branch)

    branch_access = branch_schema.BranchBase(name="station1", location="269 mm way")

    employee_data = emp_schema.EmployeeCreate(
        full_name="Test Tenant",
        email="test@example.com",
        password="password123",
        confirmed_password="password123",
        role="admin",
        branch_access=[branch_access]
    )

    employee = await emp_crud.create_employee(data=employee_data, db=session)
    response = await client.post("/employee/token", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "login successful"
