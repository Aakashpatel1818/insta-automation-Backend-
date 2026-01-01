"""MongoDB connection and initialization"""

from motor.motor_asyncio import AsyncClient, AsyncDatabase
from app.core.config import settings

client: AsyncClient = None
db: AsyncDatabase = None

async def connect_to_mongo():
    """Connect to MongoDB"""
    global client, db
    client = AsyncClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]
    print(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")

async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")

def get_db() -> AsyncDatabase:
    """Get database instance"""
    return db