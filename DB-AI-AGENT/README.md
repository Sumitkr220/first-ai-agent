# DB-AI-AGENT 🤖

An AI-powered database assistant that allows users to ask natural language questions and get curated outputs from MongoDB, similar to ChatGPT.

## 🚀 Features

- **Natural Language Queries**: Ask questions in plain English
- **MongoDB Integration**: Direct connection to MongoDB databases
- **AI-Powered Analysis**: Uses OpenAI GPT-4 for query understanding
- **REST API**: Full REST API with FastAPI
- **Real-time Processing**: Instant query analysis and execution
- **Schema Understanding**: AI understands database structure automatically

## 📋 Prerequisites

- Python 3.8+
- MongoDB Atlas account
- OpenAI API key
- Virtual environment (recommended)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd DB-AI-AGENT
```

### 2. Setup Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory:
```env
# MongoDB Configuration
MONGODB_URI=your_mongodb_connection_string
MONGODB_DATABASE=sample_supplies

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo-preview

# Application Configuration
APP_NAME=DB-AI-AGENT
DEBUG=True
LOG_LEVEL=INFO
```

## 🚀 Quick Start

### 1. Start the Server
```bash
python scripts/start_server.py
```

### 2. Test the API
```bash
python scripts/test_api.py
```

### 3. Access API Documentation
Open your browser and go to: http://localhost:8000/docs

## 📚 API Endpoints

### Health Check
```bash
GET /health
```

### Query Database
```bash
POST /api/v1/query
{
  "query": "How many purchaseMethod is Online",
  "session_id": "test_session"
}
```

### Analyze Query
```bash
POST /api/v1/analyze
{
  "query": "Find all sales from New York",
  "session_id": "test_session"
}
```

### Get Database Schema
```bash
GET /api/v1/schema?collection_name=sales&include_sample=true
```

## 🧪 Testing

### Run All Tests
```bash
python scripts/test_api.py
```

### Database Utilities
```bash
python scripts/database_utils.py
```

## 📁 Project Structure

```
DB-AI-AGENT/
├── app/                    # Main application code
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── main_simple.py     # FastAPI application
│   ├── agents/            # AI agents (LangGraph)
│   ├── database/          # Database connection & schemas
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic services
│   └── utils/             # Utility functions
├── scripts/               # Utility scripts
│   ├── setup.py          # Project setup
│   ├── start_server.py   # Server startup
│   ├── test_api.py       # API testing
│   └── database_utils.py # Database utilities
├── tests/                 # Test files
├── docs/                  # Documentation
├── logs/                  # Application logs
├── data/                  # Data files
├── config/                # Configuration files
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | Required |
| `MONGODB_DATABASE` | Database name | `sample_supplies` |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4-turbo-preview` |
| `APP_NAME` | Application name | `DB-AI-AGENT` |
| `DEBUG` | Debug mode | `True` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🤖 How It Works

1. **Query Analysis**: The AI analyzes natural language queries
2. **Schema Understanding**: AI understands database structure
3. **Query Generation**: Converts natural language to MongoDB queries
4. **Execution**: Executes queries against MongoDB
5. **Response Generation**: Creates human-readable responses

## 📊 Example Queries

### Count Queries
- "How many documents are in the sales collection"
- "How many purchaseMethod is Online"
- "Count all sales from New York"

### Find Queries
- "Show me all sales from Denver"
- "Find sales with laptops"
- "Get all online purchases"

### Aggregate Queries
- "Show me all unique purchaseMethod values"
- "What is the average price of items"
- "Group sales by store location"

## 🛠️ Development

### Adding New Features
1. Create feature branch
2. Add tests in `tests/`
3. Update documentation
4. Submit pull request

### Running Tests
```bash
# Run API tests
python scripts/test_api.py

# Run database tests
python scripts/database_utils.py
```

## 📝 Logs

Application logs are stored in the `logs/` directory:
- `app.log`: Application logs
- `error.log`: Error logs
- `access.log`: Access logs

## 🔒 Security

- Environment variables for sensitive data
- Input validation with Pydantic
- Error handling and logging
- CORS configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API docs at `/docs`

## 🎯 Roadmap

- [ ] Add more database types (PostgreSQL, MySQL)
- [ ] Implement query caching
- [ ] Add user authentication
- [ ] Create web interface
- [ ] Add query history
- [ ] Implement real-time notifications

---

**Made with ❤️ for AI-powered database interactions** 