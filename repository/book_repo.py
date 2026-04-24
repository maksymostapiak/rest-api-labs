from typing import List, Dict, Optional
import uuid
from models.database import books_db

class BookRepository:
    async def get_all(self) -> List[Dict]:
        return books_db

    async def get_by_id(self, book_id: uuid.UUID) -> Optional[Dict]:
        for book in books_db:
            if book["id"] == book_id:
                return book
        return None

    async def add(self, book_data: Dict) -> Dict:
        books_db.append(book_data)
        return book_data

    async def delete(self, book_id: uuid.UUID) -> bool:
        global books_db
        initial_length = len(books_db)

        books_db[:] = [book for book in books_db if book["id"] != book_id]

        return len(books_db) < initial_length