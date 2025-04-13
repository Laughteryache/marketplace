import pytest
from global_config import settings
from httpx import AsyncClient

from .testers import alex_data, john_data, steve_data, luca_data

IP_ADDRESS = settings.IP_ADDRESS
SERVER_PORT = settings.SERVER_PORT

sign_up = f"http://{IP_ADDRESS}:{SERVER_PORT}/v1/api/auth/user/sign-up"
sign_in = f"http://{IP_ADDRESS}:{SERVER_PORT}/v1/api/auth/user/sign-in"



@pytest.mark.asyncio
async def test_john_sign_up():
    async with AsyncClient() as client:
        response = await client.post(url=sign_up, json=john_data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_john_sign_in():
    async with AsyncClient() as client:
        response = await client.post(url=sign_in, json=john_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_no_json_sign_up():
    async with AsyncClient() as client:
        response = await client.post(url=sign_up, json={})
    assert response.status_code == 422



@pytest.mark.asyncio
async def test_wtf_sign_in():
    async with AsyncClient() as client:
        put_response = await client.put(url=sign_in, json=alex_data)
        patch_response = await client.patch(url=sign_in, json=alex_data)
        get_response = await client.get(url=sign_in)
        head_response = await client.head(url=sign_in)
    assert put_response.status_code == 405
    assert patch_response.status_code == 405
    assert get_response.status_code == 405
    assert head_response.status_code == 405


@pytest.mark.asyncio
async def test_wtf_sign_up():
    async with AsyncClient() as client:
        put_response = await client.put(url=sign_up, json=alex_data)
        patch_response = await client.patch(url=sign_up, json=alex_data)
        get_response = await client.get(url=sign_up)
        head_response = await client.head(url=sign_up)
    assert put_response.status_code == 405
    assert patch_response.status_code == 405
    assert get_response.status_code == 405
    assert head_response.status_code == 405


@pytest.mark.asyncio
async def test_steve_sign_up():
    async with AsyncClient() as client:
        response = await client.post(url=sign_up, json=steve_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_luca_sign_in():
    async with AsyncClient() as client:
        response = await client.post(url=sign_in, json=luca_data)
    assert response.status_code == 422
