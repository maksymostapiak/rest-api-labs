from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from schemas.book import BookCreate, BookResponse, BookStatus
from services.book_service import BookService
from models.database import get_db
from schemas.book import BookCreate, BookResponse, BookCursorResponse

router = APIRouter(prefix="/books", tags=["Books"])

def get_book_service(db: AsyncSession = Depends(get_db)):
    return BookService(db)

@router.get("/", response_model=BookCursorResponse, status_code=status.HTTP_200_OK)
async def get_books(
    limit: int = Query(10, ge=1, le=100),
    cursor: Optional[uuid.UUID] = Query(None, description="ID останньої книги з попередньої сторінки"),
    status_filter: Optional[BookStatus] = Query(None, alias="status"),
    author: Optional[str] = None,
    service: BookService = Depends(get_book_service)
):
    return await service.get_all_books(
        limit=limit, 
        cursor=cursor, 
        status=status_filter, 
        author=author
    )

@router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def get_book(book_id: uuid.UUID, service: BookService = Depends(get_book_service)):
    book = await service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книгу не знайдено")
    return book

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, service: BookService = Depends(get_book_service)):
    return await service.create_book(book)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: uuid.UUID, service: BookService = Depends(get_book_service)):

    await service.delete_book(book_id)
    return