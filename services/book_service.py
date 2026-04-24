import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.book import BookCreate, BookResponse, BookStatus
from repository.book_repo import BookRepository
from schemas.book import BookCreate, BookResponse, BookCursorResponse

class BookService:
    def __init__(self, db: AsyncSession):
        self.repo = BookRepository(db)

    async def get_all_books(
        self, 
        limit: int,
        cursor: Optional[uuid.UUID] = None,
        status: Optional[BookStatus] = None, 
        author: Optional[str] = None
    ) -> BookCursorResponse:
        
        status_value = status.value if status else None
        books = await self.repo.get_all(limit, cursor, status_value, author)
        
        items = [BookResponse.model_validate(book) for book in books]
        
        # Визначаємо наступний курсор (id останнього елемента в списку)
        next_cursor = items[-1].id if len(items) == limit else None

        return BookCursorResponse(items=items, next_cursor=next_cursor)

    async def get_book_by_id(self, book_id: uuid.UUID) -> Optional[BookResponse]:
        book = await self.repo.get_by_id(book_id)
        if book:
            return BookResponse.model_validate(book)
        return None

    async def create_book(self, book_data: BookCreate) -> BookResponse:
        book_dict = book_data.model_dump()
        created_book = await self.repo.add(book_dict)
        return BookResponse.model_validate(created_book)

    async def delete_book(self, book_id: uuid.UUID) -> None:
        await self.repo.delete(book_id)