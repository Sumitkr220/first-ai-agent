import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MongoDB connection and provides database access."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            # MongoDB Atlas connection with TLS/SSL compatibility fixes
            connection_params = {
                'serverSelectionTimeoutMS': 15000,
                'maxPoolSize': 10,
                'minPoolSize': 1,
                'tls': True,
                'tlsAllowInvalidCertificates': True,
                'tlsAllowInvalidHostnames': True
            }
            
            self.client = MongoClient(
                settings.mongodb_uri,
                **connection_params
            )
            
            # Test the connection
            self.client.admin.command('ping')
            self.database = self.client[settings.mongodb_database]
            
            logger.info(f"Successfully connected to MongoDB database: {settings.mongodb_database}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            # Don't raise immediately, try to continue without database
            logger.warning("Continuing without database connection - some features may not work")
            self.database = None
        except Exception as e:
            logger.error(f"Unexpected error during database connection: {e}")
            logger.warning("Continuing without database connection - some features may not work")
            self.database = None
    
    def get_database(self) -> Database:
        """Get the database instance."""
        if self.database is None:
            try:
                self._connect()
            except Exception as e:
                logger.error(f"Failed to reconnect to database: {e}")
                return None
        return self.database
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database."""
        db = self.get_database()
        if db is None:
            raise ConnectionError("Database connection not available")
        return db[collection_name]
    
    def list_collections(self) -> list:
        """List all collections in the database."""
        try:
            db = self.get_database()
            if db is None:
                logger.warning("Database not connected, returning empty collection list")
                return []
            return db.list_collection_names()
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    def get_collection_schema(self, collection_name: str) -> dict:
        """Get schema information for a collection."""
        try:
            collection = self.get_collection(collection_name)
            # Get a sample document to understand the schema
            sample_doc = collection.find_one()
            if sample_doc:
                return {
                    "collection_name": collection_name,
                    "fields": list(sample_doc.keys()),
                    "sample_document": sample_doc
                }
            return {"collection_name": collection_name, "fields": [], "sample_document": None}
        except ConnectionError:
            logger.warning(f"Database not connected, returning empty schema for {collection_name}")
            return {"collection_name": collection_name, "fields": [], "sample_document": None}
        except Exception as e:
            logger.error(f"Error getting schema for collection {collection_name}: {e}")
            return {"collection_name": collection_name, "fields": [], "sample_document": None}
    
    def close(self) -> None:
        """Close the database connection."""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")


# Global database manager instance
db_manager = DatabaseManager() 