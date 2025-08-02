#!/usr/bin/env python3
"""
Debug script to test API endpoint
"""

import requests
import json

def test_api_endpoint():
    """Test the API endpoint with different parameters"""
    
    print("Testing API endpoint...")
    
    # Test 1: With include_real_time_weather=True and city_name
    print("\n1. Testing with include_real_time_weather=True and city_name...")
    response = requests.post(
        "http://localhost:8000/first-ai-agent",
        json={
            "query": "current weather of pune?",
            "include_real_time_weather": True,
            "city_name": "Pune"
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response received")
        print(f"Has real_time_weather: {'real_time_weather' in data}")
        if 'real_time_weather' in data:
            print(f"Weather data: {json.dumps(data['real_time_weather'], indent=2)}")
        else:
            print("❌ No real_time_weather in response")
            print(f"Available keys: {list(data.keys())}")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test 2: Without city_name but with include_real_time_weather=True
    print("\n2. Testing with include_real_time_weather=True but no city_name...")
    response = requests.post(
        "http://localhost:8000/first-ai-agent",
        json={
            "query": "current weather of pune?",
            "include_real_time_weather": True
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response received")
        print(f"Has real_time_weather: {'real_time_weather' in data}")
        if 'real_time_weather' in data:
            print(f"Weather data: {json.dumps(data['real_time_weather'], indent=2)}")
        else:
            print("❌ No real_time_weather in response")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_api_endpoint() 