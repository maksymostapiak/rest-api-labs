from fastapi import FastAPI
from api.books import router as books_router

app = FastAPI(title="Library API")

app.include_router(books_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)