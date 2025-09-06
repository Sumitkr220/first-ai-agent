#!/usr/bin/env python3
"""
Test script to demonstrate the query API functionality
"""

import requests
import json

def test_query_api():
    """Test the query API with different natural language queries."""
    
    # API endpoint
    url = "http://localhost:8000/api/v1/query"
    
    # Test queries
    test_queries = [
        "What are the top 5 products by sales volume?",
        "How many sales were made online?",
        "Show me the total revenue by month",
        "What is the average customer satisfaction?",
        "Which store location has the most sales?"
    ]
    
    print("🔍 Testing DB-AI-AGENT Query API")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 40)
        
        try:
            # Make the API request
            payload = {
                "query": query,
                "session_id": f"test_session_{i}",
                "context": {},
                "max_results": 10,
                "include_analysis": True
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    print("✅ Success!")
                    print(f"🤖 AI Response: {result.get('response', 'No response')}")
                    
                    # Show query analysis
                    analysis = result.get("query_analysis", {})
                    if analysis:
                        print(f"📊 Target Collection: {analysis.get('target_collection')}")
                        print(f"🔧 Query Type: {analysis.get('query_type')}")
                        print(f"🎯 Confidence: {analysis.get('confidence_score', 0):.2f}")
                    
                    # Show results
                    query_result = result.get("query_result", {})
                    if query_result and query_result.get("result"):
                        print(f"📈 Results: {len(query_result['result'])} records found")
                        print(f"⏱️  Execution Time: {query_result.get('execution_time', 0):.3f}s")
                    
                else:
                    print("❌ Failed")
                    print(f"Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()

def test_simple_query():
    """Test a simple query to show the working example."""
    
    print("🎯 Testing your specific query: 'What are the top 5 products by sales volume?'")
    print("=" * 70)
    
    url = "http://localhost:8000/api/v1/query"
    
    payload = {
        "query": "What are the top 5 products by sales volume?",
        "session_id": "demo_session",
        "context": {},
        "max_results": 5,
        "include_analysis": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                print("✅ Query executed successfully!")
                print("\n📊 Results:")
                print(result.get("response", "No response"))
                
                # Show the raw data
                query_result = result.get("query_result", {})
                if query_result and query_result.get("result"):
                    print("\n📋 Raw Data:")
                    for i, item in enumerate(query_result["result"], 1):
                        print(f"{i}. {item['_id']}: {item['totalQuantity']} units")
                
            else:
                print("❌ Query failed")
                print(f"Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Starting DB-AI-AGENT Query Tests")
    print("Make sure the API server is running on http://localhost:8000")
    print()
    
    # Test the specific query first
    test_simple_query()
    
    print("\n" + "=" * 70)
    print("🧪 Running additional test queries...")
    
    # Test multiple queries
    test_query_api()
    
    print("✅ All tests completed!") 