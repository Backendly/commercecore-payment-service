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
        "/connected-accounts/onboarding", json={"account_id": "acct_1Q2aJc2azLnUiqXE"}
    )
    data = response.json()
    assert response.status_code == 201
