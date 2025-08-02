#!/usr/bin/env python3
"""
Debug script to test weather functionality
"""

import requests
import json

def test_weather_functionality():
    """Test the weather functionality step by step"""
    
    print("Testing weather functionality...")
    
    # Test 1: Basic query without weather
    print("\n1. Testing basic query...")
    response = requests.post(
        "http://localhost:8000/first-ai-agent",
        json={
            "query": "What is the weather like in Mumbai?",
            "include_real_time_weather": False,
            "city_name": "Mumbai"
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Basic query successful")
        print(f"Has real_time_weather: {'real_time_weather' in data}")
        if 'real_time_weather' in data:
            print(f"Weather data: {data['real_time_weather']}")
    else:
        print(f"❌ Basic query failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test 2: Query with weather data
    print("\n2. Testing query with weather data...")
    response = requests.post(
        "http://localhost:8000/first-ai-agent",
        json={
            "query": "What is the weather like in Mumbai?",
            "include_real_time_weather": True,
            "city_name": "Mumbai"
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Weather query successful")
        print(f"Has real_time_weather: {'real_time_weather' in data}")
        if 'real_time_weather' in data:
            print(f"Weather data: {json.dumps(data['real_time_weather'], indent=2)}")
        else:
            print("❌ No weather data in response")
    else:
        print(f"❌ Weather query failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test 3: Coldest cities query
    print("\n3. Testing coldest cities query...")
    response = requests.post(
        "http://localhost:8000/first-ai-agent",
        json={
            "query": "What are the coldest cities in India?",
            "include_real_time_weather": True
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Coldest cities query successful")
        print(f"Has real_time_weather: {'real_time_weather' in data}")
        if 'real_time_weather' in data:
            print(f"Weather data: {json.dumps(data['real_time_weather'], indent=2)}")
        else:
            print("❌ No weather data in response")
    else:
        print(f"❌ Coldest cities query failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_weather_functionality() 