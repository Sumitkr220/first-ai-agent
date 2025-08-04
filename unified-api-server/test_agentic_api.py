#!/usr/bin/env python3
"""
Test script for the Agentic API
Tests intelligent routing to different tools
"""

import requests
import json
import time

def test_agentic_api():
    """Test the agentic API with various query types"""
    
    print("🤖 Testing Agentic API")
    print("=" * 50)
    
    # Test queries for different tools
    test_queries = [
        # Geo-Weather queries
        {
            "query": "What's the weather in Mumbai?",
            "expected_tool": "geo-weather",
            "description": "Weather query"
        },
        {
            "query": "Temperature in Delhi right now",
            "expected_tool": "geo-weather", 
            "description": "Temperature query"
        },
        {
            "query": "Find the coldest cities in India",
            "expected_tool": "geo-weather",
            "description": "Geographical query"
        },
        
        # PDF RAG queries
        {
            "query": "What's in the PDF document?",
            "expected_tool": "pdf-rag",
            "description": "PDF content query"
        },
        {
            "query": "Tell me about the invoice details",
            "expected_tool": "pdf-rag",
            "description": "Invoice query"
        },
        {
            "query": "What products are mentioned in the document?",
            "expected_tool": "pdf-rag",
            "description": "Document product query"
        },
        
        # Products RAG queries
        {
            "query": "Find me the best rated products",
            "expected_tool": "products-rag",
            "description": "Product rating query"
        },
        {
            "query": "Show me electronics under $100",
            "expected_tool": "products-rag",
            "description": "Product price query"
        },
        {
            "query": "What brands are available?",
            "expected_tool": "products-rag",
            "description": "Brand query"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}/9")
        print(f"🔍 Query: {test_case['query']}")
        print(f"📊 Expected Tool: {test_case['expected_tool']}")
        print(f"📋 Description: {test_case['description']}")
        
        try:
            response = requests.post(
                "http://localhost:8002/agent",
                headers={"Content-Type": "application/json"},
                json={"query": test_case['query']},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Response:")
                print(f"   Tool Used: {data.get('tool_used', 'N/A')}")
                print(f"   Confidence: {data.get('confidence', 'N/A')}")
                print(f"   Reasoning: {data.get('reasoning', 'N/A')}")
                print(f"   Answer Preview: {data.get('answer', 'N/A')[:100]}...")
                
                # Check if correct tool was used
                actual_tool = data.get('tool_used', 'unknown')
                expected_tool = test_case['expected_tool']
                
                if actual_tool == expected_tool:
                    print(f"✅ Correct tool selected!")
                else:
                    print(f"⚠️ Tool mismatch: Expected {expected_tool}, got {actual_tool}")
                
                # Check confidence
                confidence = data.get('confidence', 0)
                if confidence >= 0.7:
                    print(f"✅ High confidence: {confidence}")
                elif confidence >= 0.5:
                    print(f"⚠️ Medium confidence: {confidence}")
                else:
                    print(f"❌ Low confidence: {confidence}")
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
        
        print("-" * 50)
        time.sleep(1)  # Small delay between tests
    
    print("\n🎉 Agentic API Testing Complete!")

def test_edge_cases():
    """Test edge cases and ambiguous queries"""
    
    print("\n🧪 Testing Edge Cases")
    print("=" * 30)
    
    edge_cases = [
        {
            "query": "Hello, how are you?",
            "description": "General greeting"
        },
        {
            "query": "What is the meaning of life?",
            "description": "Philosophical question"
        },
        {
            "query": "Tell me a joke",
            "description": "Entertainment query"
        }
    ]
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n📝 Edge Case {i}/3")
        print(f"🔍 Query: {test_case['query']}")
        print(f"📋 Description: {test_case['description']}")
        
        try:
            response = requests.post(
                "http://localhost:8002/agent",
                headers={"Content-Type": "application/json"},
                json={"query": test_case['query']},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Tool Selected: {data.get('tool_used', 'N/A')}")
                print(f"📊 Confidence: {data.get('confidence', 'N/A')}")
                print(f"💭 Reasoning: {data.get('reasoning', 'N/A')}")
            else:
                print(f"❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_agentic_api()
    test_edge_cases() 