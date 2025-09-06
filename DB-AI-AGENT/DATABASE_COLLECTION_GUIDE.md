# 🗄️ **Database & Collection Selection Guide**

## 📋 **How Database and Collection Selection Works**

### **1. Database Selection (Fixed)**
The database is **configured once** and remains the same for all queries:

```python
# In app/config.py
mongodb_database: str = Field(default="sample_supplies", env="MONGODB_DATABASE")
```

**Current Setup:**
- **Database**: `sample_supplies` (configured in `.env` file)
- **Connection**: MongoDB Atlas cluster
- **Collections**: `sales`, `products`, `customers`, etc.

### **2. Collection Selection (AI-Driven)**
The AI automatically determines which collection to query based on the user's question:

```python
# AI analyzes the query and determines collection
analysis = ai_service.analyze_query(query, database_schema)
target_collection = analysis.target_collection  # e.g., "sales", "products"
```

---

## 🔍 **Step-by-Step Process**

### **Step 1: Database Connection**
```python
# app/database/connection.py
class DatabaseManager:
    def __init__(self):
        self.database = self.client[settings.mongodb_database]  # "sample_supplies"
```

### **Step 2: Schema Analysis**
```python
# app/services/db_service.py
def get_database_info(self) -> Dict[str, Any]:
    collections = self.get_all_collections()  # ["sales", "products", "customers"]
    schemas = {}
    for collection in collections:
        schemas[collection] = self.get_collection_schema(collection)
    return {"collections": collections, "schemas": schemas}
```

### **Step 3: AI Collection Selection**
```python
# app/services/ai_service.py
def analyze_query(self, query: str, database_schema: Dict[str, Any]) -> QueryAnalysis:
    system_prompt = f"""
    Database Schema:
    {database_schema}  # Contains all collections and their schemas
    
    Determine the appropriate collection to query based on the user's question.
    """
```

### **Step 4: Query Execution**
```python
# app/services/db_service.py
def execute_count_query(self, collection_name: str, query: Dict[str, Any]):
    collection = self.db_manager.get_collection(collection_name)  # Gets specific collection
    return collection.count_documents(query)
```

---

## 🎯 **Collection Selection Examples**

### **Example 1: Sales Collection**
```
User Query: "How many Online purchases?"
AI Analysis: 
- target_collection: "sales"
- query_type: "count"
- processed_query: {"purchaseMethod": "Online"}
```

### **Example 2: Products Collection**
```
User Query: "Show me all products with price > $100"
AI Analysis:
- target_collection: "products"
- query_type: "find"
- processed_query: {"price": {"$gt": 100}}
```

### **Example 3: Customers Collection**
```
User Query: "How many customers are from New York?"
AI Analysis:
- target_collection: "customers"
- query_type: "count"
- processed_query: {"location": "New York"}
```

---

## 🔧 **How to Handle Multiple Collections**

### **Current System (Single Database, Multiple Collections)**
```
Database: sample_supplies
├── Collection: sales
│   ├── Fields: purchaseMethod, customer, items, saleDate
│   └── Documents: 5,000
├── Collection: products
│   ├── Fields: name, price, category, stock
│   └── Documents: 1,000
└── Collection: customers
    ├── Fields: name, email, location, preferences
    └── Documents: 500
```

### **AI Collection Selection Logic**
The AI uses these factors to select the right collection:

1. **Keyword Matching**: "purchases" → `sales` collection
2. **Field Matching**: "price" → `products` collection
3. **Context Understanding**: "customers" → `customers` collection
4. **Schema Analysis**: Available fields in each collection

---

## 🚀 **How to Update Collection Selection**

### **Option 1: Environment Variable (Database Level)**
```bash
# .env file
MONGODB_DATABASE=your_new_database_name
```

### **Option 2: Multiple Database Support (Advanced)**
If you want to support multiple databases, you would need to modify the system:

#### **A. Update Configuration**
```python
# app/config.py
class Settings(BaseSettings):
    # Current: Single database
    mongodb_database: str = Field(default="sample_supplies", env="MONGODB_DATABASE")
    
    # Future: Multiple databases
    # mongodb_databases: Dict[str, str] = Field(default={}, env="MONGODB_DATABASES")
```

#### **B. Update Database Manager**
```python
# app/database/connection.py
class DatabaseManager:
    def __init__(self):
        self.databases = {}
        self._connect_all()
    
    def get_database(self, database_name: str) -> Database:
        """Get a specific database by name."""
        if database_name not in self.databases:
            self.databases[database_name] = self.client[database_name]
        return self.databases[database_name]
    
    def get_collection(self, database_name: str, collection_name: str):
        """Get a collection from a specific database."""
        db = self.get_database(database_name)
        return db[collection_name]
```

#### **C. Update AI Service**
```python
# app/services/ai_service.py
def analyze_query(self, query: str, all_databases_schema: Dict[str, Any]) -> QueryAnalysis:
    system_prompt = f"""
    You are a database query analyzer. Your job is to:
    1. Analyze the user's natural language query
    2. Understand the database schemas for ALL databases
    3. Determine the appropriate DATABASE and COLLECTION to query
    4. Generate the appropriate MongoDB query
    
    All Databases Schema:
    {all_databases_schema}
    
    Return your analysis in the following JSON format:
    {{
        "target_database": "database_name",
        "target_collection": "collection_name",
        "query_type": "find|aggregate|count",
        "processed_query": "the processed query as a JSON string",
        "confidence_score": 0.0-1.0
    }}
    """
```

#### **D. Update Database Service**
```python
# app/services/db_service.py
def execute_count_query(self, database_name: str, collection_name: str, query: Dict[str, Any]):
    collection = self.db_manager.get_collection(database_name, collection_name)
    return collection.count_documents(query)
```

---

## 📊 **Current vs. Future Architecture**

### **Current Architecture (Single Database)**
```
User Query → AI Analysis → Collection Selection → Query Execution
                ↓
        Database: sample_supplies
        Collections: sales, products, customers
```

### **Future Architecture (Multiple Databases)**
```
User Query → AI Analysis → Database + Collection Selection → Query Execution
                ↓
    Databases: 
    ├── sample_supplies (sales, products, customers)
    ├── user_data (profiles, preferences, history)
    └── analytics (reports, metrics, insights)
```

---

## 🎯 **Collection Selection Examples**

### **Current System Examples**

#### **Sales Collection Queries**
```bash
# Count total sales
curl -X POST http://localhost:8000/api/v1/query \
  -d '{"query": "How many sales are there?", "session_id": "test"}'
# AI selects: target_collection = "sales"

# Filter by purchase method
curl -X POST http://localhost:8000/api/v1/query \
  -d '{"query": "How many Online purchases?", "session_id": "test"}'
# AI selects: target_collection = "sales"
```

#### **Products Collection Queries**
```bash
# Find expensive products
curl -X POST http://localhost:8000/api/v1/query \
  -d '{"query": "Show me products over $100", "session_id": "test"}'
# AI selects: target_collection = "products"

# Count by category
curl -X POST http://localhost:8000/api/v1/query \
  -d '{"query": "How many electronics products?", "session_id": "test"}'
# AI selects: target_collection = "products"
```

---

## 🔧 **How to Add New Collections**

### **Step 1: Add Collection to MongoDB**
```javascript
// In MongoDB Atlas
use sample_supplies
db.createCollection("inventory")
db.inventory.insertMany([
  {item: "Laptop", quantity: 50, location: "Warehouse A"},
  {item: "Mouse", quantity: 200, location: "Warehouse B"}
])
```

### **Step 2: The System Automatically Detects It**
```python
# The system will automatically include the new collection
def get_database_info(self) -> Dict[str, Any]:
    collections = self.get_all_collections()  # Now includes "inventory"
    # AI will automatically consider "inventory" for relevant queries
```

### **Step 3: Test with New Collection**
```bash
# Query the new collection
curl -X POST http://localhost:8000/api/v1/query \
  -d '{"query": "How many laptops are in inventory?", "session_id": "test"}'
# AI should select: target_collection = "inventory"
```

---

## 🚨 **Troubleshooting Collection Selection**

### **Issue 1: AI Selects Wrong Collection**
**Solution**: Improve the AI prompt with better examples:
```python
system_prompt = f"""
Database Schema:
- sales: purchaseMethod, customer, items, saleDate
- products: name, price, category, stock
- customers: name, email, location, preferences

Examples:
- "purchases" or "sales" → sales collection
- "products" or "items" → products collection
- "customers" or "users" → customers collection
"""
```

### **Issue 2: Collection Not Found**
**Solution**: Check if collection exists:
```python
def get_collection(self, collection_name: str):
    """Get a collection with error handling."""
    try:
        return self.get_database()[collection_name]
    except Exception as e:
        logger.error(f"Collection {collection_name} not found: {e}")
        # Return default collection or raise error
        return self.get_database()["sales"]  # Default fallback
```

### **Issue 3: Multiple Collections with Similar Fields**
**Solution**: Use more specific queries:
```bash
# Instead of: "How many items?"
# Use: "How many sales items?" or "How many product items?"
```

---

## 📈 **Performance Considerations**

### **Collection Selection Performance**
- **AI Analysis**: ~2-3 seconds per query
- **Database Query**: ~0.001-0.1 seconds
- **Total Time**: ~5 seconds per request

### **Optimization Strategies**
1. **Cache Collection Schemas**: Store schema info in memory
2. **Pre-trained Collection Selection**: Use ML model for faster selection
3. **Query Templates**: Pre-define common query patterns

---

## 🎯 **Summary**

### **Current System**
- ✅ **Single Database**: `sample_supplies`
- ✅ **Multiple Collections**: `sales`, `products`, `customers`
- ✅ **AI-Driven Selection**: Automatically chooses collection
- ✅ **Dynamic Detection**: New collections automatically included

### **How It Works**
1. **Database**: Fixed to `sample_supplies` (configurable in `.env`)
2. **Collections**: Automatically detected from database
3. **Selection**: AI analyzes query and chooses appropriate collection
4. **Execution**: Query runs on selected collection

### **To Change Collections**
- **Add New Collection**: Just create it in MongoDB, system auto-detects
- **Change Database**: Update `MONGODB_DATABASE` in `.env`
- **Multiple Databases**: Requires code modifications (future enhancement)

**The system is designed to be flexible and automatically adapt to your database structure! 🚀** 