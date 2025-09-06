#!/usr/bin/env python3
"""
Database utilities for DB-AI-AGENT
Handles database operations and data management
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from bson import ObjectId, Decimal128
from datetime import datetime
from typing import Dict, List, Any
from app.config import settings

class DatabaseManager:
    """Database management utilities"""
    
    def __init__(self):
        self.client = MongoClient(settings.mongodb_uri)
        self.db = self.client[settings.mongodb_database]
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        collections = self.db.list_collection_names()
        info = {
            "database": settings.mongodb_database,
            "collections": collections,
            "total_collections": len(collections)
        }
        
        for collection in collections:
            count = self.db[collection].count_documents({})
            info[f"{collection}_count"] = count
        
        return info
    
    def get_collection_schema(self, collection_name: str) -> Dict[str, Any]:
        """Get collection schema"""
        try:
            # Get sample documents to understand schema
            sample_docs = list(self.db[collection_name].find().limit(5))
            
            if not sample_docs:
                return {"error": f"No documents found in {collection_name}"}
            
            # Analyze schema from sample documents
            schema = self._analyze_schema(sample_docs)
            
            return {
                "collection": collection_name,
                "document_count": self.db[collection_name].count_documents({}),
                "schema": schema
            }
            
        except Exception as e:
            return {"error": f"Error analyzing schema: {str(e)}"}
    
    def _analyze_schema(self, documents: List[Dict]) -> Dict[str, Any]:
        """Analyze document schema"""
        if not documents:
            return {}
        
        # Get all unique fields
        all_fields = set()
        for doc in documents:
            self._extract_fields(doc, all_fields)
        
        # Analyze field types
        schema = {}
        for field in all_fields:
            field_type = self._get_field_type(documents, field)
            schema[field] = field_type
        
        return schema
    
    def _extract_fields(self, obj: Any, fields: set, prefix: str = ""):
        """Recursively extract field names"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                field_name = f"{prefix}.{key}" if prefix else key
                fields.add(field_name)
                self._extract_fields(value, fields, field_name)
        elif isinstance(obj, list) and obj:
            self._extract_fields(obj[0], fields, prefix)
    
    def _get_field_type(self, documents: List[Dict], field: str) -> str:
        """Get the type of a field"""
        values = []
        for doc in documents:
            value = self._get_nested_value(doc, field)
            if value is not None:
                values.append(type(value).__name__)
        
        if not values:
            return "unknown"
        
        # Return the most common type
        from collections import Counter
        type_counts = Counter(values)
        return type_counts.most_common(1)[0][0]
    
    def _get_nested_value(self, obj: Any, field: str) -> Any:
        """Get nested value using dot notation"""
        keys = field.split('.')
        current = obj
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            # Test connection by listing collections
            collections = self.db.list_collection_names()
            print(f"✅ Database connection successful")
            print(f"   Database: {settings.mongodb_database}")
            print(f"   Collections: {collections}")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        self.client.close()

def main():
    """Main function for database utilities"""
    print("🔧 Database Utilities")
    print("=" * 50)
    
    manager = DatabaseManager()
    
    # Test connection
    if not manager.test_connection():
        return
    
    # Get database info
    print("\n📊 Database Information:")
    info = manager.get_database_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Get schema for each collection
    print("\n📋 Collection Schemas:")
    for collection in info.get("collections", []):
        print(f"\n   Collection: {collection}")
        schema = manager.get_collection_schema(collection)
        if "error" not in schema:
            print(f"   Document count: {schema.get('document_count', 0)}")
            print(f"   Schema: {schema.get('schema', {})}")
        else:
            print(f"   Error: {schema['error']}")
    
    manager.close()

if __name__ == "__main__":
    main() 