import pytest
from app.schemas import employee as emp_schema
from app.crud import employee as emp_crud
from app.utils.general import create_access_token
from app.models import Products, Branch
from datetime import date


@pytest.mark.asyncio
async def test_walk_in_sales(client, session):
    branch1 = Branch(name="Buvel1", location="100 MM way b/c")
    session.add(branch1)

    branch2 = Branch(name="Buvel2", location="269 MM way b/c")
    session.add(branch2)

    product1 = Products(product_name="petrol", latest_price=1100.0)
    session.add(product1)

    product2 = Products(product_name="diesel", latest_price=1200.0)
    session.add(product2)

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

    # test creation of stock delivery records and updating stock
    deliveries = [
        {
            "branch_id": 1,
            "product_id": 1,
            "quantity": 100,
            "supplier_name": "Total Nig Plc",
            "unit_cost": 990.0,
            "supplied_date": date.today().isoformat(),
        },
        {
            "branch_id": 2,
            "product_id": 1,
            "quantity": 200,
            "supplier_name": "Total Nig Plc",
            "unit_cost": 990.0,
            "supplied_date": date.today().isoformat(),
        },

    ]

    response = await client.post("/employee/register-new-delivery", json=deliveries)

    # testing the creation of new record for walk in sales in the db
    walk_in_sale = {
        "product_id": 1,
        "branch_id": 2,
        "total_price": 15300,
        "quantity": 15
    }
    response = await client.post("/employee/register-new-walk-in-sales", json=walk_in_sale)
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "walk in sales record entered successfully"

    # testing the update endpoint api for walk in sales
    walk_in_sale_update = {
        "id": 1,
        "branch_id": 2,
        "product_id": 1,
        "plate_number": "mkk295xa",
        "total_price": 15300,
        "quantity": 15
    }
    response = await client.post("/employee/update-walk-in-sales", json=walk_in_sale_update)
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "sales note and inventory successfully updated"

    # test getting the total sales record for walk in sales
    response = await client.get("/employee/get-total-walk-in-sales-records?branch_id=2")
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == 1

    # test getting paginated sales record for walk in sales
    response = await client.get("/employee/get-walk-in-sales-records?branch_id=2")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["product"]["product_name"] == "petrol"
