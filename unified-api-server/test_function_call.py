#!/usr/bin/env python3
"""
Test to verify function call is working
"""

import requests
import json

def test_function_call():
    """Test if the function is being called"""
    
    print("🧪 Testing Function Call")
    print("=" * 40)
    
    try:
        response = requests.post(
            "http://localhost:8000/geo-weather",
            headers={"Content-Type": "application/json"},
            json={
                "query": "What is the current weather in Mumbai?",
                "include_real_time_weather": True,
                "city_name": "Mumbai"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            weather_data = data.get('real_time_weather', {})
            
            print(f"✅ API Response:")
            print(f"   Source: {weather_data.get('source', 'N/A')}")
            print(f"   Temperature: {weather_data.get('temperature', {}).get('current', 'N/A')}")
            print(f"   Humidity: {weather_data.get('humidity', 'N/A')}")
            print(f"   Wind Speed: {weather_data.get('wind_speed', 'N/A')}")
            print(f"   Description: {weather_data.get('description', 'N/A')}")
            
            # Check if it's using web scraping
            source = weather_data.get('source', '')
            if 'web_scraping' in source or 'open_meteo' in source:
                print("✅ Web scraping is working!")
            else:
                print("❌ Still using fallback API")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_function_call() 