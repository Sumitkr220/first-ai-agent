# 🎯 **How AI Determines Target Collection - Detailed Explanation**

## 📋 **The Process Flow**

### **Step 1: Database Schema Collection**
When a query comes in, the system first gathers all available collections and their schemas:

```python
# app/services/db_service.py - get_database_info()
def get_database_info(self) -> Dict[str, Any]:
    collections = self.get_all_collections()  # ["sales", "products", "customers"]
    schemas = {}
    
    for collection_name in collections:
        schema = self.get_collection_schema(collection_name)
        schemas[collection_name] = schema.dict()
    
    return {
        "database_name": "sample_supplies",
        "collections": ["sales", "products", "customers"],
        "schemas": {
            "sales": {
                "collection_name": "sales",
                "fields": ["_id", "purchaseMethod", "customer", "items", "saleDate"],
                "sample_document": {...},
                "document_count": 5000
            },
            "products": {
                "collection_name": "products", 
                "fields": ["_id", "name", "price", "category", "stock"],
                "sample_document": {...},
                "document_count": 1000
            },
            "customers": {
                "collection_name": "customers",
                "fields": ["_id", "name", "email", "location", "preferences"],
                "sample_document": {...},
                "document_count": 500
            }
        }
    }
```

### **Step 2: AI Prompt Creation**
The AI receives this complete database schema and a system prompt:

```python
# app/services/ai_service.py - analyze_query()
system_prompt = f"""
You are a database query analyzer. Your job is to:
1. Analyze the user's natural language query
2. Understand the database schema
3. Determine the appropriate collection to query
4. Generate the appropriate MongoDB query or aggregation pipeline
5. Provide confidence score and suggestions

Database Schema:
{database_schema}  # This contains ALL collections and their schemas

Return your analysis in the following JSON format:
{{
    "target_collection": "collection_name",
    "query_type": "find|aggregate|count",
    "processed_query": "the processed query or pipeline as a JSON string",
    "confidence_score": 0.0-1.0,
    "suggested_improvements": ["suggestion1", "suggestion2"]
}}
"""
```

### **Step 3: AI Analysis**
The AI analyzes the user query against the database schema:

**Example Query**: `"How many Online purchases?"`

**AI Reasoning Process**:
1. **Keyword Analysis**: "purchases" → likely related to sales/transactions
2. **Field Matching**: "Online" → matches `purchaseMethod` field in sales collection
3. **Collection Selection**: Based on context, selects "sales" collection
4. **Query Generation**: Creates MongoDB query `{"purchaseMethod": "Online"}`

---

## 🔍 **Detailed AI Decision Process**

### **What the AI Sees**

When you ask `"How many Online purchases?"`, the AI receives:

```json
{
  "database_name": "sample_supplies",
  "collections": ["sales", "products", "customers"],
  "schemas": {
    "sales": {
      "collection_name": "sales",
      "fields": ["_id", "purchaseMethod", "customer", "items", "saleDate", "storeLocation"],
      "sample_document": {
        "_id": "ObjectId(...)",
        "purchaseMethod": "Online",
        "customer": {"age": 25, "email": "...", "gender": "F", "satisfaction": 4},
        "items": [{"name": "Laptop", "price": "Decimal128('999.99')", "quantity": 1, "tags": ["electronics"]}],
        "saleDate": "2024-01-15T10:30:00Z",
        "storeLocation": "New York"
      },
      "document_count": 5000
    },
    "products": {
      "collection_name": "products",
      "fields": ["_id", "name", "price", "category", "stock"],
      "sample_document": {...},
      "document_count": 1000
    },
    "customers": {
      "collection_name": "customers", 
      "fields": ["_id", "name", "email", "location", "preferences"],
      "sample_document": {...},
      "document_count": 500
    }
  }
}
```

### **AI Decision Logic**

The AI uses these factors to determine the target collection:

#### **1. Keyword Matching**
- **"purchases"** → Related to buying/selling → `sales` collection
- **"Online"** → Matches `purchaseMethod` field in `sales` collection
- **"How many"** → Indicates a count operation

#### **2. Field Analysis**
- **sales.purchaseMethod**: Contains values like "Online", "In store", "Phone"
- **sales.customer**: Contains customer information
- **sales.items**: Contains purchased items
- **sales.saleDate**: Contains transaction dates

#### **3. Context Understanding**
- The query is about "purchases" and "Online" method
- This directly relates to sales transactions
- The `sales` collection has the `purchaseMethod` field

#### **4. Collection Selection**
Based on the analysis, the AI determines:
- **target_collection**: "sales" ✅
- **query_type**: "count" ✅
- **processed_query**: `{"purchaseMethod": "Online"}` ✅

---

## 🎯 **AI Response Example**

The AI returns this JSON response:

```json
{
  "target_collection": "sales",
  "query_type": "count", 
  "processed_query": "{\"purchaseMethod\": \"Online\"}",
  "confidence_score": 0.95,
  "suggested_improvements": [
    "Consider adding date range filters for more specific results",
    "Include store location analysis for geographic insights"
  ]
}
```

---

## 🔧 **How to See This in Action**

### **Test Different Queries**

#### **Query 1: Sales Collection**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many Online purchases?", "session_id": "test"}'
```
**AI Analysis**: 
- Keywords: "purchases", "Online"
- Field match: `purchaseMethod` in sales
- **Result**: `target_collection = "sales"`

#### **Query 2: Products Collection**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me products over $100", "session_id": "test"}'
```
**AI Analysis**:
- Keywords: "products", "price"
- Field match: `price` in products
- **Result**: `target_collection = "products"`

#### **Query 3: Customers Collection**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many customers are from New York?", "session_id": "test"}'
```
**AI Analysis**:
- Keywords: "customers", "location"
- Field match: `location` in customers
- **Result**: `target_collection = "customers"`

---

## 🚀 **Collection Selection Rules**

### **AI Decision Factors**

#### **1. Primary Keywords**
- **"purchases", "sales", "transactions"** → `sales` collection
- **"products", "items", "goods"** → `products` collection  
- **"customers", "users", "people"** → `customers` collection

#### **2. Field-Specific Keywords**
- **"purchaseMethod", "Online", "In store"** → `sales.purchaseMethod`
- **"price", "cost", "expensive"** → `products.price`
- **"location", "city", "address"** → `customers.location`

#### **3. Operation Keywords**
- **"How many", "count"** → `count` operation
- **"Show me", "find", "get"** → `find` operation
- **"group by", "aggregate"** → `aggregate` operation

---

## 🔍 **Debug Collection Selection**

### **To See What the AI Receives**

You can add logging to see the exact database schema:

```python
# In app/services/ai_service.py
def analyze_query(self, query: str, database_schema: Dict[str, Any]) -> QueryAnalysis:
    logger.info(f"Database schema sent to AI: {database_schema}")
    logger.info(f"User query: {query}")
    # ... rest of the method
```

### **To Test Collection Selection**

```python
# Test script to see AI decisions
def test_collection_selection():
    queries = [
        "How many Online purchases?",
        "Show me products over $100", 
        "How many customers are from New York?",
        "What are the total sales by month?",
        "Find expensive electronics"
    ]
    
    for query in queries:
        analysis = ai_service.analyze_query(query, database_schema)
        print(f"Query: {query}")
        print(f"Target Collection: {analysis.target_collection}")
        print(f"Query Type: {analysis.query_type}")
        print(f"Confidence: {analysis.confidence_score}")
        print("---")
```

---

## 🎯 **Summary**

### **How "sales" Gets Selected**

1. **User Query**: `"How many Online purchases?"`
2. **Schema Analysis**: AI sees all collections and their fields
3. **Keyword Matching**: "purchases" + "Online" → sales collection
4. **Field Matching**: `purchaseMethod` field exists in sales
5. **Context Understanding**: Query is about transactions
6. **AI Decision**: `target_collection = "sales"`
7. **Query Generation**: `{"purchaseMethod": "Online"}`

### **The Magic**
The AI doesn't have hardcoded rules. Instead, it:
- ✅ **Analyzes the complete database schema**
- ✅ **Understands natural language context**
- ✅ **Matches keywords to fields and collections**
- ✅ **Makes intelligent decisions based on the query**

**This is why the system is so flexible - it can automatically adapt to any database structure! 🚀** 