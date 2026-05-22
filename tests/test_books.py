import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from main import app

pytestmark = pytest.mark.asyncio(loop_scope="session")

@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def auth_headers(client: AsyncClient):
    response = await client.post("/auth/token", data={"username": "admin", "password": "secret"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture(loop_scope="session")
async def limit_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
        yield ac

# --- ТЕСТИ ---

async def test_anonymous_rate_limit(limit_client: AsyncClient):
    """
    Перевірка лімітів для анонімного юзера (ліміт: 2 запити на хвилину).
    """
    for _ in range(3):
        response = await limit_client.get("/books/")
        assert response.status_code == 401 

    response_blocked = await limit_client.get("/books/")
    assert response_blocked.status_code == 429
    assert "Anonymous limit" in response_blocked.json()["detail"]


async def test_authorized_rate_limit(limit_client: AsyncClient, auth_headers):
    """
    Перевірка лімітів для авторизованого юзера (ліміт: 10 запитів на хвилину).
    """
    for _ in range(11):
        response = await limit_client.get("/books/", headers=auth_headers)
        assert response.status_code == 200

    response_blocked = await limit_client.get("/books/", headers=auth_headers)
    assert response_blocked.status_code == 429
    assert "Authorized limit" in response_blocked.json()["detail"]