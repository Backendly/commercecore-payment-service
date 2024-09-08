from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from .base import Base
import os

load_dotenv()

Database_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(Database_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_db():
    """Returns a new session"""
    with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def create_all_tables(app: FastAPI):
    """Creates all tables in the database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
