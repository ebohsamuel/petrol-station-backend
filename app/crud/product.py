from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Products, PriceHistory
from app.schemas.product import ProductUpdate, ProductCreate


async def get_product_by_name(product_name: str, db: AsyncSession):
    return await db.scalar(
        select(Products)
        .where(Products.product_name == product_name)
    )


async def get_product_by_id(id: int, db: AsyncSession):
    return await db.scalar(
        select(Products)
        .where(Products.id == id)
    )


async def get_all_products(db: AsyncSession):
    stmt = await db.execute(select(Products.id, Products.product_name, Products.latest_price))
    return stmt.all()


async def create_product(data: ProductCreate, db: AsyncSession):
    product = Products(**data.model_dump(exclude_none=True))
    instances = [product]
    if data.latest_price:
        price_history = PriceHistory(product=product, price=data.latest_price)
        instances.append(price_history)
    try:
        db.add_all(instances=instances)
        await db.commit()
        return product
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
    except ValueError as e:
        await db.rollback()
        raise


async def update_product_record(data: ProductUpdate, db: AsyncSession):
    product = await get_product_by_id(data.id, db)

    for key, value in data.model_dump(exclude={"id"}).items():
        setattr(product, key, value)
    try:
        await db.commit()
        return product
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
    except ValueError as e:
        await db.rollback()
        raise
