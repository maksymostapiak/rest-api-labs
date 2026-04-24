from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import uuid

class BookStatus(str, Enum):
    AVAILABLE = "наявні в бібліотеці"
    BORROWED = "видані комусь"

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, description="Назва книги")
    author: str = Field(..., min_length=1, description="Автор книги")
    description: Optional[str] = Field(None, description="Опис книги")
    status: BookStatus = Field(default=BookStatus.AVAILABLE, description="Статус книги")
    year: int = Field(..., gt=0, description="Рік випуску")

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: uuid.UUID