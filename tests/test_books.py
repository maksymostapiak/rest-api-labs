import pytest
import uuid
from main import app
from models.database import SessionLocal, engine, Base
from models.book_model import BookDB

@pytest.fixture(scope="module")
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        Base.metadata.create_all(bind=engine)
        yield client

@pytest.fixture(autouse=True)
def clear_db():
    db = SessionLocal()
    try:
        db.query(BookDB).delete()
        db.commit()
    finally:
        db.close()

def test_create_book(test_client):
    response = test_client.post("/books", json={
        "title": "Кобзар",
        "author": "Тарас Шевченко",
        "description": "Збірка поетичних творів",
        "status": "наявні в бібліотеці",
        "year": 1840
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Кобзар"
    assert "id" in data

def test_get_books(test_client):
    test_client.post("/books", json={"title": "1984", "author": "Джордж Орвелл", "year": 1949, "status": "наявні в бібліотеці"})
    test_client.post("/books", json={"title": "Кобзар", "author": "Тарас Шевченко", "year": 1840, "status": "видані комусь"})
    
    response = test_client.get("/books")
    assert response.status_code == 200
    data = response.get_json()

    assert len(data["items"]) == 2

    response = test_client.get("/books?status=видані комусь")
    data = response.get_json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Кобзар"

def test_get_book_by_id(test_client):
    create_response = test_client.post("/books", json={
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "status": "наявні в бібліотеці"
    })
    book_id = create_response.get_json()["id"]

    response = test_client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.get_json()["id"] == book_id

    fake_id = str(uuid.uuid4())
    response = test_client.get(f"/books/{fake_id}")
    assert response.status_code == 404

def test_delete_book(test_client):
    create_response = test_client.post("/books", json={
        "title": "Test Book",
        "author": "Test Author",
        "year": 2024,
        "status": "наявні в бібліотеці"
    })
    book_id = create_response.get_json()["id"]

    response1 = test_client.delete(f"/books/{book_id}")
    assert response1.status_code == 200
    assert response1.get_json()["message"] == "Книгу видалено"


    assert test_client.get(f"/books/{book_id}").status_code == 404

    response2 = test_client.delete(f"/books/{book_id}")
    assert response2.status_code == 404