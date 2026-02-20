"""MongoDB connection and get_db helper for Token Trail."""
from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import MONGO_URI, MONGO_DB

# Global client (reused across requests)
_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    """Get or create the MongoDB client."""
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client


def get_db() -> Database:
    """Get the MongoDB database instance."""
    client = get_mongo_client()
    return client[MONGO_DB]
