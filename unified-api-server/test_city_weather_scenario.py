#!/usr/bin/env python3
"""
Test to check if agentic API can extract city from PDF and find weather
"""

from main import AgenticAPI, GeoWeatherAPI, PDFRAGAPI, ProductsRAGAPI

def test_city_extraction_and_weather():
    """Test if agentic API can extract city from PDF and get weather"""
    
    print("🏙️ Testing City Extraction from PDF + Weather Scenario")
    print("=" * 60)
    
    # Create APIs
    geo_weather_api = GeoWeatherAPI()
    pdf_rag_api = PDFRAGAPI()
    products_rag_api = ProductsRAGAPI()
    
    # Create agentic API
    agentic_api = AgenticAPI(geo_weather_api, pdf_rag_api, products_rag_api)
    
    print("✅ AgenticAPI created successfully!")
    
    # Test queries that should extract city from PDF and get weather
    test_queries = [
        {
            "query": "What city is mentioned in the invoice and what's the weather there?",
            "description": "Extract city from PDF and get weather"
        },
        {
            "query": "Find the city in the document and tell me the current weather",
            "description": "Document city + weather query"
        },
        {
            "query": "What's the weather in the city mentioned in the invoice?",
            "description": "Invoice city weather query"
        },
        {
            "query": "Extract the location from the PDF and get the temperature there",
            "description": "Location extraction + temperature"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}/4")
        print(f"🔍 Query: {test_case['query']}")
        print(f"📋 Description: {test_case['description']}")
        
        try:
            result = agentic_api.process_multi_step_query(test_case['query'])
            
            print(f"✅ Response:")
            print(f"   Tool Used: {result.get('tool_used', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
            print(f"   Answer Preview: {result.get('answer', 'N/A')[:200]}...")
            
            # Check if it used the right tool
            tool_used = result.get('tool_used', 'unknown')
            if tool_used == 'pdf-rag':
                print(f"✅ Correctly used PDF-RAG to extract city information!")
            elif tool_used == 'geo-weather':
                print(f"✅ Used geo-weather for weather data!")
            else:
                print(f"⚠️ Used {tool_used} tool")
            
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
        
        print("-" * 60)
    
    print("\n🎉 City Extraction + Weather Testing Complete!")

def test_specific_city_from_pdf():
    """Test with a specific city that should be in the PDF"""
    
    print("\n🏙️ Testing Specific City from PDF")
    print("=" * 40)
    
    # Create APIs
    geo_weather_api = GeoWeatherAPI()
    pdf_rag_api = PDFRAGAPI()
    products_rag_api = ProductsRAGAPI()
    
    # Create agentic API
    agentic_api = AgenticAPI(geo_weather_api, pdf_rag_api, products_rag_api)
    
    # Test with specific cities that might be in the PDF
    test_cities = [
        "Kolkata",  # This should be in the PDF based on the test results
        "New Delhi",  # This might be in the PDF
        "Bhiwadi",   # This might be in the PDF
        "Alwar"      # This might be in the PDF
    ]
    
    for city in test_cities:
        print(f"\n🔍 Testing weather for: {city}")
        
        try:
            # First, check if city is mentioned in PDF
            pdf_result = agentic_api.process_query(f"Is {city} mentioned in the document?")
            print(f"📄 PDF Check: {pdf_result.get('answer', 'N/A')[:100]}...")
            
            # Then get weather for that city
            weather_result = agentic_api.process_query(f"What's the weather in {city}?")
            print(f"🌤️ Weather: {weather_result.get('answer', 'N/A')[:100]}...")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_city_extraction_and_weather()
    test_specific_city_from_pdf() 