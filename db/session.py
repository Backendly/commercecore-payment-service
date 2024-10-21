from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from typing import AsyncGenerator, Any
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from .base import Base
import os
import pymysql
from redis_db.redis_db import CustomRedis

load_dotenv()
pymysql.install_as_MySQLdb()

DATABASE_URL = os.getenv("T_DATABASE", "DATABASE_URL")
CA_CERT_PATH = os.getenv("CA_CERT_PATH")

engine = create_async_engine(
    url=DATABASE_URL,
    echo=True,
    connect_args={},
)
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """Returns a new session"""
    async with AsyncSessionLocal() as session:
        yield session


def redis_instance():
    return CustomRedis()


@asynccontextmanager
async def create_all_tables(app: FastAPI):
    """Creates all tables in the database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
