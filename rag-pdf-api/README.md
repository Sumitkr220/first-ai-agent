# PDF RAG API

A FastAPI-based Retrieval-Augmented Generation (RAG) system that answers questions based on PDF document content using OpenAI.

## 🚀 Features

- **PDF Text Extraction**: Extracts text from PDF files using multiple libraries (pdfplumber, PyPDF2)
- **Text Chunking**: Splits PDF content into manageable chunks for better processing
- **Semantic Search**: Uses sentence transformers and FAISS for efficient similarity search
- **OpenAI Integration**: Generates contextual answers based on PDF content only
- **RESTful API**: Easy-to-use endpoints for querying PDF content
- **Real-time Processing**: No pre-processing required, processes PDF on startup

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- PDF file to process

## 🛠️ Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd rag-pdf-api
   ```

2. **Activate virtual environment**
   ```bash
   source ../venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   echo "OPENAI_API_KEY=your_api_key_here" > ../.env
   ```

5. **Ensure PDF file is present**
   ```bash
   # The PDF file should be named: ilovepdf_merged.pdf
   ls ilovepdf_merged.pdf
   ```

## 🚀 Quick Start

### Option 1: Using the startup script
```bash
chmod +x start_pdf_rag.sh
./start_pdf_rag.sh
```

### Option 2: Manual startup
```bash
source ../venv/bin/activate
python main.py
```

The API will be available at:
- **API**: http://localhost:8002
- **Documentation**: http://localhost:8002/docs
- **Health Check**: http://localhost:8002/health

## 📚 API Endpoints

### 1. Root Endpoint
```http
GET /
```
Returns API description and available endpoints.

### 2. Health Check
```http
GET /health
```
Returns the health status of the API and PDF processing status.

### 3. PDF Statistics
```http
GET /pdf/stats
```
Returns statistics about the loaded PDF (chunks, characters, etc.).

### 4. Query PDF
```http
POST /query
```
**Request Body:**
```json
{
  "query": "What is the main topic of this document?",
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "What is the main topic of this document?",
  "answer": "Based on the PDF content...",
  "relevant_chunks": [
    {
      "chunk_id": 0,
      "content": "PDF text chunk...",
      "similarity_score": 0.85,
      "chunk_length": 1000
    }
  ],
  "model_used": "gpt-4o-mini",
  "total_chunks_processed": 150
}
```

## 🧪 Testing

Run the test script to verify the API functionality:

```bash
python test_pdf_rag.py
```

This will test:
- Health endpoint
- PDF statistics
- Various sample queries

## 📖 How It Works

1. **PDF Processing**: 
   - Extracts text from PDF using pdfplumber (with PyPDF2 fallback)
   - Cleans and normalizes the text
   - Splits into chunks using RecursiveCharacterTextSplitter

2. **Embedding Generation**:
   - Uses sentence-transformers (all-MiniLM-L6-v2) to create embeddings
   - Builds FAISS index for fast similarity search

3. **Query Processing**:
   - Encodes user query using the same embedding model
   - Searches for most similar chunks using FAISS
   - Sends relevant chunks to OpenAI with strict instructions

4. **Answer Generation**:
   - OpenAI generates answers based ONLY on provided PDF chunks
   - Ensures no external knowledge is used
   - Returns contextual, PDF-based responses

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key

### PDF Processing Settings
- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Embedding Model**: all-MiniLM-L6-v2
- **OpenAI Model**: gpt-4o-mini

### API Settings
- **Port**: 8002
- **Host**: 0.0.0.0

## 📊 Performance

- **Text Extraction**: Supports complex PDF layouts
- **Embedding Generation**: Batch processing with progress bars
- **Search**: Fast similarity search using FAISS
- **Response Time**: Typically 2-5 seconds per query

## 🔒 Security

- API key stored in environment variables
- No PDF content stored permanently
- All processing done in memory
- No external data sources used in responses

## 🐛 Troubleshooting

### Common Issues

1. **PDF not loading**:
   - Ensure PDF file exists and is readable
   - Check file permissions

2. **OpenAI API errors**:
   - Verify API key is set correctly
   - Check API quota and billing

3. **Memory issues**:
   - Large PDFs may require more RAM
   - Consider reducing chunk size

4. **Port conflicts**:
   - Change port in main.py if 8002 is in use

## 📝 Example Usage

### Using curl
```bash
# Health check
curl http://localhost:8002/health

# Query the PDF
curl -X POST http://localhost:8002/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main findings?", "top_k": 3}'
```

### Using Python
```python
import requests

response = requests.post("http://localhost:8002/query", json={
    "query": "What is the methodology used?",
    "top_k": 5
})

print(response.json()["answer"])
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is for educational and research purposes. 