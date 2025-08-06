from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Branch
from app.schemas.branch import BranchCreate, BranchUpdate


async def get_branch_by_id(id: int, db: AsyncSession):
    return await db.scalar(
        select(Branch)
        .where(Branch.id == id)
    )


async def get_branch_by_name(name: str, db: AsyncSession):
    return await db.scalar(
        select(Branch)
        .where(Branch.name == name)
    )


async def get_branch_records(db: AsyncSession):
    stmt = await db.execute(select(Branch.id, Branch.name, Branch.location))
    return stmt.all()


async def create_branch(data: BranchCreate, db: AsyncSession):
    branch_data = Branch(**data.model_dump())
    try:
        db.add(branch_data)
        await db.commit()
        return branch_data
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
    except ValueError as e:
        await db.rollback()
        raise


async def update_branch_record(data: BranchUpdate, db: AsyncSession):
    branch_data = await get_branch_by_id(data.id, db)

    for key, value in data.model_dump(exclude={"id"}).items():
        setattr(branch_data, key, value)

    try:
        db.add(branch_data)
        await db.commit()
        return branch_data
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"An error occurred: {e}")
        raise
    except ValueError as e:
        await db.rollback()
        raise
