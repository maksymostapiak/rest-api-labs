import pytest
import httpx
import uuid
from httpx import ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

from main import app
from models.database import get_db


TEST_MONGO_URL = "mongodb://admin:adminpassword@localhost:27017/"
test_client = AsyncIOMotorClient(TEST_MONGO_URL)
test_db = test_client.test_library_db

async def override_get_db():
    yield test_db


app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function", autouse=True)
async def setup_db():

    await test_db.books.delete_many({})
    yield

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_book(async_client):
    response = await async_client.post("/books/", json={
        "title": "Кобзар",
        "author": "Тарас Шевченко",
        "description": "Збірка поетичних творів",
        "status": "наявні в бібліотеці",
        "year": 1840
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Кобзар"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_books_limit_offset(async_client):

    await async_client.post("/books/", json={"title": "Книга 1", "author": "Автор", "year": 2001})
    await async_client.post("/books/", json={"title": "Книга 2", "author": "Автор", "year": 2002})
    await async_client.post("/books/", json={"title": "Книга 3", "author": "Автор", "year": 2003})

    response_page1 = await async_client.get("/books/?limit=2&offset=0")
    assert response_page1.status_code == 200
    data_page1 = response_page1.json()
    assert len(data_page1) == 2
    assert data_page1[0]["title"] == "Книга 1"
    assert data_page1[1]["title"] == "Книга 2"

    response_page2 = await async_client.get("/books/?limit=2&offset=2")
    assert response_page2.status_code == 200
    data_page2 = response_page2.json()
    assert len(data_page2) == 1
    assert data_page2[0]["title"] == "Книга 3"


@pytest.mark.asyncio
async def test_get_books_filtering(async_client):
    await async_client.post("/books/", json={"title": "1984", "author": "Джордж Орвелл", "year": 1949, "status": "наявні в бібліотеці"})
    await async_client.post("/books/", json={"title": "Кобзар", "author": "Тарас Шевченко", "year": 1840, "status": "видані комусь"})
    
    response_status = await async_client.get("/books/?status=видані комусь")
    assert response_status.status_code == 200
    data_status = response_status.json()
    assert len(data_status) == 1
    assert data_status[0]["title"] == "Кобзар"

    response_author = await async_client.get("/books/?author=Орвелл")
    assert response_author.status_code == 200
    data_author = response_author.json()
    assert len(data_author) == 1
    assert data_author[0]["title"] == "1984"


@pytest.mark.asyncio
async def test_get_book_by_id(async_client):
    create_res = await async_client.post("/books/", json={"title": "Dune", "author": "Frank Herbert", "year": 1965})
    book_id = create_res.json()["id"]

    response = await async_client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["id"] == book_id

    fake_id = str(uuid.uuid4())
    response = await async_client.get(f"/books/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_book(async_client):
    create_res = await async_client.post("/books/", json={"title": "Delete Me", "author": "Author", "year": 2000})
    book_id = create_res.json()["id"]

    del_res = await async_client.delete(f"/books/{book_id}")
    assert del_res.status_code == 204
    get_res = await async_client.get(f"/books/{book_id}")
    assert get_res.status_code == 404