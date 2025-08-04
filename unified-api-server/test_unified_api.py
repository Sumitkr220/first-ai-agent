import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("✅ Health Check:")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_stats():
    """Test the stats endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/stats")
        print("\n✅ API Stats:")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Stats failed: {e}")
        return False

def test_geo_weather(query: str, include_details: bool = False, include_real_time_weather: bool = False, city_name: str = None):
    """Test Geo-Weather API"""
    try:
        payload = {
            "query": query,
            "include_details": include_details,
            "include_real_time_weather": include_real_time_weather,
            "city_name": city_name
        }
        
        print(f"\n🌍 Geo-Weather Query: {query}")
        if include_real_time_weather:
            print(f"📍 City: {city_name or 'Auto-detected'}")
        
        response = requests.post(f"{BASE_URL}/geo-weather", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Answer:")
            print(result["answer"])
            print(f"\n📊 Model: {result['model_used']}")
            
            if result.get("details"):
                print(f"📈 Details: {result['details']}")
            
            if result.get("real_time_weather"):
                print(f"🌤️ Real-time Weather: {result['real_time_weather']}")
            
            return True
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False

def test_pdf_rag(query: str, top_k: int = 5):
    """Test PDF RAG API"""
    try:
        payload = {
            "query": query,
            "top_k": top_k
        }
        
        print(f"\n📄 PDF RAG Query: {query}")
        print(f"📊 Top-k: {top_k}")
        
        response = requests.post(f"{BASE_URL}/pdf-rag", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Answer:")
            print(result["answer"])
            print(f"\n📈 Stats:")
            print(f"- Model used: {result['model_used']}")
            print(f"- Total chunks processed: {result['total_chunks_processed']}")
            print(f"- Relevant chunks found: {len(result['relevant_chunks'])}")
            
            if result['relevant_chunks']:
                print(f"\n🔍 Top relevant chunk:")
                top_chunk = result['relevant_chunks'][0]
                print(f"- Chunk ID: {top_chunk['chunk_id']}")
                print(f"- Similarity Score: {top_chunk['similarity_score']:.4f}")
                print(f"- Content preview: {top_chunk['content'][:200]}...")
            
            return True
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False

def test_products_rag(query: str, top_k: int = 5):
    """Test Products RAG API"""
    try:
        payload = {
            "query": query,
            "top_k": top_k
        }
        
        print(f"\n🛍️ Products RAG Query: {query}")
        print(f"📊 Top-k: {top_k}")
        
        response = requests.post(f"{BASE_URL}/products-rag", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Answer:")
            print(result["answer"])
            print(f"\n📈 Stats:")
            print(f"- Model used: {result['model_used']}")
            print(f"- Total products processed: {result['total_products_processed']}")
            print(f"- Relevant products found: {len(result['relevant_products'])}")
            
            if result['relevant_products']:
                print(f"\n🔍 Top relevant product:")
                top_product = result['relevant_products'][0]
                print(f"- Product ID: {top_product['product_id']}")
                print(f"- Similarity Score: {top_product['similarity_score']:.4f}")
                print(f"- Name: {top_product.get('Name', 'N/A')}")
                print(f"- Brand: {top_product.get('Brand', 'N/A')}")
                print(f"- Price: {top_product.get('Price', 'N/A')}")
            
            return True
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Unified LLM Learning API")
    print("=" * 60)
    
    # Test health
    if not test_health():
        print("❌ Health check failed. Make sure the server is running.")
        return
    
    # Test stats
    test_stats()
    
    # Test Geo-Weather API
    print("\n" + "=" * 60)
    print("🌍 Testing Geo-Weather API")
    print("=" * 60)
    
    geo_weather_queries = [
        ("What is the weather like in Mumbai?", False, True, "Mumbai"),
        ("What are the coldest cities in India?", False, False, None),
        ("Tell me about the climate of Delhi", False, True, "Delhi"),
        ("How many countries are there in the world?", False, False, None),
        ("What is the current temperature in Bangalore?", False, True, "Bangalore")
    ]
    
    for i, (query, include_details, include_real_time_weather, city_name) in enumerate(geo_weather_queries, 1):
        print(f"\n📝 Test {i}/{len(geo_weather_queries)}")
        test_geo_weather(query, include_details, include_real_time_weather, city_name)
        time.sleep(1)
    
    # Test PDF RAG API
    print("\n" + "=" * 60)
    print("📄 Testing PDF RAG API")
    print("=" * 60)
    
    pdf_queries = [
        "What is the invoice number and company name?",
        "What products are mentioned in the document?",
        "What are the tax details mentioned?",
        "What is the billing address?",
        "What are the limitations mentioned in the document?"
    ]
    
    for i, query in enumerate(pdf_queries, 1):
        print(f"\n📝 Test {i}/{len(pdf_queries)}")
        test_pdf_rag(query)
        time.sleep(1)
    
    # Test Products RAG API
    print("\n" + "=" * 60)
    print("🛍️ Testing Products RAG API")
    print("=" * 60)
    
    product_queries = [
        "What are the best rated products?",
        "Show me products under $50",
        "What electronics products are available?",
        "Find products from Apple brand",
        "What are the most expensive products?"
    ]
    
    for i, query in enumerate(product_queries, 1):
        print(f"\n📝 Test {i}/{len(product_queries)}")
        test_products_rag(query)
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("✅ Unified API Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main() 