import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text

from main import app
from models.database import async_session

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

@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def clear_db():
    async with async_session() as session:
        await session.execute(text("DELETE FROM books"))
        await session.commit()

# --- ТЕСТИ ---

async def test_unauthorized_access(client: AsyncClient):
    response = await client.get("/books/")
    assert response.status_code == 401

async def test_create_book(client: AsyncClient, auth_headers):
    response = await client.post("/books/", json={
        "title": "Кобзар",
        "author": "Тарас Шевченко",
        "description": "Збірка поетичних творів",
        "status": "наявні в бібліотеці",
        "year": 1840
    }, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Кобзар"
    assert "id" in data

async def test_get_books(client: AsyncClient, auth_headers):
    await client.post("/books/", json={"title": "1984", "author": "Джордж Орвелл", "year": 1949, "status": "наявні в бібліотеці"}, headers=auth_headers)
    await client.post("/books/", json={"title": "Кобзар", "author": "Тарас Шевченко", "year": 1840, "status": "видані комусь"}, headers=auth_headers)
    
    response = await client.get("/books/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["items"]) == 2

    response = await client.get("/books/?status=видані комусь", headers=auth_headers)
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["title"] == "Кобзар"

async def test_get_book_by_id(client: AsyncClient, auth_headers):
    create_response = await client.post("/books/", json={
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "status": "наявні в бібліотеці"
    }, headers=auth_headers)
    book_id = create_response.json()["id"]

    response = await client.get(f"/books/{book_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == book_id

    fake_id = str(uuid.uuid4())
    response = await client.get(f"/books/{fake_id}", headers=auth_headers)
    assert response.status_code == 404

async def test_delete_book_idempotent(client: AsyncClient, auth_headers):
    create_response = await client.post("/books/", json={
        "title": "Test Book",
        "author": "Test Author",
        "year": 2024,
        "status": "наявні в бібліотеці"
    }, headers=auth_headers)
    book_id = create_response.json()["id"]

    response1 = await client.delete(f"/books/{book_id}", headers=auth_headers)
    assert response1.status_code == 204

    check_response = await client.get(f"/books/{book_id}", headers=auth_headers)
    assert check_response.status_code == 404

    response2 = await client.delete(f"/books/{book_id}", headers=auth_headers)
    assert response2.status_code == 204