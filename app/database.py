from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: ${DATABASE_URL}")

async_engine = create_async_engine(DATABASE_URL)

async_SessionLocal = async_sessionmaker(autoflush=False, bind=async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_SessionLocal() as session:
        yield session
