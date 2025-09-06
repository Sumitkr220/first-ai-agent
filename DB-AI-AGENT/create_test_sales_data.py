#!/usr/bin/env python3
"""
Create comprehensive test sales data over 2 years
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import random
from bson import Decimal128
from app.database.connection import db_manager

def create_test_sales_data():
    """Create comprehensive test sales data over 2 years."""
    print("🚀 Creating comprehensive test sales data...")
    
    try:
        collection = db_manager.get_collection("sales")
        
        # Clear existing data
        collection.delete_many({})
        print("🗑️ Cleared existing sales data")
        
        # Products with realistic prices
        products = [
            {"name": "Laptop", "price": Decimal128("999.99"), "tags": ["electronics", "computer"]},
            {"name": "Smartphone", "price": Decimal128("699.99"), "tags": ["electronics", "mobile"]},
            {"name": "Tablet", "price": Decimal128("399.99"), "tags": ["electronics", "mobile"]},
            {"name": "Headphones", "price": Decimal128("199.99"), "tags": ["electronics", "audio"]},
            {"name": "Gaming Console", "price": Decimal128("499.99"), "tags": ["electronics", "gaming"]},
            {"name": "Monitor", "price": Decimal128("299.99"), "tags": ["electronics", "computer"]},
            {"name": "Keyboard", "price": Decimal128("89.99"), "tags": ["electronics", "computer"]},
            {"name": "Mouse", "price": Decimal128("59.99"), "tags": ["electronics", "computer"]},
            {"name": "Webcam", "price": Decimal128("129.99"), "tags": ["electronics", "computer"]},
            {"name": "Speaker", "price": Decimal128("149.99"), "tags": ["electronics", "audio"]}
        ]
        
        # Store locations
        locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
        
        # Purchase methods
        purchase_methods = ["online", "in store", "phone"]
        
        # Generate data for 2 years (2023-2024)
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        # Create sales data with seasonal trends
        sales_data = []
        
        current_date = start_date
        while current_date <= end_date:
            # Generate 1-5 sales per day (more during holidays)
            daily_sales = random.randint(1, 5)
            
            # Increase sales during holidays
            if current_date.month in [11, 12]:  # Holiday season
                daily_sales = random.randint(3, 8)
            elif current_date.month in [6, 7, 8]:  # Summer
                daily_sales = random.randint(2, 6)
            
            for _ in range(daily_sales):
                # Random time during business hours
                hour = random.randint(9, 21)
                minute = random.randint(0, 59)
                sale_time = current_date.replace(hour=hour, minute=minute)
                
                # Select random product
                product = random.choice(products)
                quantity = random.randint(1, 3)
                
                # Customer data
                customer_age = random.randint(18, 65)
                customer_gender = random.choice(["M", "F"])
                customer_email = f"customer{random.randint(1000, 9999)}@example.com"
                customer_satisfaction = random.randint(1, 5)
                
                # Sale data
                sale = {
                    "saleDate": sale_time,
                    "storeLocation": random.choice(locations),
                    "purchaseMethod": random.choice(purchase_methods),
                    "couponUsed": random.choice([True, False]),
                    "customer": {
                        "age": customer_age,
                        "email": customer_email,
                        "gender": customer_gender,
                        "satisfaction": customer_satisfaction
                    },
                    "items": [{
                        "name": product["name"],
                        "price": product["price"],
                        "quantity": quantity,
                        "tags": product["tags"]
                    }]
                }
                
                sales_data.append(sale)
            
            current_date += timedelta(days=1)
        
        # Insert data in batches
        batch_size = 1000
        for i in range(0, len(sales_data), batch_size):
            batch = sales_data[i:i + batch_size]
            collection.insert_many(batch)
            print(f"📦 Inserted batch {i//batch_size + 1}/{(len(sales_data) + batch_size - 1)//batch_size}")
        
        # Verify data
        total_count = collection.count_documents({})
        print(f"\n✅ Created {total_count} sales records")
        
        # Show date range
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
        
        result = list(collection.aggregate(pipeline))[0]
        print(f"📅 Date Range: {result['min_date']} to {result['max_date']}")
        print(f"📊 Total Sales: {result['total_sales']}")
        
        # Show quarterly breakdown
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$saleDate"},
                        "quarter": {"$ceil": {"$divide": [{"$month": "$saleDate"}, 3]}}
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.year": 1, "_id.quarter": 1}}
        ]
        
        quarters = list(collection.aggregate(pipeline))
        print(f"\n📈 Quarterly Breakdown:")
        for quarter in quarters:
            year = quarter["_id"]["year"]
            q = quarter["_id"]["quarter"]
            count = quarter["count"]
            print(f"  Q{q} {year}: {count} sales")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")

if __name__ == "__main__":
    create_test_sales_data() 