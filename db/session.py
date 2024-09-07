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
DBSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    """Returns a new session"""
    db = DBSession()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def create_all_tables(app: FastAPI):
    """Creates all tables in the database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
