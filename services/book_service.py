import uuid
from typing import List, Optional
from schemas.book import BookCreate, BookResponse, BookStatus
from repository.book_repo import BookRepository

class BookService:
    def __init__(self):
        self.repo = BookRepository()

    async def get_all_books(
        self, 
        status: Optional[BookStatus] = None, 
        author: Optional[str] = None,
        sort_by: Optional[str] = None
    ) -> List[BookResponse]:
        books = await self.repo.get_all()
        
        if status:
            books = [b for b in books if b["status"] == status]
        if author:
            books = [b for b in books if author.lower() in b["author"].lower()]
            
        if sort_by == "title":
            books.sort(key=lambda x: x["title"])
        elif sort_by == "year":
            books.sort(key=lambda x: x["year"])

        return [BookResponse(**book) for book in books]

    async def get_book_by_id(self, book_id: uuid.UUID) -> Optional[BookResponse]:
        book = await self.repo.get_by_id(book_id)
        if book:
            return BookResponse(**book)
        return None

    async def create_book(self, book_data: BookCreate) -> BookResponse:
        book_dict = book_data.model_dump()
        book_dict["id"] = uuid.uuid4()
        
        created_book = await self.repo.add(book_dict)
        return BookResponse(**created_book)

    async def delete_book(self, book_id: uuid.UUID) -> None:

        await self.repo.delete(book_id)