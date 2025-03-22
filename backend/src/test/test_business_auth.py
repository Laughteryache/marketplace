import pytest
from httpx import AsyncClient
from global_config import settings
from watchfiles import awatch

IP_ADDRESS = settings.IP_ADDRESS
SERVER_PORT = settings.SERVER_PORT

alex_data = { # Good Boy
    'email': 'alex@alexandria.com',
    'password': '$uper5trong4lexandrsPWD',
}

john_data = { # Bad Boy
    'email': 'john@johnwill.com',
    'password': 'notstrongpwd',
}

business_sign_up = f"http://{IP_ADDRESS}:{SERVER_PORT}/v1/api/auth/business/sign-up"
business_sign_in = f"http://{IP_ADDRESS}:{SERVER_PORT}/v1/api/auth/business/sign-in"

@pytest.mark.asyncio
async def test_alex_sign_up():
    async with AsyncClient() as client:
        response = await client.post(
            url=business_sign_up, json=alex_data
        )
    assert response.status_code == 200
    assert 'access_token' in response.json().keys()
    assert 'refresh_token' in response.json().keys()

    async with AsyncClient() as client:
        response = await client.post(
            url=business_sign_up, json=alex_data
        )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_john_sign_up():
    async with AsyncClient() as client:
        response = await client.post(
            url=business_sign_up, json=john_data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_no_json_sign_up():
    async with AsyncClient() as client:
        response = await client.post(
            url=business_sign_up, json={}
        )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_alex_sign_in():
    async with AsyncClient() as client:
        response = await client.post(
            url=business_sign_in, json=alex_data
        )
    assert response.status_code == 200
    assert 'access_token' in response.json().keys()
    assert 'refresh_token' in response.json().keys()