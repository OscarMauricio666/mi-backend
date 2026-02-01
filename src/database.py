"""
MongoDB Atlas Connection with Beanie ODM.

Provides database client, connection/disconnection, and Beanie initialization.
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie

from src.config import get_settings
from src.documents import ALL_DOCUMENTS

settings = get_settings()


class Database:
    """MongoDB Atlas connection manager."""

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    connected: bool = False


db = Database()


async def connect_to_mongo():
    """Establish connection with MongoDB Atlas and initialize Beanie."""
    try:
        if not settings.mongodb_url or "usuario:password" in settings.mongodb_url or "<" in settings.mongodb_url:
            print("MongoDB: Using example credentials - connection skipped")
            return

        db.client = AsyncIOMotorClient(settings.mongodb_url, serverSelectionTimeoutMS=5000)
        await db.client.admin.command('ping')
        db.db = db.client[settings.database_name]

        # Initialize Beanie with document models
        await init_beanie(database=db.db, document_models=ALL_DOCUMENTS)

        db.connected = True
        print(f"Connected to MongoDB Atlas - Database: {settings.database_name}")
        print(f"Beanie initialized with {len(ALL_DOCUMENTS)} document models")
    except Exception as e:
        print(f"MongoDB: Could not connect - {e}")
        db.connected = False


async def close_mongo_connection():
    """Close MongoDB Atlas connection."""
    if db.client:
        db.client.close()
        print("MongoDB Atlas connection closed")


def get_database() -> Optional[AsyncIOMotorDatabase]:
    """Get database instance."""
    return db.db
