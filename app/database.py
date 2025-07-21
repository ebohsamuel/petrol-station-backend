from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
import os


DATABASE_URL = os.getenv("DATABASE_URL")

async_engine = create_async_engine(DATABASE_URL)

async_SessionLocal = async_sessionmaker(autoflush=False, bind=async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass