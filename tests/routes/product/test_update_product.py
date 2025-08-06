import pytest
from app.schemas import employee as emp_schema
from app.crud import employee as emp_crud
from app.utils.general import create_access_token
from app.models import Products


@pytest.mark.asyncio
async def test_update_product(client, session):
    product = Products(product_name="petrol", latest_price=1100.0)
    session.add(product)
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

    product_data = {
        "id": "1",
        "product_name": "petroleum",
    }

    response = await client.post("/employee/update-product", json=product_data)
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "update successful"
