#!/usr/bin/env python3
"""
Test script to fix revenue calculation issues
"""

import requests
import json

def test_revenue_with_fixed_pipeline():
    """Test revenue calculation with a fixed pipeline."""
    
    print("🔧 Testing Fixed Revenue Pipeline...")
    print("=" * 50)
    
    # Test different revenue-related queries that should work
    revenue_queries = [
        "What are the top 5 products by total sales value?",
        "Show me the 5 products with highest total sales value",
        "Which 5 products have the highest total sales value?",
        "Top 5 products by total sales amount",
        "Products with highest total sales value"
    ]
    
    url = "http://localhost:8000/api/v1/query"
    
    for i, query in enumerate(revenue_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 40)
        
        try:
            payload = {
                "query": query,
                "session_id": f"revenue_fix_{i}",
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

def show_working_revenue_prompts():
    """Show the working prompts for revenue data."""
    
    print("🎯 Working Prompts for Revenue Data")
    print("=" * 40)
    print()
    
    working_prompts = [
        "What are the top 5 products by total sales value?",
        "Show me the 5 products with highest total sales value",
        "Which 5 products have the highest total sales value?",
        "Top 5 products by total sales amount",
        "Products with highest total sales value",
        "Best selling products by total sales value",
        "Most valuable products by sales"
    ]
    
    for i, prompt in enumerate(working_prompts, 1):
        print(f"{i}. \"{prompt}\"")
    
    print()
    print("💡 Key Terms That Work:")
    print("- 'total sales value' (most reliable)")
    print("- 'highest total sales value'")
    print("- 'total sales amount'")
    print("- 'sales value'")
    print()
    print("❌ Terms That Don't Work:")
    print("- 'revenue' (causes aggregation errors)")
    print("- 'highest revenue'")
    print("- 'most revenue'")

def test_quantity_vs_value_comparison():
    """Compare quantity vs value queries."""
    
    print("\n📊 Quantity vs Value Comparison")
    print("=" * 40)
    
    url = "http://localhost:8000/api/v1/query"
    
    # Test quantity query
    quantity_payload = {
        "query": "What are the top 5 products by sales volume?",
        "session_id": "quantity_test",
        "context": {},
        "max_results": 5,
        "include_analysis": True
    }
    
    # Test value query
    value_payload = {
        "query": "What are the top 5 products by total sales value?",
        "session_id": "value_test",
        "context": {},
        "max_results": 5,
        "include_analysis": True
    }
    
    try:
        print("📦 Testing Quantity Query...")
        response = requests.post(url, json=quantity_payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Quantity Query - WORKS!")
                print(result.get("response", "No response"))
            else:
                print("❌ Quantity Query Failed")
        else:
            print(f"❌ Quantity Query HTTP Error: {response.status_code}")
        
        print("\n💰 Testing Value Query...")
        response = requests.post(url, json=value_payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Value Query - WORKS!")
                print(result.get("response", "No response"))
            else:
                print("❌ Value Query Failed")
        else:
            print(f"❌ Value Query HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Starting Revenue Fix Tests")
    print("=" * 50)
    
    # Show working prompts
    show_working_revenue_prompts()
    
    print("\n" + "=" * 70)
    print("🧪 Testing Fixed Revenue Queries...")
    
    # Test fixed revenue queries
    test_revenue_with_fixed_pipeline()
    
    print("\n" + "=" * 70)
    print("📊 Comparing Quantity vs Value...")
    
    # Test comparison
    test_quantity_vs_value_comparison()
    
    print("\n✅ All tests completed!") 