import logging
import time
import json
from typing import List, Dict, Any, Optional
from pymongo.errors import PyMongoError
from bson import ObjectId, Decimal128
from datetime import datetime

from app.database.connection import db_manager
from app.database.schemas import QueryResult, CollectionSchema

logger = logging.getLogger(__name__)


def convert_bson_to_json(obj):
    """Convert BSON types to JSON-serializable types."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, Decimal128):
        return float(str(obj))
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_bson_to_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_bson_to_json(item) for item in obj]
    else:
        return obj


class DatabaseService:
    """Service for database operations and query execution."""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def get_all_collections(self) -> List[str]:
        """Get all collection names from the database."""
        try:
            return self.db_manager.list_collections()
        except Exception as e:
            logger.error(f"Error getting collections: {e}")
            return []
    
    def get_collection_schema(self, collection_name: str) -> CollectionSchema:
        """Get schema information for a specific collection."""
        try:
            schema_info = self.db_manager.get_collection_schema(collection_name)
            collection = self.db_manager.get_collection(collection_name)
            
            # Get document count
            document_count = collection.count_documents({})
            
            # Convert sample document to JSON-serializable format
            sample_document = schema_info.get("sample_document")
            if sample_document:
                sample_document = convert_bson_to_json(sample_document)
            
            return CollectionSchema(
                collection_name=collection_name,
                fields=schema_info.get("fields", []),
                sample_document=sample_document,
                document_count=document_count
            )
        except Exception as e:
            logger.error(f"Error getting schema for collection {collection_name}: {e}")
            return CollectionSchema(collection_name=collection_name)
    
    def execute_find_query(self, collection_name: str, query: Dict[str, Any], 
                          limit: int = 100) -> QueryResult:
        """Execute a find query on a collection."""
        start_time = time.time()
        
        try:
            collection = self.db_manager.get_collection(collection_name)
            
            # Execute the query
            cursor = collection.find(query).limit(limit)
            results = list(cursor)
            
            # Convert all BSON types to JSON-serializable format
            results = convert_bson_to_json(results)
            
            execution_time = time.time() - start_time
            
            return QueryResult(
                query=str(query),
                result=results,
                total_count=len(results),
                execution_time=execution_time
            )
            
        except PyMongoError as e:
            logger.error(f"MongoDB error executing find query: {e}")
            return QueryResult(
                query=str(query),
                error=f"Database error: {str(e)}",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Unexpected error executing find query: {e}")
            return QueryResult(
                query=str(query),
                error=f"Unexpected error: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    def execute_aggregate_query(self, collection_name: str, pipeline: List[Dict[str, Any]]) -> QueryResult:
        """Execute an aggregation pipeline on a collection."""
        start_time = time.time()
        
        try:
            collection = self.db_manager.get_collection(collection_name)
            
            # Execute the aggregation
            cursor = collection.aggregate(pipeline)
            results = list(cursor)
            
            # Convert all BSON types to JSON-serializable format
            results = convert_bson_to_json(results)
            
            execution_time = time.time() - start_time
            
            return QueryResult(
                query=str(pipeline),
                result=results,
                total_count=len(results),
                execution_time=execution_time
            )
            
        except PyMongoError as e:
            logger.error(f"MongoDB error executing aggregate query: {e}")
            return QueryResult(
                query=str(pipeline),
                error=f"Database error: {str(e)}",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Unexpected error executing aggregate query: {e}")
            return QueryResult(
                query=str(pipeline),
                error=f"Unexpected error: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    def execute_count_query(self, collection_name: str, query: Dict[str, Any] = None) -> QueryResult:
        """Execute a count query on a collection."""
        start_time = time.time()
        
        try:
            collection = self.db_manager.get_collection(collection_name)
            
            # Execute the count
            count = collection.count_documents(query or {})
            
            execution_time = time.time() - start_time
            
            return QueryResult(
                query=f"count_documents({query or {}})",
                result=[{"count": count}],
                total_count=1,
                execution_time=execution_time
            )
            
        except PyMongoError as e:
            logger.error(f"MongoDB error executing count query: {e}")
            return QueryResult(
                query=f"count_documents({query or {}})",
                error=f"Database error: {str(e)}",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Unexpected error executing count query: {e}")
            return QueryResult(
                query=f"count_documents({query or {}})",
                error=f"Unexpected error: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get comprehensive database information."""
        try:
            collections = self.get_all_collections()
            schemas = {}
            
            for collection_name in collections:
                schema = self.get_collection_schema(collection_name)
                # Convert schema to dict and ensure it's JSON-serializable
                schema_dict = schema.dict()
                schemas[collection_name] = convert_bson_to_json(schema_dict)
            
            return {
                "database_name": self.db_manager.get_database().name,
                "collections": collections,
                "schemas": schemas
            }
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {"error": str(e)}


# Global database service instance
db_service = DatabaseService() 