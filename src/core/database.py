from typing import Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import settings

class DatabaseManager:
    _client: Optional[MongoClient] = None
    
    @classmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def get_client(cls) -> MongoClient:
        if cls._client is None:
            try:
                cls._client = MongoClient(
                    settings.MONGO_URI,
                    tlsAllowInvalidCertificates=True,
                    serverSelectionTimeoutMS=5000
                )
                # Verify connection
                cls._client.admin.command('ping')
            except ConnectionFailure as e:
                raise ConnectionFailure(f"Failed to connect to MongoDB: {e}")
        return cls._client
    
    @classmethod
    def get_db(cls):
        return cls.get_client()[settings.DB_NAME]
    
    @classmethod
    def close(cls):
        if cls._client is not None:
            cls._client.close()
            cls._client = None

# Create a singleton instance
db = DatabaseManager() 