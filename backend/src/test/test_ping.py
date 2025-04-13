import pytest
from global_config import settings
from httpx import AsyncClient

IP_ADDRESS = settings.IP_ADDRESS
SERVER_PORT = settings.SERVER_PORT


@pytest.mark.asyncio
async def test_ping():
    url = f"http://{IP_ADDRESS}:{SERVER_PORT}/ping"
    for i in range(10):
        async with AsyncClient() as client:
            response = await client.get(url)
        assert response.status_code == 200
