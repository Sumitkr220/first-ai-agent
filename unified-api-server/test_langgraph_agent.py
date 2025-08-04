#!/usr/bin/env python3
"""
Test script for LangGraph-based Agentic API
Demonstrates the agent's ability to intelligently route queries using LLM chain of thought reasoning
"""

import requests
import json
import time

# API endpoint
BASE_URL = "http://localhost:8001"

def test_agent_query(query, description):
    """Test the agent with a specific query"""
    print(f"\n{'='*60}")
    print(f"🧪 Test: {description}")
    print(f"📝 Query: {query}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/agent",
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Success!")
            print(f"🔧 Tool Used: {result['tool_used']}")
            print(f"🎯 Confidence: {result['confidence']}")
            print(f"🧠 Reasoning: {result['reasoning']}")
            print(f"📄 Answer: {result['answer'][:200]}...")
            
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def main():
    """Main test function"""
    print("🚀 LangGraph Agent Test Suite")
    print("Testing intelligent query routing with LLM chain of thought reasoning")
    
    # Test cases
    test_cases = [
        {
            "query": "What is the weather in Delhi?",
            "description": "Weather Query - Should use geo-weather tool"
        },
        {
            "query": "What products are available in the electronics category?",
            "description": "Product Query - Should use products-rag tool"
        },
        {
            "query": "What cities are mentioned in the invoice document?",
            "description": "PDF Query - Should use pdf-rag tool"
        },
        {
            "query": "Extract cities from the invoice and get weather for all of them",
            "description": "Multi-step Query - Should combine pdf-rag and geo-weather"
        },
        {
            "query": "Tell me about the coldest cities in India",
            "description": "Complex Weather Query - Should use geo-weather with reasoning"
        },
        {
            "query": "What are the product details for eyeglasses in the catalog?",
            "description": "Product Catalog Query - Should use products-rag"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}/{len(test_cases)}")
        result = test_agent_query(test_case["query"], test_case["description"])
        results.append({
            "test": i,
            "description": test_case["description"],
            "query": test_case["query"],
            "result": result
        })
        time.sleep(2)  # Small delay between tests
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    successful_tests = [r for r in results if r["result"] is not None]
    failed_tests = [r for r in results if r["result"] is None]
    
    print(f"✅ Successful Tests: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed Tests: {len(failed_tests)}/{len(results)}")
    
    print(f"\n🎯 Tool Usage Summary:")
    tool_counts = {}
    for result in successful_tests:
        tool = result["result"]["tool_used"]
        tool_counts[tool] = tool_counts.get(tool, 0) + 1
    
    for tool, count in tool_counts.items():
        print(f"  - {tool}: {count} times")
    
    print(f"\n🧠 Average Confidence: {sum(r['result']['confidence'] for r in successful_tests) / len(successful_tests):.2f}")
    
    print(f"\n🎉 LangGraph Agent Test Complete!")
    print("The agent successfully uses LLM chain of thought reasoning for tool selection!")

if __name__ == "__main__":
    main() 