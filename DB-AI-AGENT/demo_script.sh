#!/bin/bash

# 🎯 DB-AI-AGENT Query API Demo Script
# Run this during your presentation to show live examples

echo "🚀 Starting DB-AI-AGENT Query API Demo"
echo "======================================"
echo ""

# Check if server is running
echo "📡 Checking server status..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Server is running!"
else
    echo "❌ Server is not running. Please start it first:"
    echo "   python3 -m uvicorn app.main_simple:app --host 0.0.0.0 --port 8000 --reload"
    exit 1
fi

echo ""
echo "🎯 Demo 1: Simple Count Query"
echo "=============================="
echo "Query: 'How many documents are in the sales collection'"
echo ""

curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many documents are in the sales collection",
    "session_id": "demo_1"
  }' | jq '.'

echo ""
echo "⏳ Waiting 2 seconds..."
sleep 2

echo ""
echo "🎯 Demo 2: Filter Query"
echo "======================="
echo "Query: 'How many purchaseMethod is Online'"
echo ""

curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many purchaseMethod is Online",
    "session_id": "demo_2"
  }' | jq '.'

echo ""
echo "⏳ Waiting 2 seconds..."
sleep 2

echo ""
echo "🎯 Demo 3: Complex Aggregation"
echo "=============================="
echo "Query: 'Show me all unique purchaseMethod values'"
echo ""

curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me all unique purchaseMethod values",
    "session_id": "demo_3"
  }' | jq '.'

echo ""
echo "⏳ Waiting 2 seconds..."
sleep 2

echo ""
echo "🎯 Demo 4: Analyze API (for comparison)"
echo "======================================="
echo "Query: 'How many purchaseMethod is Online' (Analysis only)"
echo ""

curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many purchaseMethod is Online",
    "session_id": "demo_4"
  }' | jq '.'

echo ""
echo "🎉 Demo Complete!"
echo "================="
echo ""
echo "📊 Summary:"
echo "- Demo 1: Simple count query"
echo "- Demo 2: Filtered count query"
echo "- Demo 3: Complex aggregation"
echo "- Demo 4: Analyze API (no execution)"
echo ""
echo "💡 Key Points:"
echo "- Natural language → MongoDB queries"
echo "- Real-time AI processing"
echo "- Human-readable responses"
echo "- Comprehensive error handling" 