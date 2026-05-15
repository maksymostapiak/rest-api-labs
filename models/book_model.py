import uuid
import enum
from sqlalchemy import Column, String, Integer, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from models.database import Base

class BookStatus(str, enum.Enum):
    AVAILABLE = "наявні в бібліотеці"
    BORROWED = "видані комусь"

class BookDB(Base):
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(SAEnum(BookStatus), default=BookStatus.AVAILABLE, nullable=False)
    year = Column(Integer, nullable=False)

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "status": self.status.value if self.status else None,
            "year": self.year
        }