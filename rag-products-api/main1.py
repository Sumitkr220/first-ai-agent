from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os
from openai import OpenAI
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import json
import re

load_dotenv()

app = FastAPI(
    title="RAG Products API",
    description="API that answers questions using only data from products-1000.csv file",
    version="1.0.0"
)

class ProductQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    include_details: Optional[bool] = True

class ProductQueryResponse(BaseModel):
    query: str
    answer: str
    model_used: str
    relevant_products: Optional[List[Dict[str, Any]]] = None
    details: Optional[Dict[str, Any]] = None
    
    model_config = {
        "protected_namespaces": ()
    }

class RAGProductsAPI:
    def __init__(self):
        self.csv_file = "products-1000.csv"
        self.products_df = None
        self.embedding_model = None
        self.index = None
        self.product_embeddings = None
        self.load_data()
        self.setup_embeddings()
    
    def load_data(self):
        """Load the products CSV file"""
        try:
            self.products_df = pd.read_csv(self.csv_file)
            print(f"✅ Loaded {len(self.products_df)} products from {self.csv_file}")
        except Exception as e:
            print(f"❌ Error loading CSV file: {e}")
            raise HTTPException(status_code=500, detail=f"Error loading products data: {e}")
    
    def setup_embeddings(self):
        """Setup sentence embeddings for product search"""
        try:
            # Use a lightweight sentence transformer model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create text representations for each product
            product_texts = []
            for _, row in self.products_df.iterrows():
                # Combine relevant fields into a searchable text
                product_text = f"Product: {row['Name']} | Brand: {row['Brand']} | Category: {row['Category']} | Description: {row['Description']} | Price: {row['Price']} {row['Currency']} | Stock: {row['Stock']} | Color: {row['Color']} | Size: {row['Size']} | Availability: {row['Availability']}"
                product_texts.append(product_text)
            
            # Generate embeddings
            self.product_embeddings = self.embedding_model.encode(product_texts, show_progress_bar=True)
            
            # Create FAISS index for similarity search
            dimension = self.product_embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            self.index.add(self.product_embeddings.astype('float32'))
            
            print(f"✅ Setup embeddings with {len(product_texts)} products")
            
        except Exception as e:
            print(f"❌ Error setting up embeddings: {e}")
            raise HTTPException(status_code=500, detail=f"Error setting up embeddings: {e}")
    
    def search_products(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant products using semantic similarity"""
        try:
            # Encode the query
            query_embedding = self.embedding_model.encode([query])
            
            # Search the index
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # Get the relevant products
            relevant_products = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.products_df):
                    product = self.products_df.iloc[idx].to_dict()
                    product['relevance_score'] = float(score)
                    relevant_products.append(product)
            
            return relevant_products
            
        except Exception as e:
            print(f"❌ Error searching products: {e}")
            return []
    
    def get_openai_client(self):
        """Get OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail="OPENAI_API_KEY environment variable not set")
        return OpenAI(api_key=api_key)
    
    def generate_answer(self, query: str, relevant_products: List[Dict[str, Any]]) -> str:
        """Generate answer using OpenAI based on relevant products"""
        try:
            client = self.get_openai_client()
            
            # Prepare context from relevant products
            context = "Based on the following product information from our database:\n\n"
            for i, product in enumerate(relevant_products, 1):
                context += f"Product {i}:\n"
                context += f"- Name: {product['Name']}\n"
                context += f"- Brand: {product['Brand']}\n"
                context += f"- Category: {product['Category']}\n"
                context += f"- Description: {product['Description']}\n"
                context += f"- Price: {product['Price']} {product['Currency']}\n"
                context += f"- Stock: {product['Stock']}\n"
                context += f"- Color: {product['Color']}\n"
                context += f"- Size: {product['Size']}\n"
                context += f"- Availability: {product['Availability']}\n"
                context += f"- Relevance Score: {product['relevance_score']:.3f}\n\n"
            
            system_prompt = f"""You are a helpful product assistant that answers questions based ONLY on the provided product information from our database. 

IMPORTANT RULES:
1. ONLY use the product information provided in the context
2. DO NOT use any external knowledge or information
3. If the question cannot be answered with the provided products, say "I can only answer questions based on the products in our database. The information you're looking for is not available in our current product catalog."
4. Be specific and mention product names, brands, prices, and other relevant details
5. If multiple products match the query, provide a comprehensive comparison
6. Always mention the relevance scores to show how well each product matches the query

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
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Error generating answer: {e}")
            return f"Error generating answer: {str(e)}"

# Initialize the RAG API
rag_api = RAGProductsAPI()

@app.get("/")
async def root():
    return {
        "message": "RAG Products API",
        "description": "API that answers questions using only data from products-1000.csv",
        "endpoints": {
            "/query": "POST - Query products using RAG",
            "/docs": "GET - API documentation"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "products_loaded": len(rag_api.products_df) if rag_api.products_df is not None else 0,
        "embeddings_ready": rag_api.index is not None
    }

@app.post("/query", response_model=ProductQueryResponse)
async def query_products(request: ProductQueryRequest):
    """Query products using RAG (Retrieval-Augmented Generation)"""
    try:
        # Search for relevant products
        relevant_products = rag_api.search_products(request.query, request.top_k)
        
        if not relevant_products:
            return ProductQueryResponse(
                query=request.query,
                answer="I couldn't find any relevant products in our database for your query. Please try rephrasing your question.",
                model_used="gpt-4o-mini",
                relevant_products=[],
                details={
                    "query_type": "no_results",
                    "products_found": 0,
                    "top_k_requested": request.top_k
                }
            )
        
        # Generate answer using OpenAI
        answer = rag_api.generate_answer(request.query, relevant_products)
        
        # Prepare response
        response_data = {
            "query": request.query,
            "answer": answer,
            "model_used": "gpt-4o-mini"
        }
        
        if request.include_details:
            response_data["details"] = {
                "query_type": "product_search",
                "products_found": len(relevant_products),
                "top_k_requested": request.top_k,
                "average_relevance_score": np.mean([p['relevance_score'] for p in relevant_products]),
                "categories_found": list(set(p['Category'] for p in relevant_products)),
                "price_range": {
                    "min": min(p['Price'] for p in relevant_products),
                    "max": max(p['Price'] for p in relevant_products)
                }
            }
        
        # Add relevant products if requested
        if request.include_details:
            response_data["relevant_products"] = relevant_products
        
        return ProductQueryResponse(**response_data)
        
    except Exception as e:
        error_msg = str(e)
        if "insufficient_quota" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(status_code=402, detail="OpenAI quota exceeded. Please check your billing and plan details.")
        elif "rate_limit" in error_msg.lower():
            raise HTTPException(status_code=429, detail="OpenAI rate limit exceeded. Please try again later.")
        else:
            raise HTTPException(status_code=500, detail=f"Error processing query: {error_msg}")

@app.get("/products/stats")
async def get_product_stats():
    """Get statistics about the products database"""
    try:
        df = rag_api.products_df
        
        stats = {
            "total_products": len(df),
            "categories": df['Category'].value_counts().to_dict(),
            "brands": df['Brand'].value_counts().head(10).to_dict(),
            "price_stats": {
                "min": float(df['Price'].min()),
                "max": float(df['Price'].max()),
                "mean": float(df['Price'].mean()),
                "median": float(df['Price'].median())
            },
            "availability": df['Availability'].value_counts().to_dict(),
            "currencies": df['Currency'].value_counts().to_dict()
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting product stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 