import os
import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models import Base, Branch

load_dotenv()

DATABASE_URL = os.getenv("Test_DATABASE_URL")
print(f"Test_DATABASE_URL: {DATABASE_URL}")

async_engine = create_async_engine(DATABASE_URL)
async_SessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)


# Create DB schema before each test
@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Create session for test
@pytest_asyncio.fixture()
async def session() -> AsyncSession:
    async with async_SessionLocal() as session:
        yield session


# Test creating a branch
@pytest.mark.asyncio
async def test_create_branch(session):
    branch_data = Branch(name="Buvel", location="MM way")
    session.add(branch_data)
    await session.commit()
    await session.refresh(branch_data)

    result = await session.scalar(select(Branch).where(Branch.id == branch_data.id))
    assert result.name == "Buvel"
    assert result.location == "MM way"
