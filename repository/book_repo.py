from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
import uuid

class BookRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.books

    async def get_all(self, limit: int, offset: int, status: str = None, author: str = None) -> List[dict]:
        query = {}
        if status:
            query["status"] = status
        if author:
            query["author"] = {"$regex": author, "$options": "i"}

        cursor = self.collection.find(query).skip(offset).limit(limit)
        books = await cursor.to_list(length=limit)
        return books

    async def get_by_id(self, book_id: str) -> Optional[dict]:
        return await self.collection.find_one({"id": book_id})

    async def add(self, book_data: dict) -> dict:
        book_data["id"] = str(uuid.uuid4())
        await self.collection.insert_one(book_data.copy())
        return book_data

    async def delete(self, book_id: str) -> bool:
        result = await self.collection.delete_one({"id": book_id})
        return result.deleted_count > 0