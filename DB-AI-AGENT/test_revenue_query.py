#!/usr/bin/env python3
"""
Test script to debug revenue queries and show correct prompts
"""

import requests
import json

def test_revenue_queries():
    """Test different revenue-related queries."""
    
    # API endpoint
    url = "http://localhost:8000/api/v1/query"
    
    # Test different revenue-related prompts
    revenue_queries = [
        "What are the top 5 products by revenue?",
        "Show me the 5 products with the highest revenue",
        "Which 5 products generate the most revenue?",
        "What are the best selling products by revenue?",
        "Top 5 products by sales amount",
        "Highest revenue products"
    ]
    
    print("💰 Testing Revenue-Related Queries")
    print("=" * 50)
    
    for i, query in enumerate(revenue_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 40)
        
        try:
            # Make the API request
            payload = {
                "query": query,
                "session_id": f"revenue_test_{i}",
                "context": {},
                "max_results": 5,
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

def show_revenue_prompts():
    """Show the best prompts for revenue queries."""
    
    print("🎯 Best Prompts for Revenue Data")
    print("=" * 40)
    print()
    
    prompts = [
        "What are the top 5 products by revenue?",
        "Show me the 5 products with the highest revenue",
        "Which 5 products generate the most revenue?",
        "What are the best selling products by revenue?",
        "Top 5 products by sales amount",
        "Highest revenue products",
        "Most profitable products",
        "Products with highest sales value"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"{i}. \"{prompt}\"")
    
    print()
    print("💡 Key Terms to Use:")
    print("- 'revenue' (most specific)")
    print("- 'sales amount'")
    print("- 'highest revenue'")
    print("- 'most revenue'")
    print("- 'sales value'")
    print()
    print("❌ Avoid Terms:")
    print("- 'sales volume' (refers to quantity)")
    print("- 'units sold' (refers to quantity)")
    print("- 'number of sales' (refers to count)")

def test_simple_quantity_query():
    """Test a simple quantity query to compare."""
    
    print("📦 Testing Quantity vs Revenue Query")
    print("=" * 40)
    
    url = "http://localhost:8000/api/v1/query"
    
    # Test quantity query (should work)
    quantity_payload = {
        "query": "What are the top 5 products by sales volume?",
        "session_id": "quantity_test",
        "context": {},
        "max_results": 5,
        "include_analysis": True
    }
    
    try:
        response = requests.post(url, json=quantity_payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                print("✅ Quantity Query (Sales Volume) - WORKS!")
                print(result.get("response", "No response"))
            else:
                print("❌ Quantity Query Failed")
                print(f"Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Starting Revenue Query Tests")
    print("Make sure the API server is running on http://localhost:8000")
    print()
    
    # Show the best prompts first
    show_revenue_prompts()
    
    print("\n" + "=" * 70)
    print("🧪 Testing Revenue Queries...")
    
    # Test revenue queries
    test_revenue_queries()
    
    print("\n" + "=" * 70)
    print("📦 Testing Quantity Query for Comparison...")
    
    # Test quantity query
    test_simple_quantity_query()
    
    print("\n✅ All tests completed!") 