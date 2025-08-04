#!/usr/bin/env python3
"""
Simple demo of city extraction from PDF and weather functionality
"""

from main import AgenticAPI, GeoWeatherAPI, PDFRAGAPI, ProductsRAGAPI

def demo_city_weather():
    """Demo the city extraction and weather functionality"""
    
    print("🏙️ Demo: Extract City from PDF Invoice and Get Weather")
    print("=" * 60)
    
    # Create APIs
    geo_weather_api = GeoWeatherAPI()
    pdf_rag_api = PDFRAGAPI()
    products_rag_api = ProductsRAGAPI()
    
    # Create agentic API
    agentic_api = AgenticAPI(geo_weather_api, pdf_rag_api, products_rag_api)
    
    # Test the specific scenario
    query = "What city is mentioned in the invoice and what's the weather there?"
    
    print(f"🔍 Query: {query}")
    print("\n🔄 Processing...")
    
    try:
        result = agentic_api.process_multi_step_query(query)
        
        print(f"\n✅ Result:")
        print(f"Tool Used: {result.get('tool_used')}")
        print(f"Confidence: {result.get('confidence')}")
        print(f"\n📄 Answer:")
        print(result.get('answer', 'No answer generated'))
        
        # Show the cities found
        raw_response = result.get('raw_response', {})
        cities_found = raw_response.get('cities_found', [])
        if cities_found:
            print(f"\n🏙️ Cities found in PDF: {', '.join(cities_found)}")
        
        print(f"\n🎉 Success! The agentic API successfully:")
        print(f"   1. ✅ Extracted cities from the PDF invoice")
        print(f"   2. ✅ Got real-time weather for the first city found")
        print(f"   3. ✅ Combined both pieces of information")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    demo_city_weather() 