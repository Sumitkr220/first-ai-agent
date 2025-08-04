import requests
import json
import time

BASE_URL = "http://localhost:8002"

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

def test_pdf_stats():
    """Test the PDF stats endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/pdf/stats")
        print("\n✅ PDF Stats:")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ PDF stats failed: {e}")
        return False

def test_pdf_query(query: str, top_k: int = 5):
    """Test a PDF query"""
    try:
        payload = {
            "query": query,
            "top_k": top_k
        }
        
        print(f"\n🔍 Query: {query}")
        print(f"📊 Top-k: {top_k}")
        
        response = requests.post(f"{BASE_URL}/query", json=payload)
        
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

def main():
    """Main test function"""
    print("🚀 Testing PDF RAG API")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("❌ Health check failed. Make sure the server is running.")
        return
    
    # Test PDF stats
    test_pdf_stats()
    
    # Test queries
    test_queries = [
        "What is the main topic of this document?",
        "What are the key points discussed?",
        "What are the main conclusions?",
        "What methodology is used?",
        "What are the findings?",
        "What are the recommendations?",
        "What is the scope of this document?",
        "What are the limitations mentioned?",
        "What are the future directions?",
        "What is the background information?"
    ]
    
    print("\n" + "=" * 50)
    print("🧪 Testing PDF Queries")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}/{len(test_queries)}")
        test_pdf_query(query)
        time.sleep(1)  # Small delay between requests
    
    print("\n" + "=" * 50)
    print("✅ PDF RAG API Testing Complete!")

if __name__ == "__main__":
    main() 