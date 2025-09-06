# 🚀 DB-AI-AGENT Quick Reference

## 📋 **System Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    DB-AI-AGENT                             │
├─────────────────────────────────────────────────────────────┤
│  Natural Language → AI Processing → MongoDB → Results      │
│                                                           │
│  🌐 FastAPI Server (Port 8000)                           │
│  🤖 OpenAI GPT-4 Turbo                                   │
│  🗄️  MongoDB Atlas (Cloud Database)                      │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 **Two Main APIs**

### **1. Query API** - Get Real Answers
```
User: "How many Online purchases?"
    ↓
AI: Converts to MongoDB query
    ↓
DB: Executes query → Returns 1585
    ↓
AI: "There have been 1,585 purchases made online"
    ↓
User: Gets actual data + answer
```

### **2. Analyze API** - Understand Intent
```
User: "How many Online purchases?"
    ↓
AI: Converts to MongoDB query
    ↓
AI: "This is a count query on sales collection"
    ↓
User: Gets query understanding (no data)
```

## 📊 **Visual Comparison**

```
┌─────────────────────────────────────────────────────────────┐
│                    QUERY API                               │
│  🎯 Purpose: Get actual data                              │
│  ⏱️  Time: 5.01 seconds                                  │
│  💰 Cost: Higher (2 API calls)                           │
│  📊 Result: Real data + human answer                      │
│  🎯 Use: Production queries                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   ANALYZE API                             │
│  🎯 Purpose: Understand query intent                      │
│  ⏱️  Time: 2.54 seconds                                  │
│  💰 Cost: Lower (1 API call)                             │
│  📊 Result: Query analysis only                           │
│  🎯 Use: Query testing & validation                       │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ **How It Works**

### **Step 1: User Input**
```
User asks: "How many purchaseMethod is Online"
```

### **Step 2: AI Processing**
```
OpenAI GPT-4 converts to:
{
  "target_collection": "sales",
  "query_type": "count", 
  "processed_query": "{\"purchaseMethod\": \"Online\"}"
}
```

### **Step 3: Database Query**
```
MongoDB executes:
db.sales.countDocuments({"purchaseMethod": "Online"})
Returns: 1585
```

### **Step 4: AI Response**
```
OpenAI generates:
"There have been 1,585 purchases made online in the data available."
```

### **Step 5: Final Output**
```
User receives:
✅ Actual count: 1585
✅ Human answer: "1,585 purchases made online"
✅ Query analysis: What was understood
✅ Execution time: 5.01 seconds
```

## 🎯 **Key Components**

| Component | File | Purpose |
|-----------|------|---------|
| **FastAPI Server** | `app/main_simple.py` | Handles HTTP requests |
| **AI Service** | `app/services/ai_service.py` | Converts language to queries |
| **Database Service** | `app/services/db_service.py` | Executes MongoDB queries |
| **MongoDB Connection** | `app/database/connection.py` | Manages database connection |
| **Configuration** | `app/config.py` | Settings & environment variables |

## 📈 **API Endpoints**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/query` | POST | Execute queries & get results |
| `/api/v1/analyze` | POST | Analyze queries without execution |
| `/api/v1/schema` | GET | Get database structure |
| `/health` | GET | Check server status |
| `/docs` | GET | Interactive API documentation |

## 🔧 **Quick Test Commands**

### **Test Query API:**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many documents are in sales", "session_id": "test"}'
```

### **Test Analyze API:**
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "How many documents are in sales", "session_id": "test"}'
```

### **Check Health:**
```bash
curl http://localhost:8000/health
```

## 🎯 **Use Cases**

### **Use Query API when you want:**
- ✅ Actual data counts
- ✅ Real database results
- ✅ Human-readable answers
- ✅ Production queries

### **Use Analyze API when you want:**
- ✅ Understand query intent
- ✅ Validate queries before running
- ✅ Faster response times
- ✅ Query testing

## 🚀 **Start the Server**
```bash
# Option 1: Using the script
python3 scripts/start_server.py

# Option 2: Direct command
python3 -m uvicorn app.main_simple:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 **Database Info**
- **Database**: `sample_supplies`
- **Collection**: `sales`
- **Documents**: 5,000
- **Fields**: `purchaseMethod`, `customer`, `items`, `saleDate`, etc.

This quick reference shows you everything you need to understand how your DB-AI-AGENT works! 🎯 