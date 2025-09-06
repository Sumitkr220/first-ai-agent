#!/usr/bin/env python3
"""
Debug script to test schema functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database.connection import db_manager
from app.services.db_service import db_service

def test_database_connection():
    """Test database connection."""
    print("🔍 Testing database connection...")
    try:
        db = db_manager.get_database()
        print(f"✅ Database connected: {db.name}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_collections():
    """Test listing collections."""
    print("\n🔍 Testing collections...")
    try:
        collections = db_service.get_all_collections()
        print(f"✅ Collections found: {collections}")
        return collections
    except Exception as e:
        print(f"❌ Error listing collections: {e}")
        return []

def test_schema():
    """Test schema retrieval."""
    print("\n🔍 Testing schema retrieval...")
    try:
        database_info = db_service.get_database_info()
        print(f"✅ Database info: {database_info}")
        return database_info
    except Exception as e:
        print(f"❌ Error getting database info: {e}")
        return None

def test_collection_schema(collection_name):
    """Test specific collection schema."""
    print(f"\n🔍 Testing schema for collection: {collection_name}")
    try:
        schema = db_service.get_collection_schema(collection_name)
        print(f"✅ Schema: {schema}")
        return schema
    except Exception as e:
        print(f"❌ Error getting schema for {collection_name}: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting schema debug...")
    
    # Test database connection
    if not test_database_connection():
        sys.exit(1)
    
    # Test collections
    collections = test_collections()
    if not collections:
        sys.exit(1)
    
    # Test database info
    database_info = test_schema()
    if not database_info:
        sys.exit(1)
    
    # Test specific collection schema
    if collections:
        test_collection_schema(collections[0])
    
    print("\n✅ All tests completed!") 