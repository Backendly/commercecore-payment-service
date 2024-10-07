from api.main import app
from httpx import AsyncClient, ASGITransport
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from db.base import Base
from contextlib import asynccontextmanager
from db.session import get_db
from asgi_lifespan import LifespanManager
import os

load_dotenv()

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine_test = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocalTest = sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False
)


async def overide_get_db():
    async with AsyncSessionLocalTest() as session:
        yield session


@asynccontextmanager
async def override_create_all_tables():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield


@pytest.fixture(scope="module")
async def client():
    async with LifespanManager(app) as lifespan:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="https://commercecore-payment-api-bbdd0516ee91.herokuapp.com/api/v1",
        ) as ac:
            async with override_create_all_tables():
                yield ac


app.dependency_overrides[get_db] = overide_get_db
