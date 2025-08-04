import os
import re
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from openai import OpenAI
from dotenv import load_dotenv
import PyPDF2
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

app = FastAPI(
    title="PDF RAG API",
    description="API that answers questions based on PDF content using RAG (Retrieval-Augmented Generation)",
    version="1.0.0"
)

class PDFQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class PDFQueryResponse(BaseModel):
    query: str
    answer: str
    relevant_chunks: List[Dict[str, Any]]
    model_used: str
    total_chunks_processed: int
    
    model_config = {"protected_namespaces": ()}

class RAGPDFAPI:
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
    
    def generate_answer(self, query: str, relevant_chunks: List[Dict[str, Any]]) -> str:
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

Context from PDF: {context}
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
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error generating answer: {str(e)}")

# Initialize the RAG API
rag_api = RAGPDFAPI()

@app.get("/")
async def root():
    """Root endpoint with API description"""
    return {
        "message": "PDF RAG API",
        "description": "Ask questions about the PDF document and get answers based on its content",
        "endpoints": {
            "/query": "POST - Ask questions about the PDF",
            "/health": "GET - Health check",
            "/pdf/stats": "GET - PDF statistics"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "pdf_loaded": len(rag_api.text_chunks) > 0,
        "chunks_count": len(rag_api.text_chunks),
        "embeddings_ready": rag_api.chunk_embeddings is not None
    }

@app.post("/query", response_model=PDFQueryResponse)
async def query_pdf(request: PDFQueryRequest):
    """Query the PDF document"""
    try:
        # Search for relevant chunks
        relevant_chunks = rag_api.search_chunks(request.query, request.top_k)
        
        if not relevant_chunks:
            return PDFQueryResponse(
                query=request.query,
                answer="No relevant information found in the PDF for your question.",
                relevant_chunks=[],
                model_used="gpt-4o-mini",
                total_chunks_processed=len(rag_api.text_chunks)
            )
        
        # Generate answer using OpenAI
        answer = rag_api.generate_answer(request.query, relevant_chunks)
        
        return PDFQueryResponse(
            query=request.query,
            answer=answer,
            relevant_chunks=relevant_chunks,
            model_used="gpt-4o-mini",
            total_chunks_processed=len(rag_api.text_chunks)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/pdf/stats")
async def get_pdf_stats():
    """Get statistics about the loaded PDF"""
    try:
        return {
            "pdf_file": rag_api.pdf_file,
            "total_chunks": len(rag_api.text_chunks),
            "total_characters": sum(len(chunk) for chunk in rag_api.text_chunks),
            "average_chunk_length": sum(len(chunk) for chunk in rag_api.text_chunks) / len(rag_api.text_chunks) if rag_api.text_chunks else 0,
            "embeddings_ready": rag_api.chunk_embeddings is not None,
            "embedding_dimension": rag_api.chunk_embeddings.shape[1] if rag_api.chunk_embeddings is not None else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting PDF stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 