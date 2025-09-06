#!/usr/bin/env python3
"""
Debug script to see what the AI generates for revenue queries
"""

import requests
import json

def debug_revenue_query():
    """Debug what the AI generates for revenue queries."""
    
    url = "http://localhost:8000/api/v1/query"
    
    # Test a simple revenue query
    payload = {
        "query": "What are the top 5 products by revenue?",
        "session_id": "debug_revenue",
        "context": {},
        "max_results": 5,
        "include_analysis": True
    }
    
    try:
        print("🔍 Debugging Revenue Query...")
        print("Query: What are the top 5 products by revenue?")
        print("-" * 50)
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success Response:")
            print(json.dumps(result, indent=2))
        else:
            print("❌ Error Response:")
            print(f"Status: {response.status_code}")
            print(f"Text: {response.text}")
            
            # Try to get more details
            try:
                error_json = response.json()
                print(f"Error JSON: {json.dumps(error_json, indent=2)}")
            except:
                print("Could not parse error as JSON")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_simple_revenue_pipeline():
    """Test a simple revenue aggregation pipeline manually."""
    
    print("\n🔧 Testing Manual Revenue Pipeline...")
    print("-" * 50)
    
    # Manual revenue aggregation pipeline
    pipeline = [
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$items.name",
                "totalRevenue": {
                    "$sum": {
                        "$multiply": [
                            {"$toDouble": "$items.price"},
                            "$items.quantity"
                        ]
                    }
                }
            }
        },
        {"$sort": {"totalRevenue": -1}},
        {"$limit": 5}
    ]
    
    print("Pipeline:")
    print(json.dumps(pipeline, indent=2))
    
    # Test this pipeline directly
    url = "http://localhost:8000/api/v1/query"
    
    # Create a custom query that should work
    payload = {
        "query": "Show me products with highest total sales value",
        "session_id": "manual_test",
        "context": {},
        "max_results": 5,
        "include_analysis": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Manual Test Response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Manual Test Failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Manual Test Exception: {e}")

if __name__ == "__main__":
    print("🚀 Starting Revenue Query Debug")
    print("=" * 50)
    
    # Debug the revenue query
    debug_revenue_query()
    
    # Test manual pipeline
    test_simple_revenue_pipeline()
    
    print("\n✅ Debug completed!") 