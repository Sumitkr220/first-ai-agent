#!/usr/bin/env python3
"""
Test to see which method is being called
"""

import requests
import json

def test_method_call():
    """Test which method is being called"""
    
    print("🧪 Testing Method Call")
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
            
            # Check the source
            source = weather_data.get('source', '')
            if 'web_scraping' in source:
                print("❌ Still using web scraping!")
            elif 'wttr_in' in source:
                print("✅ Using wttr.in API!")
            else:
                print(f"⚠️ Using unknown source: {source}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_method_call() 