#!/usr/bin/env python3
"""
Debug script to test web scraping directly
"""

import requests
import time
import random
import re
from datetime import datetime

def test_direct_scraping():
    """Test web scraping directly"""
    
    print("🔍 Testing Direct Web Scraping")
    print("=" * 50)
    
    # Test the Open-Meteo API directly
    city_name = "Mumbai"
    print(f"🌍 Testing for: {city_name}")
    
    try:
        print("🔄 Trying Open-Meteo API...")
        url = "https://api.open-meteo.com/v1/forecast?latitude=19.076&longitude=72.8777&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&timezone=auto"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            current = data.get('current', {})
            
            print(f"✅ Open-Meteo API Response:")
            print(f"   Temperature: {current.get('temperature_2m')}°C")
            print(f"   Humidity: {current.get('relative_humidity_2m')}%")
            print(f"   Wind Speed: {current.get('wind_speed_10m')} km/h")
            print(f"   Weather Code: {current.get('weather_code')}")
            
            # Convert weather code to description
            weather_codes = {
                0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
                45: 'Foggy', 48: 'Depositing rime fog', 51: 'Light drizzle',
                53: 'Moderate drizzle', 55: 'Dense drizzle', 56: 'Light freezing drizzle',
                57: 'Dense freezing drizzle', 61: 'Slight rain', 63: 'Moderate rain',
                65: 'Heavy rain', 66: 'Light freezing rain', 67: 'Heavy freezing rain',
                71: 'Slight snow fall', 73: 'Moderate snow fall', 75: 'Heavy snow fall',
                77: 'Snow grains', 80: 'Slight rain showers', 81: 'Moderate rain showers',
                82: 'Violent rain showers', 85: 'Slight snow showers', 86: 'Heavy snow showers',
                95: 'Thunderstorm', 96: 'Thunderstorm with slight hail', 99: 'Thunderstorm with heavy hail'
            }
            
            weather_desc = weather_codes.get(current.get('weather_code', 0), 'Unknown')
            print(f"   Description: {weather_desc}")
            
        else:
            print(f"❌ Open-Meteo API failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Open-Meteo API error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Direct Scraping Test Complete!")

if __name__ == "__main__":
    test_direct_scraping() 