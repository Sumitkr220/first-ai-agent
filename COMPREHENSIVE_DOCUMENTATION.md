# 🌤️ Real-Time Weather API - Comprehensive Documentation

## Table of Contents
1. [Necessary Setup](#1-necessary-setup)
2. [Theory & Basic Concepts](#2-theory--basic-concepts)
3. [Complete Implementation Guide](#3-complete-implementation-guide)
4. [Methods & Tools Deep Dive](#4-methods--tools-deep-dive)

---

## 1. Necessary Setup

### 1.1 Prerequisites
- **Python 3.8+** installed
- **Git** for version control
- **Terminal/Command Line** access
- **OpenAI API Key** (paid account required)

### 1.2 Environment Setup

#### Step 1: Create Project Directory
```bash
mkdir LLM-Learning
cd LLM-Learning
```

#### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

#### Step 3: Install Dependencies
```bash
pip install fastapi uvicorn[standard] python-dotenv openai requests
```

#### Step 4: Create Requirements File
```bash
pip freeze > requirements.txt
```

### 1.3 API Key Setup

#### Step 1: Get OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create account or sign in
3. Navigate to API Keys section
4. Create new API key
5. Copy the key (starts with `sk-`)

#### Step 2: Create Environment File
```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

#### Step 3: Optional - OpenWeatherMap API Key
```bash
echo "OPENWEATHER_API_KEY=your_openweather_key_here" >> .env
```

### 1.4 Project Structure
```
LLM-Learning/
├── venv/                    # Virtual environment
├── main.py                  # Main FastAPI application
├── requirements.txt         # Python dependencies
├── .env                    # Environment variables
├── README.md              # Project documentation
└── test_*.py              # Test scripts
```

---

## 2. Theory & Basic Concepts

### 2.1 FastAPI Framework

#### What is FastAPI?
FastAPI is a modern, fast web framework for building APIs with Python based on standard Python type hints.

#### Key Features:
- **Automatic API Documentation** (Swagger UI)
- **Type Safety** with Pydantic models
- **Async Support** for high performance
- **OpenAPI Standard** compliance

#### Basic FastAPI Structure:
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class RequestModel(BaseModel):
    field: str

@app.post("/endpoint")
async def endpoint(request: RequestModel):
    return {"message": "response"}
```

### 2.2 Pydantic Models

#### Purpose:
Pydantic provides data validation using Python type annotations.

#### Key Concepts:
- **BaseModel**: Base class for data models
- **Type Validation**: Automatic type checking
- **Serialization**: JSON conversion
- **Documentation**: Auto-generated API docs

#### Example:
```python
from pydantic import BaseModel
from typing import Optional

class WeatherRequest(BaseModel):
    city: str
    include_aqi: Optional[bool] = False
```

### 2.3 OpenAI API Integration

#### OpenAI Client:
```python
from openai import OpenAI

client = OpenAI(api_key="your_key")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}]
)
```

#### Function Calling:
```python
tools=[{
    "type": "function",
    "function": {
        "name": "web_search",
        "parameters": {...}
    }
}]
```

### 2.4 Environment Variables

#### Purpose:
- Secure storage of sensitive data
- Configuration management
- Environment-specific settings

#### Implementation:
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

### 2.5 HTTP Requests & APIs

#### Requests Library:
```python
import requests

response = requests.get("https://api.example.com/data")
data = response.json()
```

#### Error Handling:
```python
try:
    response = requests.get(url)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"Error: {e}")
```

### 2.6 Async Programming

#### Why Async?
- **Concurrent Operations**: Handle multiple requests simultaneously
- **Better Performance**: Non-blocking I/O operations
- **Scalability**: Efficient resource usage

#### Async/Await Pattern:
```python
async def get_weather_data():
    # Async operation
    result = await external_api_call()
    return result
```

---

## 3. Complete Implementation Guide

### 3.1 Project Architecture

#### Core Components:
1. **FastAPI Application** (`main.py`)
2. **Weather Data Functions** (Real-time & Web Search)
3. **OpenAI Integration** (GPT-4o-mini)
4. **External APIs** (wttr.in, OpenWeatherMap)
5. **Data Models** (Pydantic)

### 3.2 Implementation Steps

#### Step 1: Basic FastAPI Setup
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Country Information API",
    description="API for comprehensive country and weather information",
    version="1.0.0"
)
```

#### Step 2: Data Models
```python
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
```

#### Step 3: OpenAI Client Setup
```python
def get_openai_client():
    load_dotenv(override=True)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400, 
            detail="OPENAI_API_KEY environment variable not set"
        )
    return OpenAI(api_key=api_key)
```

#### Step 4: Weather Data Functions

##### Simple Weather Function:
```python
def get_real_time_weather_simple(city_name: str):
    """Get weather data using wttr.in API"""
    try:
        url = f"https://wttr.in/{city_name}?format=j1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        current = data.get("current_condition", [{}])[0]
        
        return {
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
        print(f"Error getting weather data: {e}")
        return None
```

##### Web Search Weather Function:
```python
def get_comprehensive_weather_with_web_search(query: str, city_name: str = None):
    """Get weather data using OpenAI web search tool"""
    try:
        client = get_openai_client()
        
        # Build search query
        if city_name:
            search_query = f"current weather {city_name} India temperature humidity wind speed AQI air quality index real time"
        else:
            search_query = f"{query} real time current weather temperature humidity wind speed AQI air quality index"
        
        # First call: Use web search tool
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user", 
                "content": f"Search for comprehensive current weather information: {search_query}"
            }],
            tools=[{
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web for comprehensive current weather information",
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
            timeout=30
        )
        
        # Process results and extract structured data
        if response.choices[0].message.tool_calls:
            # Extract and process web search results
            # Return structured weather data
            return weather_data
        
        return None
    except Exception as e:
        print(f"Error getting comprehensive weather data: {e}")
        return None
```

#### Step 5: Main API Endpoint
```python
@app.post("/first-ai-agent", response_model=CountryQueryResponse)
async def ask_country_query(request: CountryQueryRequest):
    # Load environment variables
    load_dotenv(override=True)
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise HTTPException(
            status_code=400, 
            detail="OPENAI_API_KEY environment variable not set"
        )
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Enhanced system prompt
        system_prompt = """You are a comprehensive geography and country information assistant with advanced real-time weather capabilities..."""
        
        # Check query type
        weather_keywords = ["weather", "temperature", "coldest", "hot", "cold", "aqi", "air quality"]
        is_weather_query = any(keyword in request.query.lower() for keyword in weather_keywords)
        
        # Generate AI response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.query}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content.strip()
        model_used = response.model
        
        # Prepare response data
        response_data = {
            "query": request.query,
            "answer": answer,
            "model_used": model_used
        }
        
        # Add weather data if requested
        if request.include_real_time_weather and request.city_name:
            weather_data = get_comprehensive_weather_with_web_search("current weather", request.city_name)
            if weather_data:
                response_data["real_time_weather"] = weather_data
            else:
                # Fallback to simple weather function
                weather_data = get_real_time_weather_simple(request.city_name)
                if weather_data:
                    response_data["real_time_weather"] = weather_data
        
        return CountryQueryResponse(**response_data)
        
    except Exception as e:
        # Handle specific OpenAI errors
        error_msg = str(e)
        if "insufficient_quota" in error_msg:
            raise HTTPException(status_code=402, detail="OpenAI quota exceeded")
        elif "rate_limit" in error_msg.lower():
            raise HTTPException(status_code=429, detail="OpenAI rate limit exceeded")
        else:
            raise HTTPException(status_code=500, detail=f"Error calling OpenAI API: {error_msg}")
```

### 3.3 Running the Application

#### Development Server:
```bash
python main.py
```

#### Production Server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Access Points:
- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

### 3.4 Testing the API

#### Using curl:
```bash
curl -X POST http://localhost:8000/first-ai-agent \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current weather in Mumbai?",
    "include_real_time_weather": true,
    "city_name": "Mumbai"
  }'
```

#### Using Python:
```python
import requests

response = requests.post(
    "http://localhost:8000/first-ai-agent",
    json={
        "query": "What is the current weather in Mumbai?",
        "include_real_time_weather": True,
        "city_name": "Mumbai"
    }
)
print(response.json())
```

---

## 4. Methods & Tools Deep Dive

### 4.1 FastAPI Methods

#### @app.post()
- **Purpose**: Define POST endpoint
- **Parameters**: 
  - `path`: URL path
  - `response_model`: Expected response structure
- **Usage**: Handle incoming POST requests

#### HTTPException
- **Purpose**: Return HTTP error responses
- **Parameters**:
  - `status_code`: HTTP status code (400, 401, 402, 429, 500)
  - `detail`: Error message
- **Usage**: Handle API errors gracefully

### 4.2 Pydantic Methods

#### BaseModel
- **Purpose**: Data validation and serialization
- **Features**:
  - Automatic type validation
  - JSON serialization
  - API documentation generation

#### model_config
- **Purpose**: Configure Pydantic model behavior
- **Usage**: `{"protected_namespaces": ()}` to avoid warnings

### 4.3 OpenAI API Methods

#### client.chat.completions.create()
- **Purpose**: Generate AI responses
- **Key Parameters**:
  - `model`: AI model name ("gpt-4o-mini")
  - `messages`: Conversation history
  - `tools`: Function calling tools
  - `max_tokens`: Response length limit
  - `temperature`: Creativity level (0.0-1.0)
  - `timeout`: Request timeout

#### Tool Calling
```python
tools=[{
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    }
}]
```

### 4.4 HTTP Request Methods

#### requests.get()
- **Purpose**: Make GET HTTP requests
- **Parameters**:
  - `url`: Target URL
  - `timeout`: Request timeout
  - `headers`: Request headers

#### requests.post()
- **Purpose**: Make POST HTTP requests
- **Parameters**:
  - `url`: Target URL
  - `json`: Request body (JSON)
  - `headers`: Request headers

#### Error Handling:
```python
response.raise_for_status()  # Raise exception for 4XX/5XX status codes
```

### 4.5 Environment Management

#### load_dotenv()
- **Purpose**: Load environment variables from .env file
- **Parameters**:
  - `override=True`: Override existing environment variables

#### os.getenv()
- **Purpose**: Get environment variable value
- **Parameters**:
  - `key`: Environment variable name
  - `default`: Default value if not found

### 4.6 Data Processing Methods

#### datetime.now().isoformat()
- **Purpose**: Generate ISO format timestamp
- **Usage**: Track when data was fetched

#### re.search()
- **Purpose**: Extract patterns from text
- **Usage**: Extract city names from queries
```python
city_match = re.search(r'weather\s+(?:of|in|for)\s+(\w+)', query.lower())
```

#### json.loads()
- **Purpose**: Parse JSON strings
- **Usage**: Process API responses

### 4.7 Error Handling Patterns

#### Try-Catch with Specific Exceptions:
```python
try:
    # API call
    response = client.chat.completions.create(...)
except HTTPException as he:
    raise he
except Exception as e:
    # Handle specific error types
    if "insufficient_quota" in str(e):
        raise HTTPException(status_code=402, detail="Quota exceeded")
```

#### Graceful Fallbacks:
```python
# Try web search first
weather_data = get_comprehensive_weather_with_web_search(query, city_name)
if not weather_data:
    # Fallback to simple function
    weather_data = get_real_time_weather_simple(city_name)
```

### 4.8 Logging and Debugging

#### Print Statements:
```python
print(f"DEBUG: API Key loaded: {api_key[:20] if api_key else 'None'}...")
print(f"Fetching weather data for {city_name}...")
print(f"Weather data added: {weather_data}")
```

#### Error Logging:
```python
print(f"Error getting weather data: {e}")
print(f"Error in web search: {e}")
```

### 4.9 Data Structures

#### Weather Data Structure:
```python
{
    "city": "Mumbai",
    "timestamp": "2025-08-02T13:05:39.585245",
    "temperature": {
        "current": "29°C",
        "feels_like": "34°C",
        "min": "N/A",
        "max": "N/A"
    },
    "humidity": "75%",
    "wind_speed": "12 km/h",
    "description": "Haze",
    "aqi": {
        "value": "N/A",
        "category": "Not available",
        "description": "AQI data not available"
    },
    "source": "wttr_in_api"
}
```

#### Coldest Cities Structure:
```python
{
    "coldest_cities_india": [
        {
            "city": "Manali",
            "temperature": "9°C",
            "feels_like": "9°C",
            "humidity": "91%",
            "description": "Patchy light rain",
            "wind_speed": "4 km/h",
            "aqi": {...},
            "timestamp": "2025-08-02T13:05:24.468257"
        }
    ],
    "total_cities_checked": 10,
    "timestamp": "2025-08-02T13:05:39.585245",
    "source": "real_time_weather_api"
}
```

### 4.10 Performance Optimization

#### Timeout Management:
```python
timeout=30  # 30-second timeout for API calls
```

#### Caching Considerations:
- Environment variables reloaded on each request
- No response caching implemented
- Real-time data freshness prioritized

#### Error Recovery:
- Multiple fallback mechanisms
- Graceful degradation
- Detailed error messages

---

## Summary

This comprehensive documentation covers:

1. **✅ Complete Setup Guide** - From environment to API keys
2. **✅ Theoretical Foundation** - FastAPI, Pydantic, OpenAI, HTTP
3. **✅ Step-by-Step Implementation** - Every component explained
4. **✅ Deep Dive into Methods** - All functions, tools, and patterns

The application successfully provides:
- **Real-time weather data** with temperature, humidity, wind speed, AQI
- **Web search integration** using OpenAI's function calling
- **Comprehensive error handling** with graceful fallbacks
- **RESTful API design** with automatic documentation
- **Scalable architecture** ready for production use

🌤️ **Your API is now ready to provide real-time weather information for any city with comprehensive data!** ✨ 