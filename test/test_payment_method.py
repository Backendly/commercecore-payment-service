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
from faker import Faker
import os

load_dotenv()

DATABASE_URL = os.getenv("TEST_DATABASE_URL")
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
            base_url="http://test",
        ) as ac:
            async with override_create_all_tables():
                yield ac


app.dependency_overrides[get_db] = overide_get_db


async def fake_payment_method():
    fake = Faker()
    return {
        "method_type": "card",
        "details": {
            "card_cvc": "1234",
            "card_number": "1234567890123456",
            "expiry_date": "02/32",
            "card_type": fake.credit_card_provider(),
        },
    }


@pytest.mark.anyio
async def test_create_payment_method(client):
    response = await client.post(
        "/api/v1/payment-methods",
        json=await fake_payment_method(),
    )
    data = response.json()
    assert response.status_code == 201
    assert "id" in data["data"]


@pytest.mark.anyio
async def test_four_card_number_exists(client):
    response = await client.post(
        "/api/v1/payment-methods",
        json=await fake_payment_method(),
    )
    data = response.json()
    assert response.status_code == 201
    assert "card_last_four" in data["data"]["details"]


@pytest.mark.anyio
async def test_must_include_card_number(client):
    request = await fake_payment_method()
    del request["details"]["card_number"]
    response = await client.post(
        "/api/v1/payment-methods",
        json=request,
    )
    data = response.json()
    assert response.status_code == 422
    data["detail"][0]["msg"] == f"Value error, card_number is required for"
    f" card payment"


@pytest.mark.anyio
async def test_must_include_card_type(client):
    request = await fake_payment_method()
    del request["details"]["card_type"]
    response = await client.post(
        "/api/v1/payment-methods",
        json=request,
    )
    data = response.json()
    assert response.status_code == 422
    data["detail"][0]["msg"] == "Value error, card_type is required for card payment"


@pytest.mark.anyio
async def test_must_include_expiry_date(client):
    request = await fake_payment_method()
    del request["details"]["expiry_date"]
    response = await client.post(
        "/api/v1/payment-methods",
        json=request,
    )
    data = response.json()
    assert response.status_code == 422
    data["detail"][0]["msg"] == "Value error, expiry_date is required for card payment"


@pytest.mark.anyio
async def test_must_include_card_cvc(client):
    request = await fake_payment_method()
    del request["details"]["card_cvc"]
    response = await client.post(
        "/api/v1/payment-methods",
        json=request,
    )
    data = response.json()
    assert response.status_code == 422
    data["detail"][0]["msg"] == "Value error, card_cvc is required for card payment"


@pytest.mark.anyio
async def test_response_time(client):
    response = await client.post(
        "/api/v1/payment-methods",
        json=await fake_payment_method(),
    )
    assert response.elapsed.total_seconds() < 1


@pytest.mark.anyio
async def test_method_type_is_required(client):
    request = await fake_payment_method()
    del request["method_type"]
    response = await client.post(
        "/api/v1/payment-methods",
        json=request,
    )
    data = response.json()
    assert response.status_code == 422
    data["detail"][0]["msg"] == "Value error, method_type is required"


@pytest.mark.anyio
async def test_response_card_num_is_last_four(client):
    request = await fake_payment_method()
    card_number = request["details"]["card_number"]
    response = await client.post(
        "/api/v1/payment-methods",
        json=request,
    )
    data = response.json()
    assert response.status_code == 201
    assert data["data"]["details"]["card_last_four"] == card_number[-4:]


@pytest.mark.anyio
async def test_details_is_required(client):
    request = await fake_payment_method()
    del request["details"]
    response = await client.post(
        "/api/v1/payment-methods",
        json=request,
    )
    data = response.json()
    assert response.status_code == 422
    data["detail"][0]["msg"] == "Value error, details is required"


@pytest.mark.anyio
async def test_card_number_is_all_digits(client):
    request = await fake_payment_method()
    request["details"]["card_number"] = "1234ab2223341233c"
    response = await client.post(
        "/api/v1/payment-methods",
        json=request,
    )
    data = response.json()
    assert response.status_code == 422
    data["detail"][0]["msg"] == "Value error, card_number must be all digits"


@pytest.mark.anyio
async def test_card_number_length_less(client):
    request = await fake_payment_method()
    request["details"]["card_number"] = "1234"
    response = await client.post(
        "/api/v1/payment-methods",
        json=request,
    )
    data = response.json()
    assert response.status_code == 422
    data["detail"][0][
        "msg"
    ] == "Value error, card_number must be between 13 and 19 digits"


@pytest.mark.anyio
async def test_card_number_length_more(client):
    request = await fake_payment_method()
    request["details"]["card_number"] = "12345678901234567890"
    response = await client.post(
        "/api/v1/payment-methods",
        json=request,
    )
    data = response.json()
    assert response.status_code == 422
    data["detail"][0][
        "msg"
    ] == "Value error, card_number must be between 13 and 19 digits"


@pytest.mark.anyio
async def test_expiry_date_is_in_MM_YY_format(client):
    request = await fake_payment_method()
    request["details"]["expiry_date"] = "12/2022"
    response = await client.post(
        "/api/v1/payment-methods",
        json=request,
    )
    data = response.json()
    assert response.status_code == 422
    assert (
        data["detail"][0]["msg"] == "Value error, expiry_date must be in MM/YY format"
    )


@pytest.mark.anyio
async def test_no_cvc_in_response(client):
    response = await client.post(
        "/api/v1/payment-methods",
        json=await fake_payment_method(),
    )
    data = response.json()
    assert response.status_code == 201
    assert "card_cvc" not in data["data"]["details"]


@pytest.mark.anyio
async def test_validation_error(client):
    response = await client.post(
        "/api/v1/payment-methods",
        json={},
    )
    data = response.json()
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_payment_methods(client):
    response = await client.get("/api/v1/payment-methods")
    data = response.json()
    assert response.status_code == 200


@pytest.mark.anyio
async def test_get_payment_method_wrong_path(client):
    response = await client.post("/api/v1/payment-method/1")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_not_allowed_method(client):
    response = await client.put("/api/v1/payment-methods")
    assert response.status_code == 405
    response = await client.delete("/api/v1/payment-methods")
    assert response.status_code == 405


@pytest.mark.anyio
async def test_get_payment_method(client):
    response = await client.post(
        "/api/v1/payment-methods", json=await fake_payment_method()
    )
    assert response.status_code == 201
    data = response.json()
    id = data["data"]["id"]

    payment_method = await client.get(f"/api/v1/payment-methods/{id}")
    assert payment_method.status_code == 200


@pytest.mark.anyio
async def test_get_payment_method_not_found(client):
    response = await client.get("/api/v1/payment-methods/pm_2yiHIBSwqIRuE-")
    assert response.status_code == 404
    data = response.json()
    assert data["details"]["message"] == "Payment method not found"


@pytest.mark.anyio
async def test_delete_payment_method(client):
    response = await client.post(
        "/api/v1/payment-methods", json=await fake_payment_method()
    )
    data = response.json()
    id = data["data"]["id"]

    delete_response = await client.delete(f"/api/v1/payment-methods/{id}")
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert data["message"] == "Payment method deleted successfully"
