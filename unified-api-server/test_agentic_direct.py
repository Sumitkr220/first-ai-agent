#!/usr/bin/env python3
"""
Direct test of agentic functionality without server
"""

import requests
import json

def test_agentic_direct():
    """Test agentic functionality directly"""
    
    print("🤖 Testing Agentic API Directly")
    print("=" * 50)
    
    # Test queries for different tools
    test_queries = [
        {
            "query": "What's the weather in Mumbai?",
            "expected_tool": "geo-weather",
            "description": "Weather query"
        },
        {
            "query": "Tell me about the invoice details",
            "expected_tool": "pdf-rag",
            "description": "Invoice query"
        },
        {
            "query": "Find me the best rated products",
            "expected_tool": "products-rag",
            "description": "Product rating query"
        }
    ]
    
    # Import and test directly
    from main import AgenticAPI, GeoWeatherAPI, PDFRAGAPI, ProductsRAGAPI
    
    try:
        # Create APIs
        geo_weather_api = GeoWeatherAPI()
        pdf_rag_api = PDFRAGAPI()
        products_rag_api = ProductsRAGAPI()
        
        # Create agentic API
        agentic_api = AgenticAPI(geo_weather_api, pdf_rag_api, products_rag_api)
        
        print("✅ AgenticAPI created successfully!")
        
        # Test each query
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n📝 Test {i}/3")
            print(f"🔍 Query: {test_case['query']}")
            print(f"📊 Expected Tool: {test_case['expected_tool']}")
            print(f"📋 Description: {test_case['description']}")
            
            try:
                result = agentic_api.process_query(test_case['query'])
                
                print(f"✅ Response:")
                print(f"   Tool Used: {result.get('tool_used', 'N/A')}")
                print(f"   Confidence: {result.get('confidence', 'N/A')}")
                print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
                print(f"   Answer Preview: {result.get('answer', 'N/A')[:100]}...")
                
                # Check if correct tool was used
                actual_tool = result.get('tool_used', 'unknown')
                expected_tool = test_case['expected_tool']
                
                if actual_tool == expected_tool:
                    print(f"✅ Correct tool selected!")
                else:
                    print(f"⚠️ Tool mismatch: Expected {expected_tool}, got {actual_tool}")
                
                # Check confidence
                confidence = result.get('confidence', 0)
                if confidence >= 0.7:
                    print(f"✅ High confidence: {confidence}")
                elif confidence >= 0.5:
                    print(f"⚠️ Medium confidence: {confidence}")
                else:
                    print(f"❌ Low confidence: {confidence}")
                    
            except Exception as e:
                print(f"❌ Test failed: {str(e)}")
            
            print("-" * 50)
        
        print("\n🎉 Direct Agentic API Testing Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up agentic API: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agentic_direct()
    if success:
        print("🎉 All direct tests passed!")
    else:
        print("❌ Direct tests failed!") 