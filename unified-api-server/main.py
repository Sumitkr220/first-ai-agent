import os
import re
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import pdfplumber
from sentence_transformers import SentenceTransformer
import faiss
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv(override=True)

# Initialize FastAPI app
app = FastAPI(title="Unified AI Agent API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class GeoWeatherRequest(BaseModel):
    query: str
    include_details: Optional[bool] = False

class GeoWeatherResponse(BaseModel):
    query: str
    answer: str
    model_used: str
    details: Optional[Dict[str, Any]] = None
    real_time_weather: Optional[Dict[str, Any]] = None
    
    model_config = {"protected_namespaces": ()}

class PDFRAGRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class PDFRAGResponse(BaseModel):
    query: str
    answer: str
    model_used: str
    relevant_chunks: List[Dict[str, Any]]
    total_chunks_processed: int
    
    model_config = {"protected_namespaces": ()}

class ProductsRAGRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class ProductsRAGResponse(BaseModel):
    query: str
    answer: str
    model_used: str
    relevant_products: List[Dict[str, Any]]
    total_products_processed: int
    
    model_config = {"protected_namespaces": ()}

class AgenticRequest(BaseModel):
    query: str
    include_details: Optional[bool] = False

class AgenticResponse(BaseModel):
    query: str
    answer: str
    tool_used: str
    confidence: float
    reasoning: str
    model_used: str
    raw_response: Dict[str, Any]
    
    model_config = {"protected_namespaces": ()}

# Simplified LLM-based Agentic API with Cascading Search
class LLMAgenticAPI:
    def __init__(self, geo_weather_api, pdf_rag_api, products_rag_api):
        self.geo_weather_api = geo_weather_api
        self.pdf_rag_api = pdf_rag_api
        self.products_rag_api = products_rag_api
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze the query to understand intent and extract information"""
        messages = [
            {
                "role": "system",
                "content": """You are an intelligent AI agent that analyzes user queries to understand their intent and extract relevant information.

Available tools:
1. geo-weather: For weather queries, location-based questions, geographical information
2. pdf-rag: For questions about documents, invoices, PDF content analysis
3. products-rag: For questions about products, product information, catalog queries
4. cascading-search: For general queries that might need multiple data sources

Analyze the query and extract any relevant information like city names, locations, etc."""
            },
            {
                "role": "user", 
                "content": f"Analyze this query: {query}"
            }
        ]
        
        response = self.llm.invoke(messages)
        return {"analysis": response.content}
    
    def select_tool(self, query: str, analysis: str) -> Dict[str, Any]:
        """Use LLM to select the appropriate tool with chain of thought reasoning"""
        messages = [
            {
                "role": "system",
                "content": """You are an intelligent tool selector. Based on the query analysis, determine which tool to use.

Available tools:
1. geo-weather: Use for weather queries, location questions, geographical information, city/temperature/climate queries
2. pdf-rag: Use for document analysis, invoice questions, PDF content queries, document-based questions
3. products-rag: Use for product queries, catalog questions, product information, shopping-related queries
4. cascading-search: Use for general queries that might need multiple data sources (PDF first, then CSV, then web search)

Think step by step:
1. What is the user asking for?
2. What type of information do they need?
3. Which tool can provide that information?
4. What is your reasoning?

Respond with a JSON object:
{
    "tool": "tool_name",
    "reasoning": "detailed reasoning for tool selection",
    "confidence": 0.0-1.0,
    "extracted_info": {"key": "value"}
}"""
            },
            {
                "role": "user",
                "content": f"Query: {query}\n\nPrevious analysis: {analysis}\n\nSelect the appropriate tool."
            }
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            # Try to parse JSON response
            tool_selection = json.loads(response.content)
        except:
            # Fallback parsing
            tool_selection = self._parse_tool_selection(response.content)
        
        return tool_selection
    
    def _parse_tool_selection(self, content: str) -> Dict[str, Any]:
        """Fallback parsing for tool selection"""
        content_lower = content.lower()
        
        # Specific tool triggers
        if any(word in content_lower for word in ["weather", "temperature", "climate", "city", "location", "mumbai", "delhi", "kolkata"]):
            return {"tool": "geo-weather", "reasoning": "Weather/location related query", "confidence": 0.8}
        elif any(word in content_lower for word in ["document", "pdf", "invoice", "file", "invoice"]):
            return {"tool": "pdf-rag", "reasoning": "Document/PDF related query", "confidence": 0.8}
        elif any(word in content_lower for word in ["product", "catalog", "item", "shopping", "eyeglasses", "lenskart"]):
            return {"tool": "products-rag", "reasoning": "Product related query", "confidence": 0.8}
        else:
            # For general queries, use cascading search
            return {"tool": "cascading-search", "reasoning": "General query - using cascading search strategy", "confidence": 0.7}
    
    def execute_cascading_search(self, query: str) -> Dict[str, Any]:
        """Execute cascading search: PDF -> CSV -> Web Search"""
        try:
            results = {
                "pdf_result": None,
                "csv_result": None,
                "web_result": None,
                "final_answer": "",
                "sources_used": []
            }
            
            # Step 1: Try PDF RAG
            print(f"🔍 Step 1: Searching PDF data for: {query}")
            try:
                relevant_chunks = self.pdf_rag_api.search_chunks(query, 5)
                if relevant_chunks and any(chunk['similarity_score'] > 0.1 for chunk in relevant_chunks):
                    pdf_result = self.pdf_rag_api.generate_answer(query, relevant_chunks)
                    results["pdf_result"] = pdf_result
                    results["sources_used"].append("pdf")
                    print(f"✅ Found relevant information in PDF")
                else:
                    print(f"❌ No relevant information found in PDF")
            except Exception as e:
                print(f"❌ PDF search failed: {str(e)}")
            
            # Step 2: Try CSV/Products RAG
            print(f"🔍 Step 2: Searching CSV data for: {query}")
            try:
                relevant_products = self.products_rag_api.search_products(query, 5)
                if relevant_products and any(product.get('similarity_score', 0) > 0.1 for product in relevant_products):
                    csv_result = self.products_rag_api.generate_answer(query, relevant_products)
                    results["csv_result"] = csv_result
                    results["sources_used"].append("csv")
                    print(f"✅ Found relevant information in CSV")
                else:
                    print(f"❌ No relevant information found in CSV")
            except Exception as e:
                print(f"❌ CSV search failed: {str(e)}")
            
            # Step 3: Try Web Search (Geo-Weather as fallback)
            print(f"🔍 Step 3: Searching web/weather data for: {query}")
            try:
                web_result = self.geo_weather_api.generate_geo_answer(query)
                if web_result and web_result.get("answer") and "not found" not in web_result.get("answer", "").lower():
                    results["web_result"] = web_result
                    results["sources_used"].append("web")
                    print(f"✅ Found relevant information from web search")
                else:
                    print(f"❌ No relevant information found from web search")
            except Exception as e:
                print(f"❌ Web search failed: {str(e)}")
            
            # Step 4: Combine results
            results["final_answer"] = self._combine_cascading_results(results)
            
            return {
                "tool_result": results,
                "answer": results["final_answer"]
            }
            
        except Exception as e:
            return {
                "tool_result": {"error": str(e)},
                "answer": f"Error executing cascading search: {str(e)}"
            }
    
    def _combine_cascading_results(self, results: Dict[str, Any]) -> str:
        """Combine results from multiple sources"""
        sources_used = results["sources_used"]
        
        if not sources_used:
            return "I couldn't find relevant information from any of the available data sources (PDF, CSV, or web search). Please try rephrasing your question or ask about something else."
        
        combined_answer = f"Based on my search across multiple data sources, here's what I found:\n\n"
        
        if "pdf" in sources_used and results["pdf_result"]:
            combined_answer += f"**From PDF Documents:**\n{results['pdf_result']['answer']}\n\n"
        
        if "csv" in sources_used and results["csv_result"]:
            combined_answer += f"**From Product Database:**\n{results['csv_result']['answer']}\n\n"
        
        if "web" in sources_used and results["web_result"]:
            combined_answer += f"**From Web Search:**\n{results['web_result']['answer']}\n\n"
        
        combined_answer += f"*Sources consulted: {', '.join(sources_used)}*"
        
        return combined_answer
    
    def execute_tool(self, query: str, tool_selection: str) -> Dict[str, Any]:
        """Execute the selected tool"""
        try:
            if tool_selection == "geo-weather":
                result = self.geo_weather_api.generate_geo_answer(query)
                return {
                    "tool_result": result,
                    "answer": result.get("answer", "Weather data not available")
                }
                
            elif tool_selection == "pdf-rag":
                relevant_chunks = self.pdf_rag_api.search_chunks(query, 5)
                if relevant_chunks:
                    result = self.pdf_rag_api.generate_answer(query, relevant_chunks)
                    return {
                        "tool_result": result,
                        "answer": result.get("answer", "PDF data not available")
                    }
                else:
                    return {
                        "tool_result": {"answer": "No relevant information found in the PDF for your question."},
                        "answer": "No relevant information found in the PDF for your question."
                    }
                
            elif tool_selection == "products-rag":
                relevant_products = self.products_rag_api.search_products(query, 5)
                if relevant_products:
                    result = self.products_rag_api.generate_answer(query, relevant_products)
                    return {
                        "tool_result": result,
                        "answer": result.get("answer", "Product data not available")
                    }
                else:
                    return {
                        "tool_result": {"answer": "No relevant products found in the database for your question."},
                        "answer": "No relevant products found in the database for your question."
                    }
                
            elif tool_selection == "cascading-search":
                return self.execute_cascading_search(query)
                
            else:
                return {
                    "tool_result": {},
                    "answer": "Tool not available"
                }
                
        except Exception as e:
            return {
                "tool_result": {"error": str(e)},
                "answer": f"Error executing tool: {str(e)}"
            }
    
    def format_response(self, query: str, tool_result: Dict[str, Any], tool_selection: str) -> str:
        """Format the final response"""
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Format the response for the user in a clear and informative way."
            },
            {
                "role": "user",
                "content": f"Format the final response for the user query: {query}\nTool used: {tool_selection}\nTool result: {tool_result.get('answer', 'No result')}"
            }
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query using LLM-based reasoning"""
        try:
            # Step 1: Analyze query
            analysis_result = self.analyze_query(query)
            analysis = analysis_result["analysis"]
            
            # Step 2: Select tool
            tool_selection = self.select_tool(query, analysis)
            tool = tool_selection.get("tool", "geo-weather")
            reasoning = tool_selection.get("reasoning", "Default reasoning")
            confidence = tool_selection.get("confidence", 0.7)
            
            # Step 3: Execute tool
            tool_result = self.execute_tool(query, tool)
            
            # Step 4: Format response
            final_answer = self.format_response(query, tool_result, tool)
            
            return {
                "query": query,
                "answer": final_answer,
                "tool_used": tool,
                "confidence": confidence,
                "reasoning": reasoning,
                "model_used": "gpt-4o-mini",
                "raw_response": tool_result
            }
            
        except Exception as e:
            return {
                "query": query,
                "answer": f"Error processing query: {str(e)}",
                "tool_used": "error",
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}",
                "model_used": "gpt-4o-mini",
                "raw_response": {"error": str(e)}
            }

# ============================================================================
# GEO WEATHER API CLASS
# ============================================================================

class GeoWeatherAPI:
    def __init__(self):
        self.openai_client = self.get_openai_client()
    
    def get_openai_client(self):
        """Get OpenAI client with API key"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=400, 
                detail="OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
            )
        return OpenAI(api_key=api_key)
    
    def get_real_time_weather_with_web_search(self, city_name: str) -> Dict[str, Any]:
        """Get real-time weather data using wttr.in API (same as openai-geo-weather)"""
        try:
            print(f"🔍 Getting real-time weather for {city_name} using wttr.in...")
            
            # Use wttr.in API directly (same as the working openai-geo-weather implementation)
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
                    print(f"✅ wttr.in data for {city_name}: {current.get('temp_C', 'N/A')}°C, {current.get('humidity', 'N/A')}% humidity")
                    return weather_data
                except Exception as e:
                    print(f"Error parsing weather data: {e}")
            else:
                print(f"❌ wttr.in API failed for {city_name}: {response.status_code}")
            
            # Fallback to simple method
            print(f"🔄 Falling back to simple weather method for {city_name}")
            return self.get_real_time_weather_simple(city_name)
            
        except Exception as e:
            print(f"❌ Weather data failed for {city_name}: {str(e)}")
            # Fallback to simple method
            return self.get_real_time_weather_simple(city_name)
    
    def get_real_time_weather_simple(self, city_name: str) -> Dict[str, Any]:
        """Get real-time weather data using a simple approach with multiple sources (same as openai-geo-weather)"""
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
                            print(f"✅ wttr.in data for {city_name}: {current.get('temp_C', 'N/A')}°C, {current.get('humidity', 'N/A')}% humidity")
                            return weather_data
                        except Exception as e:
                            print(f"Error parsing weather data: {e}")
                except Exception as e:
                    print(f"Public weather API error: {e}")
            
            return weather_data
            
        except Exception as e:
            print(f"Error getting weather data: {e}")
            return {
                'city': city_name,
                'error': f"Failed to fetch weather data: {str(e)}",
                'source': 'weather_api_error'
            }
    
    def get_coldest_cities_india_simple(self) -> Dict[str, Any]:
        """Get coldest cities in India"""
        indian_cities = [
            'Manali', 'Leh', 'Srinagar', 'Gangtok', 'Darjeeling',
            'Dalhousie', 'Shimla', 'Kufri', 'Kullu', 'Nainital'
        ]
        
        cities_data = []
        for city in indian_cities:
            weather_data = self.get_real_time_weather_simple(city)
            if 'error' not in weather_data:
                cities_data.append(weather_data)
        
        # Sort by temperature (lowest first)
        cities_data.sort(key=lambda x: float(x['temperature']['current'].replace('°C', '')) if x['temperature']['current'] != 'N/A' else 999)
        
        return {
            'coldest_cities_india': cities_data[:10],
            'total_cities_checked': len(indian_cities),
            'timestamp': datetime.now().isoformat(),
            'source': 'real_time_weather_api'
        }
    
    def generate_geo_answer(self, query: str, include_details: bool = False, 
                           include_real_time_weather: bool = False, city_name: str = None) -> Dict[str, Any]:
        """Generate answer for geo-weather queries"""
        try:
            # Extract city name from query if not provided
            if include_real_time_weather and not city_name:
                city_match = re.search(r'\b(?:weather|temperature|climate)\s+(?:in|of|at)\s+(\w+)', query, re.IGNORECASE)
                if city_match:
                    city_name = city_match.group(1)
            
            # Get real-time weather if requested
            real_time_weather = None
            if include_real_time_weather and city_name:
                print(f"Fetching real-time weather data for {city_name}...")
                real_time_weather = self.get_real_time_weather_with_web_search(city_name)
                print(f"Weather data added: {real_time_weather}")
            
            # Get coldest cities if query mentions it
            coldest_cities = None
            if 'coldest' in query.lower() and 'india' in query.lower():
                print("Fetching real-time coldest cities data...")
                coldest_cities = self.get_coldest_cities_india_simple()
                print(f"Coldest cities data added: {coldest_cities}")
            
            # Prepare system prompt
            system_prompt = """You are a helpful geographical and weather assistant. You can provide information about:
1. Countries, cities, and geographical features
2. Weather patterns and climate information
3. Real-time weather data when available
4. Coldest cities and temperature comparisons

Provide accurate, helpful information based on the user's query."""

            # Add real-time data to context if available
            context = ""
            if real_time_weather and 'error' not in real_time_weather:
                context += f"\nReal-time weather for {city_name}: {json.dumps(real_time_weather, indent=2)}\n"
            
            if coldest_cities:
                context += f"\nColdest cities in India: {json.dumps(coldest_cities, indent=2)}\n"

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt + context},
                    {"role": "user", "content": query}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Prepare details if requested
            details = None
            if include_details:
                details = {
                    "query_type": "weather" if any(word in query.lower() for word in ["weather", "temperature", "climate"]) else "geographical",
                    "requires_location": any(word in query.lower() for word in ["weather", "temperature", "city", "country"]),
                    "response_length": len(answer),
                    "model_tokens_used": response.usage.total_tokens if response.usage else 0
                }
            
            return {
                "answer": answer,
                "model_used": "gpt-4o-mini",
                "details": details,
                "real_time_weather": real_time_weather
            }
            
        except Exception as e:
            raise Exception(f"Error generating geo-weather answer: {str(e)}")

# ============================================================================
# PDF RAG API CLASS
# ============================================================================

class PDFRAGAPI:
    def __init__(self, pdf_file: str = "ilovepdf_merged.pdf"):
        self.pdf_file = pdf_file
        self.text_chunks = []
        self.chunk_embeddings = None
        self.index = None
        self.embedding_model = None
        
        # Load and process PDF
        self.load_pdf()
        self.setup_embeddings()
    
    def load_pdf(self):
        """Extract text from PDF file"""
        try:
            text_content = ""
            
            # Try using pdfplumber first (better for complex PDFs)
            try:
                with pdfplumber.open(self.pdf_file) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                print(f"✅ Extracted text using pdfplumber from {self.pdf_file}")
            except Exception as e:
                print(f"pdfplumber failed, trying PyPDF2: {e}")
                                # Fallback to PyPDF2
                import PyPDF2
                with open(self.pdf_file, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                print(f"✅ Extracted text using PyPDF2 from {self.pdf_file}")
            
            # Clean the text
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            self.text_chunks = text_splitter.split_text(text_content)
            print(f"✅ Created {len(self.text_chunks)} text chunks from PDF")
            
        except Exception as e:
            raise Exception(f"Error loading PDF: {str(e)}")
    
    def setup_embeddings(self):
        """Generate embeddings for text chunks"""
        try:
            # Use a lightweight sentence transformer model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Generate embeddings for each text chunk
            print("Generating embeddings for text chunks...")
            self.chunk_embeddings = self.embedding_model.encode(
                self.text_chunks, 
                show_progress_bar=True,
                batch_size=32
            )
            
            # Create FAISS index
            dimension = self.chunk_embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            self.index.add(self.chunk_embeddings.astype('float32'))
            
            print(f"✅ Setup embeddings with {len(self.text_chunks)} text chunks")
            
        except Exception as e:
            raise Exception(f"Error setting up embeddings: {str(e)}")
    
    def search_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant text chunks"""
        try:
            # Encode the query
            query_embedding = self.embedding_model.encode([query])
            
            # Search the index
            scores, indices = self.index.search(
                query_embedding.astype('float32'), 
                min(top_k, len(self.text_chunks))
            )
            
            # Return relevant chunks with scores
            relevant_chunks = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.text_chunks):
                    relevant_chunks.append({
                        "chunk_id": int(idx),
                        "content": self.text_chunks[idx],
                        "similarity_score": float(score),
                        "chunk_length": len(self.text_chunks[idx])
                    })
            
            return relevant_chunks
            
        except Exception as e:
            raise Exception(f"Error searching chunks: {str(e)}")
    
    def get_openai_client(self):
        """Get OpenAI client with API key"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=400, 
                detail="OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
            )
        return OpenAI(api_key=api_key)
    
    def generate_answer(self, query: str, relevant_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate answer using OpenAI based on relevant chunks"""
        try:
            client = self.get_openai_client()
            
            # Prepare context from relevant chunks
            context = "Based on the following information from the PDF document:\n\n"
            for i, chunk in enumerate(relevant_chunks, 1):
                context += f"Section {i}:\n{chunk['content']}\n\n"
            
            system_prompt = f"""You are a helpful assistant that answers questions based ONLY on the provided information from the PDF document. 

IMPORTANT RULES:
1. ONLY use the information provided in the context from the PDF
2. DO NOT use any external knowledge or information
3. If the question cannot be answered with the provided PDF content, say "I can only answer questions based on the information in the PDF document. The answer to your question is not found in the provided content."
4. Be specific and cite relevant sections when possible
5. If the information is not complete in the PDF, acknowledge the limitations

Context: {context}
Question: {query}

Please provide a detailed answer based only on the PDF information above."""

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
            
            return {
                "answer": answer,
                "model_used": "gpt-4o-mini",
                "relevant_chunks": relevant_chunks,
                "total_chunks_processed": len(relevant_chunks)
            }
            
        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "model_used": "gpt-4o-mini",
                "relevant_chunks": [],
                "total_chunks_processed": 0
            }

# ============================================================================
# PRODUCTS RAG API CLASS
# ============================================================================

class ProductsRAGAPI:
    def __init__(self, csv_file: str = "products-1000.csv"):
        self.csv_file = csv_file
        self.products_df = None
        self.product_embeddings = None
        self.index = None
        self.embedding_model = None
        
        # Load and process products
        self.load_data()
        self.setup_embeddings()
    
    def load_data(self):
        """Load the products CSV file"""
        try:
            self.products_df = pd.read_csv(self.csv_file)
            print(f"✅ Loaded {len(self.products_df)} products from {self.csv_file}")
        except Exception as e:
            raise Exception(f"Error loading CSV: {str(e)}")
    
    def setup_embeddings(self):
        """Generate embeddings for product descriptions"""
        try:
            # Use a lightweight sentence transformer model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create product descriptions for embedding
            product_texts = []
            for _, row in self.products_df.iterrows():
                description = f"Name: {row.get('Name', '')} Brand: {row.get('Brand', '')} Category: {row.get('Category', '')} Price: {row.get('Price', '')} Rating: {row.get('Rating', '')}"
                product_texts.append(description)
            
            # Generate embeddings
            print("Generating embeddings for products...")
            self.product_embeddings = self.embedding_model.encode(
                product_texts, 
                show_progress_bar=True,
                batch_size=32
            )
            
            # Create FAISS index
            dimension = self.product_embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            self.index.add(self.product_embeddings.astype('float32'))
            
            print(f"✅ Setup embeddings with {len(self.products_df)} products")
            
        except Exception as e:
            raise Exception(f"Error setting up embeddings: {str(e)}")
    
    def search_products(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant products"""
        try:
            # Encode the query
            query_embedding = self.embedding_model.encode([query])
            
            # Search the index
            scores, indices = self.index.search(
                query_embedding.astype('float32'), 
                min(top_k, len(self.products_df))
            )
            
            # Return relevant products with scores
            relevant_products = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.products_df):
                    product = self.products_df.iloc[idx].to_dict()
                    relevant_products.append({
                        "product_id": int(idx),
                        "similarity_score": float(score),
                        **product
                    })
            
            return relevant_products
            
        except Exception as e:
            raise Exception(f"Error searching products: {str(e)}")
    
    def get_openai_client(self):
        """Get OpenAI client with API key"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=400, 
                detail="OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
            )
        return OpenAI(api_key=api_key)
    
    def generate_answer(self, query: str, relevant_products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate answer using OpenAI based on relevant products"""
        try:
            client = self.get_openai_client()
            
            # Prepare context from relevant products
            context = "Based on the following product information from our database:\n\n"
            for i, product in enumerate(relevant_products, 1):
                context += f"Product {i}:\n"
                context += f"- Name: {product.get('Name', 'N/A')}\n"
                context += f"- Brand: {product.get('Brand', 'N/A')}\n"
                context += f"- Category: {product.get('Category', 'N/A')}\n"
                context += f"- Price: {product.get('Price', 'N/A')}\n"
                context += f"- Rating: {product.get('Rating', 'N/A')}\n"
                context += f"- Availability: {product.get('Availability', 'N/A')}\n\n"
            
            system_prompt = f"""You are a helpful product assistant that answers questions based ONLY on the provided product information from our database. 

IMPORTANT RULES:
1. ONLY use the product information provided in the context
2. DO NOT use any external knowledge or information
3. If the question cannot be answered with the provided products, say "I can only answer questions based on the products in our database. The answer to your question is not found in the provided content."
4. Be specific about product details when relevant
5. If the information is not complete, acknowledge the limitations

Context: {context}
Question: {query}

Please provide a detailed answer based only on the product information above."""

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
            
            return {
                "answer": answer,
                "model_used": "gpt-4o-mini",
                "relevant_products": relevant_products,
                "total_products_processed": len(relevant_products)
            }
            
        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "model_used": "gpt-4o-mini",
                "relevant_products": [],
                "total_products_processed": 0
            }

# ============================================================================
# INITIALIZE ALL APIs
# ============================================================================

geo_weather_api = GeoWeatherAPI()
pdf_rag_api = PDFRAGAPI()
products_rag_api = ProductsRAGAPI()
agentic_api = LLMAgenticAPI(geo_weather_api, pdf_rag_api, products_rag_api)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API description"""
    return {
        "message": "Unified AI Agent API",
        "description": "Combined API for Geo-Weather, PDF RAG, and Products RAG",
        "version": "1.0.0",
        "endpoints": {
            "/geo-weather": "POST - Geo-Weather queries with real-time data",
            "/pdf-rag": "POST - PDF document queries",
            "/products-rag": "POST - Product database queries",
            "/agent": "POST - Intelligent agentic queries (auto-routes to appropriate tool)",
            "/health": "GET - Health check for all services",
            "/stats": "GET - Statistics for all services"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for all services"""
    return {
        "status": "healthy",
        "services": {
            "geo_weather": True,
            "pdf_rag": {
                "pdf_loaded": len(pdf_rag_api.text_chunks) > 0,
                "chunks_count": len(pdf_rag_api.text_chunks),
                "embeddings_ready": pdf_rag_api.chunk_embeddings is not None
            },
            "products_rag": {
                "products_loaded": len(products_rag_api.products_df) > 0 if products_rag_api.products_df is not None else False,
                "products_count": len(products_rag_api.products_df) if products_rag_api.products_df is not None else 0,
                "embeddings_ready": products_rag_api.product_embeddings is not None
            }
        }
    }

@app.get("/stats")
async def get_stats():
    """Get statistics for all services"""
    return {
        "geo_weather": {
            "status": "ready"
        },
        "pdf_rag": {
            "pdf_file": pdf_rag_api.pdf_file,
            "total_chunks": len(pdf_rag_api.text_chunks),
            "total_characters": sum(len(chunk) for chunk in pdf_rag_api.text_chunks),
            "average_chunk_length": sum(len(chunk) for chunk in pdf_rag_api.text_chunks) / len(pdf_rag_api.text_chunks) if pdf_rag_api.text_chunks else 0,
            "embeddings_ready": pdf_rag_api.chunk_embeddings is not None,
            "embedding_dimension": pdf_rag_api.chunk_embeddings.shape[1] if pdf_rag_api.chunk_embeddings is not None else None
        },
        "products_rag": {
            "csv_file": products_rag_api.csv_file,
            "total_products": len(products_rag_api.products_df) if products_rag_api.products_df is not None else 0,
            "embeddings_ready": products_rag_api.product_embeddings is not None,
            "embedding_dimension": products_rag_api.product_embeddings.shape[1] if products_rag_api.product_embeddings is not None else None
        }
    }

# ============================================================================
# GEO WEATHER ENDPOINTS
# ============================================================================

@app.post("/geo-weather", response_model=GeoWeatherResponse)
async def geo_weather_query(request: GeoWeatherRequest):
    """Geo-Weather query endpoint"""
    try:
        result = geo_weather_api.generate_geo_answer(
            query=request.query,
            include_details=request.include_details,
            include_real_time_weather=request.include_real_time_weather,
            city_name=request.city_name
        )
        
        return GeoWeatherResponse(
            query=request.query,
            answer=result["answer"],
            model_used=result["model_used"],
            details=result.get("details"),
            real_time_weather=result.get("real_time_weather")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing geo-weather query: {str(e)}")

# ============================================================================
# PDF RAG ENDPOINTS
# ============================================================================

@app.post("/pdf-rag", response_model=PDFRAGResponse)
async def pdf_rag_query(request: PDFRAGRequest):
    """PDF RAG query endpoint"""
    try:
        # Search for relevant chunks
        relevant_chunks = pdf_rag_api.search_chunks(request.query, request.top_k)
        
        if not relevant_chunks:
            return PDFRAGResponse(
                query=request.query,
                answer="No relevant information found in the PDF for your question.",
                relevant_chunks=[],
                model_used="gpt-4o-mini",
                total_chunks_processed=len(pdf_rag_api.text_chunks)
            )
        
        # Generate answer using OpenAI
        answer = pdf_rag_api.generate_answer(request.query, relevant_chunks)
        
        return PDFRAGResponse(
            query=request.query,
            answer=answer,
            relevant_chunks=relevant_chunks,
            model_used="gpt-4o-mini",
            total_chunks_processed=len(pdf_rag_api.text_chunks)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF RAG query: {str(e)}")

# ============================================================================
# PRODUCTS RAG ENDPOINTS
# ============================================================================

@app.post("/products-rag", response_model=ProductsRAGResponse)
async def products_rag_query(request: ProductsRAGRequest):
    """Products RAG query endpoint"""
    try:
        # Search for relevant products
        relevant_products = products_rag_api.search_products(request.query, request.top_k)
        
        if not relevant_products:
            return ProductsRAGResponse(
                query=request.query,
                answer="No relevant products found in the database for your question.",
                relevant_products=[],
                model_used="gpt-4o-mini",
                total_products_processed=len(products_rag_api.products_df) if products_rag_api.products_df is not None else 0
            )
        
        # Generate answer using OpenAI
        answer = products_rag_api.generate_answer(request.query, relevant_products)
        
        return ProductsRAGResponse(
            query=request.query,
            answer=answer,
            relevant_products=relevant_products,
            model_used="gpt-4o-mini",
            total_products_processed=len(products_rag_api.products_df) if products_rag_api.products_df is not None else 0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing products RAG query: {str(e)}")

# ============================================================================
# AGENTIC API ENDPOINTS
# ============================================================================

@app.post("/agent", response_model=AgenticResponse)
async def agentic_query(request: AgenticRequest):
    """Agentic query endpoint that intelligently routes to appropriate tools"""
    try:
        # Use multi-step processing for complex queries
        result = agentic_api.process_query(request.query)
        
        return AgenticResponse(
            query=result["query"],
            answer=result["answer"],
            tool_used=result["tool_used"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            model_used=result["model_used"],
            raw_response=result["raw_response"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing agentic query: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 