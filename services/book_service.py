from typing import List, Optional
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase
from schemas.book import BookCreate, BookResponse, BookStatus
from repository.book_repo import BookRepository

class BookService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = BookRepository(db)

    async def get_all_books(
        self, limit: int, offset: int, status: Optional[BookStatus] = None, author: Optional[str] = None
    ) -> List[BookResponse]:
        status_value = status.value if status else None
        books = await self.repo.get_all(limit, offset, status_value, author)
        return [BookResponse(**book) for book in books]

    async def get_book_by_id(self, book_id: uuid.UUID) -> Optional[BookResponse]:
        book = await self.repo.get_by_id(str(book_id))
        if book:
            return BookResponse(**book)
        return None

    async def create_book(self, book_data: BookCreate) -> BookResponse:
        book_dict = book_data.model_dump()
        created_book = await self.repo.add(book_dict)
        return BookResponse(**created_book)

    async def delete_book(self, book_id: uuid.UUID) -> None:
        await self.repo.delete(str(book_id))