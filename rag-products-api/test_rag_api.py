#!/usr/bin/env python3
"""
Test script for RAG Products API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_rag_query(query: str, top_k: int = 5):
    """Test a RAG query"""
    print(f"\n🔍 Testing Query: {query}")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={
                "query": query,
                "top_k": top_k,
                "include_details": True
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"📝 Answer: {data['answer']}")
            print(f"🤖 Model: {data['model_used']}")
            
            if 'details' in data:
                details = data['details']
                print(f"📊 Details:")
                print(f"   - Products Found: {details.get('products_found', 0)}")
                print(f"   - Average Relevance Score: {details.get('average_relevance_score', 0):.3f}")
                print(f"   - Categories: {details.get('categories_found', [])}")
                if 'price_range' in details:
                    price_range = details['price_range']
                    print(f"   - Price Range: ${price_range['min']} - ${price_range['max']}")
            
            if 'relevant_products' in data and data['relevant_products']:
                print(f"\n🏷️  Top Relevant Products:")
                for i, product in enumerate(data['relevant_products'][:3], 1):
                    print(f"   {i}. {product['Name']} (Score: {product['relevance_score']:.3f})")
                    print(f"      Brand: {product['Brand']} | Category: {product['Category']}")
                    print(f"      Price: {product['Price']} {product['Currency']} | Stock: {product['Stock']}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_health():
    """Test health endpoint"""
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check Exception: {e}")

def test_stats():
    """Test product stats endpoint"""
    print("\n📊 Testing Product Stats...")
    try:
        response = requests.get(f"{BASE_URL}/products/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Product Stats:")
            print(f"   - Total Products: {data['total_products']}")
            print(f"   - Price Range: ${data['price_stats']['min']} - ${data['price_stats']['max']}")
            print(f"   - Top Categories: {list(data['categories'].keys())[:5]}")
        else:
            print(f"❌ Stats Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats Exception: {e}")

def main():
    """Main test function"""
    print("🚀 RAG Products API Test Suite")
    print("=" * 60)
    
    # Test health first
    test_health()
    
    # Test stats
    test_stats()
    
    # Test queries
    test_queries = [
        "What are the most expensive products?",
        "Show me kitchen appliances under $100",
        "What electronics are available in stock?",
        "Find products from the brand 'Douglas Group'",
        "What fitness equipment do you have?",
        "Show me products in the 'Health & Wellness' category",
        "What are the cheapest products available?",
        "Find products with 'Smart' in the name",
        "What products are currently out of stock?",
        "Show me products in the color 'Blue'"
    ]
    
    for query in test_queries:
        test_rag_query(query)
        time.sleep(1)  # Small delay between requests
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main() 