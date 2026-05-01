import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://admin:adminpassword@localhost:27017/")

client = AsyncIOMotorClient(MONGO_URL)
db = client.library_db

async def get_db():
    yield db