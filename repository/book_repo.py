from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from models.book_model import BookDB, BookStatus

class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, 
        limit: int, 
        cursor: Optional[uuid.UUID] = None, 
        status: str = None, 
        author: str = None
    ) -> List[BookDB]:
        query = self.db.query(BookDB)

        if status:
            query = query.filter(BookDB.status == status)
        if author:
            query = query.filter(BookDB.author.ilike(f"%{author}%"))

        if cursor:
            query = query.filter(BookDB.id > cursor)

        return query.order_by(BookDB.id).limit(limit).all()

    def get_by_id(self, book_id: uuid.UUID) -> Optional[BookDB]:
        return self.db.query(BookDB).filter(BookDB.id == book_id).first()

    def add(self, book_data: dict) -> BookDB:
        new_book = BookDB(**book_data)
        self.db.add(new_book)
        self.db.commit()
        self.db.refresh(new_book)
        return new_book

    def delete(self, book_id: uuid.UUID) -> bool:
        book = self.get_by_id(book_id)
        if book:
            self.db.delete(book)
            self.db.commit()
            return True
        return False