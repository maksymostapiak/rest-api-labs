import pytest
from fastapi.testclient import TestClient
from main import app
from models.database import books_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():

    books_db.clear()

def test_create_book():
    response = client.post("/books/", json={
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

def test_get_books():
    client.post("/books/", json={"title": "1984", "author": "Джордж Орвелл", "year": 1949, "status": "наявні в бібліотеці"})
    client.post("/books/", json={"title": "Кобзар", "author": "Тарас Шевченко", "year": 1840, "status": "видані комусь"})
    
    response = client.get("/books/")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get("/books/?status=видані комусь")
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Кобзар"

    response = client.get("/books/?sort_by=year")
    assert response.json()[0]["year"] == 1840

def test_get_book_by_id():
    create_response = client.post("/books/", json={
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "status": "наявні в бібліотеці"
    })
    book_id = create_response.json()["id"]

    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["id"] == book_id

    import uuid
    fake_id = str(uuid.uuid4())
    response = client.get(f"/books/{fake_id}")
    assert response.status_code == 404

def test_delete_book_idempotent():
    create_response = client.post("/books/", json={
        "title": "Test Book",
        "author": "Test Author",
        "year": 2024,
        "status": "наявні в бібліотеці"
    })
    book_id = create_response.json()["id"]

    response1 = client.delete(f"/books/{book_id}")
    assert response1.status_code == 204

    assert client.get(f"/books/{book_id}").status_code == 404

    response2 = client.delete(f"/books/{book_id}")
    assert response2.status_code == 204