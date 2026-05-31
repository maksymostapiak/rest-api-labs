import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLITE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'library.db')}"

DATABASE_URL = os.getenv("DATABASE_URL", SQLITE_URL)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()