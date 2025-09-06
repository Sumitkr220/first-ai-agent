#!/usr/bin/env python3
"""
Test script to analyze sales data structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import db_manager
from app.services.db_service import db_service

def analyze_sales_data():
    """Analyze sales data structure and content."""
    print("🔍 Analyzing sales data...")
    
    try:
        # Get sales collection
        collection = db_manager.get_collection("sales")
        
        # Get total count
        total_count = collection.count_documents({})
        print(f"📊 Total sales records: {total_count}")
        
        if total_count == 0:
            print("❌ No sales data found!")
            return
        
        # Get sample documents
        sample_docs = list(collection.find().limit(3))
        print(f"\n📋 Sample documents:")
        for i, doc in enumerate(sample_docs):
            print(f"\n--- Document {i+1} ---")
            for key, value in doc.items():
                print(f"  {key}: {type(value).__name__} = {value}")
        
        # Check date range
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "min_date": {"$min": "$saleDate"},
                    "max_date": {"$max": "$saleDate"},
                    "total_sales": {"$sum": 1}
                }
            }
        ]
        
        date_range = list(collection.aggregate(pipeline))
        if date_range:
            result = date_range[0]
            print(f"\n📅 Date Range:")
            print(f"  Earliest sale: {result['min_date']}")
            print(f"  Latest sale: {result['max_date']}")
            print(f"  Total sales: {result['total_sales']}")
        
        # Check purchase methods
        pipeline = [
            {"$group": {"_id": "$purchaseMethod", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        purchase_methods = list(collection.aggregate(pipeline))
        print(f"\n💳 Purchase Methods:")
        for method in purchase_methods:
            print(f"  {method['_id']}: {method['count']}")
        
        # Check store locations
        pipeline = [
            {"$group": {"_id": "$storeLocation", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        locations = list(collection.aggregate(pipeline))
        print(f"\n🏪 Store Locations:")
        for location in locations:
            print(f"  {location['_id']}: {location['count']}")
        
        # Check items structure
        pipeline = [
            {"$unwind": "$items"},
            {"$group": {"_id": "$items.name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        
        items = list(collection.aggregate(pipeline))
        print(f"\n🛍️ Top Items:")
        for item in items:
            print(f"  {item['_id']}: {item['count']}")
        
    except Exception as e:
        print(f"❌ Error analyzing sales data: {e}")

if __name__ == "__main__":
    analyze_sales_data() 