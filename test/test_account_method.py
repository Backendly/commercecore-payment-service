from .test_utils import client, overide_get_db
import pytest
from db.session import get_db
from api.main import app

app.dependency_overrides[get_db] = overide_get_db


@pytest.mark.anyio
async def test_create_connected_account(client):
    """This will test connected account  creation"""
    response = await client.post("/connected-accounts", json={"email": "ezewisdomjohn"})
    data = response.json()
    assert response.status_code == 201


@pytest.mark.anyio
async def test_account_onboarding_link(client):
    """This will test the onboarding of a user"""
    response = await client.post(
        "/connected-accounts/onboarding",
        json={"account_id": "acct_1Q2aJc2azLnUiqXE"},
        headers={"X-Developer-Token": "b9f10f7c-4743-4423-a2c0-888168864f5d"},
    )
    data = response.json()
    assert response.status_code == 201
    assert data != None


@pytest.mark.anyio
async def test_account_login_link_for_incomplete_onboarding(client):
    """This will test account login success"""
    response = await client.post(
        "/connected-accounts/login",
        json={"account_id": "acct_1Q2aJc2azLnUiqXE"},
        headers={"X-Developer-Token": "b9f10f7c-4743-4423-a2c0-888168864f5d"},
    )
    data = response.json()
    assert response.status_code == 500


@pytest.mark.anyio
async def test_test_unauthorized_creation_of_connected_account(client):
    """This will test unauthorized creation of connected account"""
    response = await client.post(
        "/connected-accounts",
        json={"email": "ezewisdomjohn"},
        headers={"X-Developer-Token": "b9f10f7c-4743-4423-a2c0-888168864f5e"},
    )
    data = response.json()
    assert response.status_code == 401
    assert data["detail"] == "Unauthorized"


@pytest.mark.anyio
async def test_unauthorized_onboarding_of_connected_account(client):
    """This will test unauthorized onboarding of connected account"""
    response = await client.post(
        "/connected-accounts/onboarding",
        json={"account_id": "acct_1Q2aJc2azLnUiqXE"},
        headers={"X-Developer-Token": "b9f10f7c-4743-4423-a2c0-888168864f5e"},
    )
    data = response.json()
    assert response.status_code == 401
    assert data["detail"] == "Unauthorized"


@pytest.mark.anyio
async def test_unauthorized_login_of_connected_account(client):
    """This will test unauthorized login of connected account"""
    response = await client.post(
        "/connected-accounts/login",
        json={"account_id": "acct_1Q2aJc2azLnUiqXE"},
        headers={"X-Developer-Token": "b9f10f7c-4743-4423-a2c0-888168864f5e"},
    )
    data = response.json()
    assert response.status_code == 401
    assert data["detail"] == "Unauthorized"


@pytest.mark.anyio
async def test_delete_acount(client):
    """This will test the deletion of an account where the developer is not the owner"""
    response = await client.delete(
        "/connected-accounts/acct_1Q2aJc2azLnUiqXE",
        headers={"X-Developer-Token": "b9f10f7c-4743-4423-a2c0-888168864f5d"},
    )
    data = response.json()
    assert response.status_code == 401
    assert data == {"detail": "Not the Owner of account"}
