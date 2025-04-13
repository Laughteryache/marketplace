import pytest
from global_config import settings
from httpx import AsyncClient

from .test_business_auth import sign_up as business_sign_up
from .test_user_auth import sign_up as user_sign_up
from .testers import olivia_data

IP_ADDRESS = settings.IP_ADDRESS
SERVER_PORT = settings.SERVER_PORT

balance = f"http://{IP_ADDRESS}:{SERVER_PORT}/v1/api/profile/balance"


@pytest.mark.asyncio
async def test_olivia_business_balance():
    async with AsyncClient() as client:
        response = await client.post(url=business_sign_up, json=olivia_data)
    assert response.status_code == 200
    assert 'access_token' in response.json().keys()
    assert 'refresh_token' in response.json().keys()
    access_token = response.json()['access_token']
    async with AsyncClient() as client:
        response = await client.get(url=balance, cookies={'token': access_token})
        assert response.status_code == 401

    async with AsyncClient() as client:
        response = await client.get(url=balance, cookies={'access_token': access_token})
    assert response.status_code == 200
    assert response.json()['balance'] == 0


@pytest.mark.asyncio
async def test_olivia_user_balance():
    async with AsyncClient() as client:
        response = await client.post(url=user_sign_up, json=olivia_data)
    assert response.status_code == 200
    assert 'access_token' in response.json().keys()
    assert 'refresh_token' in response.json().keys()
    access_token = response.json()['access_token']

    async with AsyncClient() as client:
        response = await client.get(url=balance, cookies={'refresh_token': access_token})
        assert response.status_code == 401

    async with AsyncClient() as client:
        response = await client.get(url=balance, cookies={'access_token': access_token})
    assert response.status_code == 200
    assert response.json()['balance'] == 0
