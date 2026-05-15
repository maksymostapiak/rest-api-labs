from fastapi import FastAPI
from api.books import router as books_router
from api.auth import router as auth_router
from models.database import engine, Base
import contextlib

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(books_router)