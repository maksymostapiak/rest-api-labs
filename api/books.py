from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
import uuid

from schemas.book import BookCreate, BookResponse, BookStatus
from services.book_service import BookService

router = APIRouter(prefix="/books", tags=["Books"])

def get_book_service():
    return BookService()

@router.get("/", response_model=List[BookResponse], status_code=status.HTTP_200_OK)
async def get_books(
    status_filter: Optional[BookStatus] = Query(None, alias="status"),
    author: Optional[str] = None,
    sort_by: Optional[str] = Query(None, description="Доступні значення: title, year"),
    service: BookService = Depends(get_book_service)
):
    return await service.get_all_books(status=status_filter, author=author, sort_by=sort_by)

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