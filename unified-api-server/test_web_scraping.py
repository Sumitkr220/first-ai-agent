#!/usr/bin/env python3
"""
Test script for web scraping weather functionality
"""

import requests
import json
import time
import random
import re
from datetime import datetime

def test_web_scraping():
    """Test the web scraping functionality"""
    
    print("🧪 Testing Web Scraping Weather Functionality")
    print("=" * 60)
    
    # Test cities
    test_cities = ["Mumbai", "Delhi", "Bangalore", "Pune"]
    
    for city in test_cities:
        print(f"\n🌍 Testing weather scraping for: {city}")
        print("-" * 40)
        
        # Test the API endpoint
        try:
            response = requests.post(
                "http://localhost:8000/geo-weather",
                headers={"Content-Type": "application/json"},
                json={
                    "query": f"What is the current weather in {city}?",
                    "include_real_time_weather": True,
                    "city_name": city
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                weather_data = data.get('real_time_weather', {})
                
                print(f"✅ API Response for {city}:")
                print(f"   Temperature: {weather_data.get('temperature', {}).get('current', 'N/A')}")
                print(f"   Humidity: {weather_data.get('humidity', 'N/A')}")
                print(f"   Wind Speed: {weather_data.get('wind_speed', 'N/A')}")
                print(f"   Description: {weather_data.get('description', 'N/A')}")
                print(f"   Source: {weather_data.get('source', 'N/A')}")
                print(f"   Data Freshness: {weather_data.get('data_freshness', 'N/A')}")
                
                if 'scraped_sources' in weather_data:
                    print(f"   Scraped Sources: {weather_data.get('scraped_sources', 0)}")
                    print(f"   Scraped URLs: {weather_data.get('scraped_urls', [])}")
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Test failed for {city}: {str(e)}")
        
        # Add delay between tests
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ Web Scraping Test Complete!")

if __name__ == "__main__":
    test_web_scraping() 