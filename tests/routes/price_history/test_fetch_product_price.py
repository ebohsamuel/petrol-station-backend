import pytest
from app.schemas.product import ProductCreate
from app.crud.product import create_product
from app.models import Products
from app.schemas import employee as emp_schema
from app.crud import employee as emp_crud
from app.utils.general import create_access_token


@pytest.mark.asyncio
async def test_get_price_history(client, session):
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

    product_data = ProductCreate(product_name="petrol", latest_price=1500.0)
    product = await create_product(product_data, session)

    data = {
        "sub": employee.email,
        "employeeId": employee.id,
        "role": employee.role,
        "employee_access": [eba.branch_id for eba in (employee.employee_access or [])],
        "employee": "employee"
    }
    access_token = create_access_token(data)
    client.cookies.set(name="access_token", value=f"Bearer {access_token}")

    response = await client.get("/employee/get-price-history?product_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["price"] == 1500.0


@pytest.mark.asyncio
async def test_get_product_latest_price(client, session):
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

    product_data = ProductCreate(product_name="petrol", latest_price=1500.0)
    product = await create_product(product_data, session)

    data = {
        "sub": employee.email,
        "employeeId": employee.id,
        "role": employee.role,
        "employee_access": [eba.branch_id for eba in (employee.employee_access or [])],
        "employee": "employee"
    }
    access_token = create_access_token(data)
    client.cookies.set(name="access_token", value=f"Bearer {access_token}")

    response = await client.get("/employee/get-product-latest-price?product_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["latest_price"] == 1500.0
