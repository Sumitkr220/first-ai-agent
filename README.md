# Country Information API

A comprehensive FastAPI application that provides detailed information about countries, cities, coordinates, weather, and more using OpenAI's GPT-4o-mini model.

## 🌟 Features

This API now supports a wide range of country-related queries through a single endpoint:

- **Country Counts**: Total number of countries, regions, territories
- **Cities**: Major cities, capitals, population, landmarks
- **Coordinates**: Latitude and longitude of cities, countries, landmarks
- **Weather**: Climate information, weather patterns, seasons
- **Geography**: Land area, borders, natural features
- **Demographics**: Population, languages, religions
- **Economy**: GDP, major industries, currency
- **Culture**: Traditions, food, festivals, history

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. **Clone and setup virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up your OpenAI API key:**
```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

4. **Run the application:**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Single Endpoint: `/first-ai-agent`

**Method**: `POST`

**Request Body**:
```json
{
  "query": "Your question here",
  "include_details": true
}
```

**Response**:
```json
{
  "query": "Your question",
  "answer": "AI-generated response",
  "model_used": "gpt-4o-mini-2024-07-18",
  "details": {
    "query_type": "cities|coordinates|weather|capital|general",
    "requires_location": true|false,
    "response_length": 1234,
    "model_tokens_used": 567
  }
}
```

## 🎯 Example Queries

Here are some examples of what you can ask:

### Country Information
```bash
curl -X POST http://localhost:8000/first-ai-agent \
  -H "Content-Type: application/json" \
  -d '{"query": "How many countries are there in the world?"}'
```

### City Lists
```bash
curl -X POST http://localhost:8000/first-ai-agent \
  -H "Content-Type: application/json" \
  -d '{"query": "List the top 5 cities in France"}'
```

### Coordinates
```bash
curl -X POST http://localhost:8000/first-ai-agent \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the coordinates of Tokyo, Japan?"}'
```

### Weather Information
```bash
curl -X POST http://localhost:8000/first-ai-agent \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather like in London, UK?"}'
```

### Capital Cities
```bash
curl -X POST http://localhost:8000/first-ai-agent \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of Brazil?"}'
```

### Regional Information
```bash
curl -X POST http://localhost:8000/first-ai-agent \
  -H "Content-Type: application/json" \
  -d '{"query": "List all countries in Europe"}'
```

### Demographics
```bash
curl -X POST http://localhost:8000/first-ai-agent \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about the population of India"}'
```

## 🧪 Testing

Run the comprehensive test script to see all functionality:

```bash
python test_expanded_api.py
```

This will test various types of queries and demonstrate the API's capabilities.

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

### API Configuration

- **Model**: GPT-4o-mini
- **Max Tokens**: 1000
- **Temperature**: 0.7
- **Port**: 8000

## 📊 Response Details

The API automatically categorizes queries and provides metadata:

- **query_type**: Detects the type of query (cities, coordinates, weather, etc.)
- **requires_location**: Whether the query needs a specific location
- **response_length**: Character count of the response
- **model_tokens_used**: Token usage for billing/monitoring

## 🛠️ Error Handling

The API handles various error scenarios:

- **400**: Missing API key
- **402**: OpenAI quota exceeded
- **429**: Rate limit exceeded
- **500**: General API errors

## 🔒 Security

- API keys are stored in environment variables
- No sensitive data is logged
- Input validation through Pydantic models

## 📈 Performance

- Fast response times with GPT-4o-mini
- Efficient token usage
- Automatic query categorization
- Detailed usage metrics

## 🤝 Contributing

Feel free to extend the functionality by:

1. Adding new query types
2. Enhancing the system prompt
3. Adding more detailed response structures
4. Implementing caching for common queries

## 📝 License

This project is open source and available under the MIT License. 