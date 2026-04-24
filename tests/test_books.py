import pytest
import httpx
import uuid
from httpx import ASGITransport
from main import app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from models.database import Base, get_db

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgrespassword@localhost:5432/library_db"
engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="function", autouse=True)
async def setup_db():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db

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
async def test_get_books_with_cursor_pagination(async_client):
    await async_client.post("/books/", json={"title": "Книга 1", "author": "Автор", "year": 2001})
    await async_client.post("/books/", json={"title": "Книга 2", "author": "Автор", "year": 2002})
    await async_client.post("/books/", json={"title": "Книга 3", "author": "Автор", "year": 2003})
    
    response_page1 = await async_client.get("/books/?limit=2")
    assert response_page1.status_code == 200
    data_page1 = response_page1.json()
    

    assert len(data_page1["items"]) == 2

    assert data_page1["next_cursor"] is not None

    next_cursor = data_page1["next_cursor"]
    response_page2 = await async_client.get(f"/books/?limit=2&cursor={next_cursor}")
    assert response_page2.status_code == 200
    data_page2 = response_page2.json()

    assert len(data_page2["items"]) == 1
    assert data_page2["next_cursor"] is None


@pytest.mark.asyncio
async def test_get_books_filtering(async_client):
    await async_client.post("/books/", json={"title": "1984", "author": "Джордж Орвелл", "year": 1949, "status": "наявні в бібліотеці"})
    await async_client.post("/books/", json={"title": "Кобзар", "author": "Тарас Шевченко", "year": 1840, "status": "видані комусь"})
    
    response = await async_client.get("/books/?status=видані комусь")
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Кобзар"

    response = await async_client.get("/books/?author=Орвелл")
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "1984"


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
    create_res = await async_client.post("/books/", json={"title": "Del", "author": "Auth", "year": 2000})
    book_id = create_res.json()["id"]

    del_res = await async_client.delete(f"/books/{book_id}")
    assert del_res.status_code == 204

    get_res = await async_client.get(f"/books/{book_id}")
    assert get_res.status_code == 404