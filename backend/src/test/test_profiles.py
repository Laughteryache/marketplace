import pytest
from global_config import settings
from httpx import AsyncClient

from .testers import mike_data

IP_ADDRESS = settings.IP_ADDRESS
SERVER_PORT = settings.SERVER_PORT

profile = f'http://{IP_ADDRESS}:{SERVER_PORT}/v1/api/profile/business'


@pytest.mark.asyncio
async def test_get_profile():
    id = 1
    async with AsyncClient() as client:
        response = await client.get(url=f'{profile}?id={id}')
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_profile_image():
    id = 1
    async with AsyncClient() as client:
        response = await client.get(url=f'{profile}/image?id={id}')
    assert response.status_code == 404
    id = 999
    async with AsyncClient() as client:
        response = await client.get(url=f'{profile}/image?id={id}')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_business_profile():
    async with AsyncClient() as client:
        response = await client.post(
            url=f"http://{IP_ADDRESS}:{SERVER_PORT}/v1/api/auth/business/sign-up",
            json=mike_data)
        assert response.status_code == 200
        assert 'access_token' in response.json().keys()
        assert 'refresh_token' in response.json().keys()
    access_token = response.json()['access_token']

    async with AsyncClient() as client:
        response = await client.patch(
            url=profile,
            cookies={'access_token': access_token},
            json={
                'title': 'Лучший бизнес',
                'description': 'Скупай всё',
                'location': 'Tchaikovsky, azino street'})
        assert response.status_code == 200
