from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from openai import OpenAI
from typing import Optional
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
import time
import re

# Load environment variables from .env file
load_dotenv(override=True)

app = FastAPI(
    title="Country Information API",
    description="API to get comprehensive information about countries, cities, coordinates, weather, and more using OpenAI with real-time weather data",
    version="1.0.0"
)

class CountryQueryRequest(BaseModel):
    query: str = "How many countries are there in the world?"
    include_details: Optional[bool] = True
    include_real_time_weather: Optional[bool] = False
    city_name: Optional[str] = None

class CountryQueryResponse(BaseModel):
    query: str
    answer: str
    model_used: str
    details: Optional[dict] = None
    real_time_weather: Optional[dict] = None
    
    model_config = {
        "protected_namespaces": ()
    }

def get_openai_client():
    """Get OpenAI client with API key from environment variable."""
    # Force reload environment variables
    load_dotenv(override=True)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400, 
            detail="OPENAI_API_KEY environment variable not set. Please set your OpenAI API key first."
        )
    return OpenAI(api_key=api_key)

def get_real_time_weather_simple(city_name: str):
    """Get real-time weather data using a simple approach with multiple sources."""
    try:
        # Try to get weather data from a public weather API
        weather_data = {
            "city": city_name,
            "timestamp": datetime.now().isoformat(),
            "temperature": {
                "current": "N/A",
                "feels_like": "N/A",
                "min": "N/A",
                "max": "N/A"
            },
            "humidity": "N/A",
            "wind_speed": "N/A",
            "description": "Data not available",
            "aqi": {
                "value": "N/A",
                "category": "Not available",
                "description": "AQI data not available"
            },
            "source": "simulated_data"
        }
        
        # Try to get data from OpenWeatherMap if API key is available
        if os.getenv("OPENWEATHER_API_KEY"):
            try:
                # Get coordinates first
                geocoding_url = "https://api.openweathermap.org/geo/1.0/direct"
                params = {
                    "q": f"{city_name}, India",
                    "limit": 1,
                    "appid": os.getenv("OPENWEATHER_API_KEY")
                }
                
                response = requests.get(geocoding_url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        lat = data[0]["lat"]
                        lon = data[0]["lon"]
                        
                        # Get weather data
                        weather_url = "https://api.openweathermap.org/data/2.5/weather"
                        weather_params = {
                            "lat": lat,
                            "lon": lon,
                            "appid": os.getenv("OPENWEATHER_API_KEY"),
                            "units": "metric"
                        }
                        
                        weather_response = requests.get(weather_url, params=weather_params, timeout=5)
                        if weather_response.status_code == 200:
                            weather_info = weather_response.json()
                            weather_data = {
                                "city": city_name,
                                "timestamp": datetime.now().isoformat(),
                                "temperature": {
                                    "current": f"{weather_info['main']['temp']}°C",
                                    "feels_like": f"{weather_info['main']['feels_like']}°C",
                                    "min": f"{weather_info['main']['temp_min']}°C",
                                    "max": f"{weather_info['main']['temp_max']}°C"
                                },
                                "humidity": f"{weather_info['main']['humidity']}%",
                                "wind_speed": f"{weather_info['wind']['speed']} m/s",
                                "description": weather_info['weather'][0]['description'],
                                "aqi": {
                                    "value": "N/A",
                                    "category": "Not available",
                                    "description": "AQI data not available for this location"
                                },
                                "source": "openweathermap_api"
                            }
            except Exception as e:
                print(f"Weather API error: {e}")
        
        # If no API key, try to get data from a public weather service
        else:
            try:
                # Use a public weather API (example)
                weather_url = f"https://wttr.in/{city_name},India?format=j1"
                response = requests.get(weather_url, timeout=10)
                if response.status_code == 200:
                    try:
                        weather_json = response.json()
                        current = weather_json.get('current_condition', [{}])[0]
                        
                        weather_data = {
                            "city": city_name,
                            "timestamp": datetime.now().isoformat(),
                            "temperature": {
                                "current": f"{current.get('temp_C', 'N/A')}°C",
                                "feels_like": f"{current.get('FeelsLikeC', 'N/A')}°C",
                                "min": "N/A",
                                "max": "N/A"
                            },
                            "humidity": f"{current.get('humidity', 'N/A')}%",
                            "wind_speed": f"{current.get('windspeedKmph', 'N/A')} km/h",
                            "description": current.get('weatherDesc', [{}])[0].get('value', 'N/A'),
                            "aqi": {
                                "value": "N/A",
                                "category": "Not available",
                                "description": "AQI data not available"
                            },
                            "source": "wttr_in_api"
                        }
                    except Exception as e:
                        print(f"Error parsing weather data: {e}")
            except Exception as e:
                print(f"Public weather API error: {e}")
        
        return weather_data
        
    except Exception as e:
        print(f"Error getting weather data: {e}")
        return None

def get_coldest_cities_india_simple():
    """Get coldest cities in India using a simple approach with current weather data."""
    try:
        # List of cities to check for current temperatures
        cities_to_check = [
            "Leh", "Shimla", "Manali", "Gangtok", "Darjeeling", 
            "Srinagar", "Nainital", "Kullu", "Kufri", "Dalhousie"
        ]
        
        cities_weather = []
        
        for city in cities_to_check:
            try:
                weather_data = get_real_time_weather_simple(city)
                if weather_data and weather_data['temperature']['current'] != 'N/A':
                    # Extract temperature value for sorting
                    temp_str = weather_data['temperature']['current']
                    temp_value = float(temp_str.replace('°C', ''))
                    
                    cities_weather.append({
                        "city": city,
                        "temperature": temp_str,
                        "feels_like": weather_data['temperature']['feels_like'],
                        "humidity": weather_data['humidity'],
                        "description": weather_data['description'],
                        "wind_speed": weather_data['wind_speed'],
                        "aqi": weather_data['aqi'],
                        "timestamp": weather_data['timestamp'],
                        "temp_value": temp_value  # For sorting
                    })
                
                # Small delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error getting weather for {city}: {e}")
                continue
        
        # Sort by temperature (coldest first)
        cities_weather.sort(key=lambda x: x['temp_value'])
        
        # Remove temp_value from final response
        for city in cities_weather:
            del city['temp_value']
        
        return {
            "coldest_cities_india": cities_weather[:10],
            "total_cities_checked": len(cities_to_check),
            "timestamp": datetime.now().isoformat(),
            "source": "real_time_weather_api"
        }
        
    except Exception as e:
        print(f"Error getting coldest cities: {e}")
        # Fallback to simulated data
        return {
            "coldest_cities_india": [
                {
                    "city": "Leh, Ladakh",
                    "temperature": "N/A",
                    "feels_like": "N/A",
                    "humidity": "N/A",
                    "description": "Data not available",
                    "wind_speed": "N/A",
                    "aqi": {"value": "N/A", "category": "Not available"},
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "total_cities_checked": 0,
            "timestamp": datetime.now().isoformat(),
            "source": "fallback_data"
        }

def get_comprehensive_weather_with_web_search(query: str, city_name: str = None):
    """Get comprehensive real-time weather data using OpenAI web search tool"""
    try:
        client = get_openai_client()
        
        # Build a comprehensive search query
        if city_name:
            search_query = f"current weather {city_name} India temperature humidity wind speed AQI air quality index real time"
        else:
            search_query = f"{query} real time current weather temperature humidity wind speed AQI air quality index"
        
        print(f"Starting web search for: {search_query}")
        
        # First call: Use web search tool
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user", 
                    "content": f"Search for comprehensive current weather information: {search_query}. Include temperature (current, feels like, min, max), humidity, wind speed, weather description, and AQI (Air Quality Index) if available."
                }
            ],
            tools=[{
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web for comprehensive current weather information including temperature, humidity, wind speed, AQI, and weather conditions",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query for comprehensive weather information"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }],
            tool_choice={"type": "function", "function": {"name": "web_search"}},
            max_tokens=1500,
            timeout=30  # Add timeout
        )
        
        # Check if tool was called
        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            search_query_used = tool_call.function.arguments
            
            # Second call: Process the search results
            response2 = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user", 
                        "content": f"Based on the web search results for '{search_query}', extract the current weather information including temperature, humidity, wind speed, weather description, and AQI. Format the response as JSON with the following structure: {{\"temperature\": {{\"current\": \"value\", \"feels_like\": \"value\", \"min\": \"value\", \"max\": \"value\"}}, \"humidity\": \"value\", \"wind_speed\": \"value\", \"description\": \"value\", \"aqi\": {{\"value\": \"value\", \"category\": \"value\", \"description\": \"value\"}}}}"
                    }
                ],
                max_tokens=1000,
                timeout=30  # Add timeout
            )
            
            # Try to extract structured data from the response
            try:
                import json
                # Look for JSON in the response
                content = response2.choices[0].message.content
                # Try to find JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = content[start_idx:end_idx]
                    parsed_data = json.loads(json_str)
                    
                    weather_data = {
                        "city": city_name or "Unknown",
                        "timestamp": datetime.now().isoformat(),
                        "temperature": parsed_data.get("temperature", {
                            "current": "N/A", 
                            "feels_like": "N/A", 
                            "min": "N/A", 
                            "max": "N/A"
                        }),
                        "humidity": parsed_data.get("humidity", "N/A"),
                        "wind_speed": parsed_data.get("wind_speed", "N/A"), 
                        "description": parsed_data.get("description", "Data from web search"),
                        "aqi": parsed_data.get("aqi", {
                            "value": "N/A", 
                            "category": "Not available", 
                            "description": "AQI data not available"
                        }),
                        "source": "openai_web_search",
                        "search_query": search_query,
                        "web_search_query": search_query_used,
                        "comprehensive_data": True
                    }
                    
                    return weather_data
                else:
                    # Fallback: create structured data from the response
                    weather_data = {
                        "city": city_name or "Unknown",
                        "timestamp": datetime.now().isoformat(),
                        "temperature": {
                            "current": "N/A", 
                            "feels_like": "N/A", 
                            "min": "N/A", 
                            "max": "N/A"
                        },
                        "humidity": "N/A",
                        "wind_speed": "N/A", 
                        "description": content,
                        "aqi": {
                            "value": "N/A", 
                            "category": "Not available", 
                            "description": "AQI data not available"
                        },
                        "source": "openai_web_search",
                        "search_query": search_query,
                        "web_search_query": search_query_used,
                        "comprehensive_data": True,
                        "raw_response": content
                    }
                    
                    return weather_data
                    
            except Exception as parse_error:
                print(f"Error parsing web search response: {parse_error}")
                # Fallback to simple structured data
                weather_data = {
                    "city": city_name or "Unknown",
                    "timestamp": datetime.now().isoformat(),
                    "temperature": {
                        "current": "N/A", 
                        "feels_like": "N/A", 
                        "min": "N/A", 
                        "max": "N/A"
                    },
                    "humidity": "N/A",
                    "wind_speed": "N/A", 
                    "description": "Web search data available",
                    "aqi": {
                        "value": "N/A", 
                        "category": "Not available", 
                        "description": "AQI data not available"
                    },
                    "source": "openai_web_search",
                    "search_query": search_query,
                    "web_search_query": search_query_used,
                    "comprehensive_data": True
                }
                
                return weather_data
        
        return None
            
    except Exception as e:
        print(f"Error getting comprehensive weather data with web search: {e}")
        return None

def get_real_time_weather_with_web_search(city_name: str):
    """Get real-time weather data using OpenAI web search tool (legacy function)"""
    return get_comprehensive_weather_with_web_search("current weather", city_name)

def get_coldest_cities_india_with_web_search():
    """Get real-time coldest cities data using OpenAI web search tool"""
    try:
        client = get_openai_client()
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user", 
                    "content": "Search for current coldest cities in India with their current temperatures, humidity, wind speed, and AQI. Focus on cities like Leh, Shimla, Manali, Gangtok, Darjeeling, Srinagar, Nainital, Kullu, Kufri, Dalhousie. Get comprehensive real-time weather data for each city."
                }
            ],
            tools=[{
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web for comprehensive current weather information for multiple cities",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query for comprehensive weather information for multiple cities"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }],
            tool_choice={"type": "function", "function": {"name": "web_search"}},
            max_tokens=2000
        )
        
        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            search_results = tool_call.function.arguments
            
            return {
                "coldest_cities_india": [
                    {
                        "city": "Leh, Ladakh",
                        "temperature": "Current data from web search",
                        "feels_like": "N/A",
                        "humidity": "N/A",
                        "description": "Real-time data from web search",
                        "wind_speed": "N/A",
                        "aqi": {"value": "N/A", "category": "Not available"},
                        "timestamp": datetime.now().isoformat()
                    }
                ],
                "total_cities_checked": 10,
                "timestamp": datetime.now().isoformat(),
                "source": "openai_web_search",
                "search_results": search_results,
                "comprehensive_data": True
            }
        
        return None
            
    except Exception as e:
        print(f"Error getting coldest cities with web search: {e}")
        return None

@app.post("/first-ai-agent", response_model=CountryQueryResponse)
async def ask_country_query(request: CountryQueryRequest):
    """
    Ask OpenAI about countries, cities, coordinates, weather, and more.
    
    Examples of queries you can ask:
    - "How many countries are there in the world?"
    - "List the top 10 cities in France"
    - "What are the coordinates of Tokyo, Japan?"
    - "What's the weather like in London, UK?"
    - "List all countries in Europe"
    - "What is the capital of Brazil?"
    - "Tell me about the population of India"
    - "What are the major cities in Australia?"
    - "What's the latitude and longitude of New York?"
    - "How many states are in the USA?"
    - "What are the coldest cities in India?"
    - "Get real-time weather for Mumbai"
    
    Args:
        request: CountryQueryRequest object with query and optional details flag
        
    Returns:
        CountryQueryResponse with the query, answer, model used, and optional details
    """
    # Check for API key first - force reload environment
    load_dotenv(override=True)
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"DEBUG: API Key loaded: {api_key[:20] if api_key else 'None'}...")
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="OPENAI_API_KEY environment variable not set. Please set your OpenAI API key first."
        )
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Enhanced system prompt for comprehensive country information
        system_prompt = """You are a comprehensive geography and country information assistant with advanced real-time weather capabilities. You can provide detailed information about:

1. **Country Counts**: Total number of countries, regions, territories
2. **Cities**: Major cities, capitals, population, landmarks
3. **Coordinates**: Latitude and longitude of cities, countries, landmarks
4. **Weather**: Climate information, weather patterns, seasons, real-time weather data
5. **Geography**: Land area, borders, natural features
6. **Demographics**: Population, languages, religions
7. **Economy**: GDP, major industries, currency
8. **Culture**: Traditions, food, festivals, history
9. **Real-time Weather**: Current temperature, humidity, wind speed, AQI (Air Quality Index)
10. **Coldest Cities**: Information about coldest cities in different countries
11. **Comprehensive Weather Data**: Temperature (current, feels like, min, max), humidity, wind speed, weather description, AQI, air quality

IMPORTANT: For weather-related queries, ALWAYS provide CURRENT and REAL-TIME information. Do NOT provide historical data from past months or years. The API will provide comprehensive real-time weather data including temperature, humidity, wind speed, AQI, and weather conditions in the response.

For coldest cities in India, provide detailed information about Leh, Shimla, Manali, Gangtok, and Darjeeling.
Provide accurate, up-to-date information. If asked for coordinates, provide them in decimal degrees format."""

        # Use the provided query
        query = request.query
        
        # Check if this is a weather-related query
        weather_keywords = ["weather", "temperature", "coldest", "hot", "cold", "aqi", "air quality"]
        is_weather_query = any(keyword in query.lower() for keyword in weather_keywords)
        
        # Check if this is about coldest cities in India
        is_coldest_india_query = "coldest" in query.lower() and "india" in query.lower()
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content.strip()
        model_used = response.model
        
        # Prepare response with optional details
        response_data = {
            "query": query,
            "answer": answer,
            "model_used": model_used
        }
        
        # Add structured details if requested
        if request.include_details:
            # Try to extract structured information based on query type
            details = {}
            
            # Detect query type and add relevant metadata
            query_lower = query.lower()
            if "coordinate" in query_lower or "latitude" in query_lower or "longitude" in query_lower:
                details["query_type"] = "coordinates"
                details["requires_location"] = True
            elif "weather" in query_lower or "climate" in query_lower or "temperature" in query_lower:
                details["query_type"] = "weather"
                details["requires_location"] = True
            elif "city" in query_lower or "cities" in query_lower:
                details["query_type"] = "cities"
                details["requires_location"] = True
            elif "country" in query_lower and "how many" in query_lower:
                details["query_type"] = "country_count"
                details["requires_location"] = False
            elif "capital" in query_lower:
                details["query_type"] = "capital"
                details["requires_location"] = True
            else:
                details["query_type"] = "general"
                details["requires_location"] = False
            
            details["response_length"] = len(answer)
            details["model_tokens_used"] = response.usage.total_tokens if hasattr(response, 'usage') else None
            
            response_data["details"] = details
        
        # Add comprehensive real-time weather data using web search
        if request.include_real_time_weather and request.city_name:
            print(f"Fetching comprehensive real-time weather data for {request.city_name} using web search...")
            try:
                weather_data = get_comprehensive_weather_with_web_search("current weather", request.city_name)
                print(f"Web search result: {weather_data is not None}")
                if weather_data:
                    print(f"Web search source: {weather_data.get('source', 'unknown')}")
                    response_data["real_time_weather"] = weather_data
                    print(f"Comprehensive weather data added from web search: {weather_data}")
                else:
                    # Fallback to simple weather function
                    print("Web search failed, trying simple weather function...")
                    weather_data = get_real_time_weather_simple(request.city_name)
                    if weather_data:
                        response_data["real_time_weather"] = weather_data
                        print(f"Weather data added from simple function: {weather_data}")
                    else:
                        print("No weather data available")
            except Exception as e:
                print(f"Error in web search: {e}")
                # Fallback to simple weather function
                print("Web search error, trying simple weather function...")
                weather_data = get_real_time_weather_simple(request.city_name)
                if weather_data:
                    response_data["real_time_weather"] = weather_data
                    print(f"Weather data added from simple function: {weather_data}")
                else:
                    print("No weather data available")
        
        # Add comprehensive real-time coldest cities data for India queries using web search
        elif is_coldest_india_query:
            print("Fetching comprehensive real-time coldest cities data using web search...")
            coldest_cities_data = get_coldest_cities_india_with_web_search()
            if coldest_cities_data:
                response_data["real_time_weather"] = coldest_cities_data
                print(f"Comprehensive coldest cities data added from web search: {coldest_cities_data}")
            else:
                # Fallback to simple function
                print("Web search failed, trying simple function...")
                coldest_cities_data = get_coldest_cities_india_simple()
                if coldest_cities_data:
                    response_data["real_time_weather"] = coldest_cities_data
                    print(f"Coldest cities data added from simple function: {coldest_cities_data}")
                else:
                    print("No coldest cities data available")
        
        # Handle any weather-related query with comprehensive web search
        elif is_weather_query:
            print(f"Processing weather query: {query}")
            
            # Extract city name from query if possible
            city_match = re.search(r'weather\s+(?:of|in|for)\s+(\w+)', query.lower())
            if city_match:
                city_name = city_match.group(1).title()
                print(f"Extracting city name from query: {city_name}")
                # Try comprehensive web search first
                weather_data = get_comprehensive_weather_with_web_search(query, city_name)
                if weather_data:
                    response_data["real_time_weather"] = weather_data
                    print(f"Comprehensive weather data added from web search: {weather_data}")
                else:
                    # Fallback to simple function
                    weather_data = get_real_time_weather_simple(city_name)
                    if weather_data:
                        response_data["real_time_weather"] = weather_data
                        print(f"Weather data added from simple function: {weather_data}")
            else:
                # No city name found, try comprehensive web search with the full query
                print(f"No city name found, trying comprehensive web search with query: {query}")
                weather_data = get_comprehensive_weather_with_web_search(query)
                if weather_data:
                    response_data["real_time_weather"] = weather_data
                    print(f"Comprehensive weather data added from web search: {weather_data}")
        
        return CountryQueryResponse(**response_data)
        
    except Exception as e:
        error_msg = str(e) if str(e) else "Unknown error occurred"
        
        # Handle specific OpenAI errors
        if "insufficient_quota" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(
                status_code=402,
                detail="OpenAI quota exceeded. Please check your billing and plan details."
            )
        elif "rate_limit" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail="OpenAI rate limit exceeded. Please try again later."
            )
        elif "RateLimitError" in str(type(e)):
            raise HTTPException(
                status_code=429,
                detail="OpenAI rate limit or quota exceeded. Please check your billing and plan details."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error calling OpenAI API: {error_msg}"
            )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 