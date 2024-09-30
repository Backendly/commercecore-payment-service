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
