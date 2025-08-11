import pytest
from app.schemas import employee as emp_schema
from app.crud import employee as emp_crud
from app.utils.general import create_access_token
from app.models import Products, Branch


@pytest.mark.asyncio
async def test_get_stock_delivery_and_inventory_records(client, session):
    branch1 = Branch(name="Buvel1", location="100 MM way b/c")
    session.add(branch1)

    branch2 = Branch(name="Buvel2", location="269 MM way b/c")
    session.add(branch2)

    product = Products(product_name="petrol", latest_price=1100.0)
    session.add(product)

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

    deliveries = [
        {
            "branch_id": 1,
            "product_id": 1,
            "quantity": 100,
            "supplier_name": "Total Nig Plc",
            "unit_cost": 990.0,
            "supplied_date": "2025-08-11"
        },
        {
            "branch_id": 2,
            "product_id": 1,
            "quantity": 200,
            "supplier_name": "Total Nig Plc",
            "unit_cost": 990.0,
            "supplied_date": "2025-08-11"
        },

    ]

    response = await client.post("/employee/register-new-delivery", json=deliveries)
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "new delivery successfully registered"

    response = await client.get("/employee/get-stock-delivery-records")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["branch"]["name"] == "Buvel2"
    assert data[1]["branch"]["name"] == "Buvel1"
    assert data[1]["product"]["product_name"] == "petrol"

    response = await client.get("/employee/get-total-delivery-record")
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == 2

    response = await client.get("/employee/get-inventory-records?branch_id=2")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["product"]["product_name"] == "petrol"
