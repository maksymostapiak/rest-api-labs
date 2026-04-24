from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from models.book_db import BookDB

class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, limit: int, offset: int, status: str = None, author: str = None, sort_by: str = None) -> List[BookDB]:
        query = select(BookDB)

        if status:
            query = query.where(BookDB.status == status)
        if author:
            query = query.where(BookDB.author.ilike(f"%{author}%")) 

        if sort_by == "title":
            query = query.order_by(BookDB.title)
        elif sort_by == "year":
            query = query.order_by(BookDB.year)

        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, book_id: uuid.UUID) -> Optional[BookDB]:
        result = await self.db.execute(select(BookDB).where(BookDB.id == book_id))
        return result.scalars().first()

    async def add(self, book_data: dict) -> BookDB:
        new_book = BookDB(**book_data)
        self.db.add(new_book)
        await self.db.commit()
        await self.db.refresh(new_book)
        return new_book

    async def delete(self, book_id: uuid.UUID) -> bool:
        result = await self.db.execute(delete(BookDB).where(BookDB.id == book_id))
        await self.db.commit()
        return result.rowcount > 0