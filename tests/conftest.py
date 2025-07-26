import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import os
from app.models import Base


load_dotenv()


DATABASE_URL = TEST_DB_URL = os.getenv("Test_DATABASE_URL") # using a local postgrelsql db in .env

async_engine = create_async_engine(DATABASE_URL)
async_SessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)


# Create DB schema before each test
@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()


# Create session for test
@pytest_asyncio.fixture()
async def session() -> AsyncSession:
    async with async_SessionLocal() as session:
        yield session
