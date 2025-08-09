import pytest

from app.models import Products
from app.schemas import employee as emp_schema
from app.crud import employee as emp_crud
from app.utils.general import create_access_token


@pytest.mark.asyncio
async def test_adjust_price(client, session):
    new_employee_data = {
        "full_name": "employee2",
        "email": "p1@example.com",
        "password": "password1234",
        "confirmed_password": "password1234",
        "role": "admin",
    }

    new_employee_data = emp_schema.EmployeeCreate(**new_employee_data)

    employee = await emp_crud.create_employee(new_employee_data, session)
    employee.is_active = True
    await session.commit()
    await session.refresh(employee, attribute_names=["employee_access"])

    product = Products(product_name="petrol")
    session.add(product)
    await session.commit()

    data = {
        "sub": employee.email,
        "employeeId": employee.id,
        "role": employee.role,
        "employee_access": [eba.branch_id for eba in (employee.employee_access or [])],
        "employee": "employee"
    }

    access_token = create_access_token(data)
    client.cookies.set(name="access_token", value=f"Bearer {access_token}")

    new_price_data = {
        "product_id": 1,
        "price": 1100.0
    }

    response = await client.post("/employee/adjust-product-price", json=new_price_data)
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "new price registered"
