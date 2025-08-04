#!/usr/bin/env python3
"""
Simple test to check if AgenticAPI can be instantiated
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import GeoWeatherAPI, PDFRAGAPI, ProductsRAGAPI, AgenticAPI

def test_agentic_instantiation():
    """Test if AgenticAPI can be instantiated"""
    try:
        print("Testing AgenticAPI instantiation...")
        
        # Create the individual APIs
        geo_weather_api = GeoWeatherAPI()
        print("✅ GeoWeatherAPI created")
        
        pdf_rag_api = PDFRAGAPI()
        print("✅ PDFRAGAPI created")
        
        products_rag_api = ProductsRAGAPI()
        print("✅ ProductsRAGAPI created")
        
        # Create the AgenticAPI
        agentic_api = AgenticAPI(geo_weather_api, pdf_rag_api, products_rag_api)
        print("✅ AgenticAPI created successfully!")
        
        # Test a simple query
        print("Testing simple query...")
        result = agentic_api.process_query("What's the weather in Mumbai?")
        print(f"✅ Query processed successfully!")
        print(f"Tool used: {result.get('tool_used')}")
        print(f"Confidence: {result.get('confidence')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agentic_instantiation()
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Tests failed!") 