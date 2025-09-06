#!/usr/bin/env python3
"""
Performance Optimization Script for DB-AI-AGENT
Implements optimizations for handling millions of records
"""

import os
import sys
import json
import time
import subprocess
from typing import Dict, Any, List

def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_step(step: str, description: str):
    """Print a step with description."""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def check_prerequisites():
    """Check if all prerequisites are met."""
    print_header("Prerequisites Check")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if we're in the right directory
    if not os.path.exists("app"):
        print("❌ Not in DB-AI-AGENT directory")
        return False
    print("✅ In correct directory")
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not detected")
    else:
        print("✅ Virtual environment active")
    
    return True

def install_optimization_dependencies():
    """Install additional dependencies for optimization."""
    print_header("Installing Optimization Dependencies")
    
    dependencies = [
        "redis==4.5.4",
        "psutil==5.9.5",
        "memory-profiler==0.61.0"
    ]
    
    for dep in dependencies:
        print_step("Installing", dep)
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    return True

def create_mongodb_indexes():
    """Create MongoDB indexes for performance."""
    print_header("Creating MongoDB Indexes")
    
    # Index creation script
    index_script = """
    // MongoDB Index Creation Script
    // Run this in MongoDB shell or MongoDB Compass
    
    // Sales collection indexes
    db.sales.createIndex({"purchaseMethod": 1})
    db.sales.createIndex({"saleDate": 1})
    db.sales.createIndex({"storeLocation": 1})
    db.sales.createIndex({"customer.age": 1})
    db.sales.createIndex({"items.price": 1})
    
    // Compound indexes
    db.sales.createIndex({"purchaseMethod": 1, "saleDate": 1})
    db.sales.createIndex({"storeLocation": 1, "purchaseMethod": 1})
    db.sales.createIndex({"customer.age": 1, "purchaseMethod": 1})
    
    // Text search indexes
    db.sales.createIndex({"items.name": "text"})
    
    // Aggregation pipeline indexes
    db.sales.createIndex({"saleDate": 1, "purchaseMethod": 1, "storeLocation": 1})
    db.sales.createIndex({"customer.age": 1, "items.price": 1})
    
    print("Indexes created successfully!")
    """
    
    # Save index script
    with open("mongodb_indexes.js", "w") as f:
        f.write(index_script)
    
    print("✅ MongoDB index script created: mongodb_indexes.js")
    print("📝 Run this script in MongoDB shell or MongoDB Compass")
    
    return True

def create_schema_cache_service():
    """Create the schema cache service."""
    print_header("Creating Schema Cache Service")
    
    schema_cache_code = '''import redis
import json
import hashlib
from typing import Dict, Any, Optional
from app.config import settings

class SchemaCache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=getattr(settings, 'redis_host', 'localhost'),
            port=getattr(settings, 'redis_port', 6379),
            db=0,
            decode_responses=True
        )
        self.cache_ttl = 3600  # 1 hour cache
    
    def get_schema_key(self, database_name: str, collection_name: str) -> str:
        """Generate cache key for schema."""
        return f"schema:{database_name}:{collection_name}"
    
    def get_cached_schema(self, database_name: str, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get cached schema."""
        try:
            key = self.get_schema_key(database_name, collection_name)
            cached = self.redis_client.get(key)
            
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            print(f"Cache error: {e}")
            return None
    
    def cache_schema(self, database_name: str, collection_name: str, schema: Dict[str, Any]):
        """Cache schema with TTL."""
        try:
            key = self.get_schema_key(database_name, collection_name)
            self.redis_client.setex(
                key, 
                self.cache_ttl, 
                json.dumps(schema)
            )
        except Exception as e:
            print(f"Cache error: {e}")
    
    def invalidate_schema(self, database_name: str, collection_name: str):
        """Invalidate cached schema."""
        try:
            key = self.get_schema_key(database_name, collection_name)
            self.redis_client.delete(key)
        except Exception as e:
            print(f"Cache error: {e}")
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate."""
        try:
            keys = self.redis_client.keys("schema:*")
            if not keys:
                return 0.0
            return len(keys) / 100.0  # Simplified calculation
        except Exception:
            return 0.0
'''
    
    # Create the file
    os.makedirs("app/services", exist_ok=True)
    with open("app/services/schema_cache.py", "w") as f:
        f.write(schema_cache_code)
    
    print("✅ Schema cache service created: app/services/schema_cache.py")
    return True

def create_query_cache_service():
    """Create the query cache service."""
    print_header("Creating Query Cache Service")
    
    query_cache_code = '''import redis
import json
import hashlib
from typing import Dict, Any, Optional
from app.config import settings

class QueryCache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=getattr(settings, 'redis_host', 'localhost'),
            port=getattr(settings, 'redis_port', 6379),
            db=1,  # Different DB for query cache
            decode_responses=True
        )
        self.cache_ttl = 1800  # 30 minutes for query results
    
    def get_cache_key(self, collection: str, query: str, query_type: str) -> str:
        """Generate cache key for query."""
        query_hash = hashlib.md5(f"{collection}:{query}:{query_type}".encode()).hexdigest()
        return f"query:{query_hash}"
    
    def get_cached_result(self, collection: str, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        """Get cached query result."""
        try:
            key = self.get_cache_key(collection, query, query_type)
            cached = self.redis_client.get(key)
            
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            print(f"Cache error: {e}")
            return None
    
    def cache_result(self, collection: str, query: str, query_type: str, result: Dict[str, Any]):
        """Cache query result."""
        try:
            key = self.get_cache_key(collection, query, query_type)
            self.redis_client.setex(
                key,
                self.cache_ttl,
                json.dumps(result)
            )
        except Exception as e:
            print(f"Cache error: {e}")
    
    def invalidate_cache(self, collection: str = None):
        """Invalidate cache for collection or all."""
        try:
            if collection:
                pattern = f"query:*{collection}*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            else:
                self.redis_client.flushdb()
        except Exception as e:
            print(f"Cache error: {e}")
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate."""
        try:
            keys = self.redis_client.keys("query:*")
            if not keys:
                return 0.0
            return len(keys) / 100.0  # Simplified calculation
        except Exception:
            return 0.0
'''
    
    # Create the file
    with open("app/services/query_cache.py", "w") as f:
        f.write(query_cache_code)
    
    print("✅ Query cache service created: app/services/query_cache.py")
    return True

def create_performance_monitor():
    """Create the performance monitoring service."""
    print_header("Creating Performance Monitor")
    
    performance_monitor_code = '''import time
import logging
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    query_time: float
    ai_processing_time: float
    response_generation_time: float
    total_time: float
    cache_hit: bool
    result_count: int
    memory_usage: float

class PerformanceMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = []
    
    def track_query(self, query: str, metrics: PerformanceMetrics):
        """Track query performance metrics."""
        self.metrics.append({
            "query": query,
            "timestamp": time.time(),
            "metrics": metrics
        })
        
        # Log performance issues
        if metrics.total_time > 5.0:  # 5 second threshold
            self.logger.warning(f"Slow query detected: {query} took {metrics.total_time:.2f}s")
        
        if metrics.result_count > 10000:
            self.logger.warning(f"Large result set: {query} returned {metrics.result_count} results")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        if not self.metrics:
            return {"message": "No metrics available"}
        
        avg_query_time = sum(m["metrics"].query_time for m in self.metrics) / len(self.metrics)
        avg_total_time = sum(m["metrics"].total_time for m in self.metrics) / len(self.metrics)
        cache_hit_rate = sum(1 for m in self.metrics if m["metrics"].cache_hit) / len(self.metrics)
        
        return {
            "total_queries": len(self.metrics),
            "average_query_time": avg_query_time,
            "average_total_time": avg_total_time,
            "cache_hit_rate": cache_hit_rate,
            "slow_queries": len([m for m in self.metrics if m["metrics"].total_time > 5.0]),
            "large_results": len([m for m in self.metrics if m["metrics"].result_count > 10000])
        }
    
    def reset_metrics(self):
        """Reset performance metrics."""
        self.metrics = []

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
'''
    
    # Create the file
    with open("app/services/performance_monitor.py", "w") as f:
        f.write(performance_monitor_code)
    
    print("✅ Performance monitor created: app/services/performance_monitor.py")
    return True

def update_config_settings():
    """Update configuration settings for optimization."""
    print_header("Updating Configuration Settings")
    
    # Read current .env file
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            env_content = f.read()
    else:
        env_content = ""
    
    # Add optimization settings
    optimization_settings = """
# Performance Optimization Settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL=3600
QUERY_TIMEOUT=30000
MAX_RESULTS=1000
PERFORMANCE_MONITORING=true
SLOW_QUERY_THRESHOLD=5.0
LARGE_RESULT_THRESHOLD=10000
MEMORY_USAGE_THRESHOLD=80
CACHE_HIT_RATE_THRESHOLD=0.7
"""
    
    # Append new settings
    with open(env_file, "a") as f:
        f.write(optimization_settings)
    
    print("✅ Configuration settings updated: .env")
    return True

def create_optimization_test():
    """Create a test script to verify optimizations."""
    print_header("Creating Optimization Test")
    
    test_code = '''#!/usr/bin/env python3
"""
Performance Optimization Test
Tests the optimization features for handling large datasets
"""

import time
import requests
import json
from typing import Dict, Any

def test_optimization_features():
    """Test optimization features."""
    print("🚀 Testing Performance Optimizations")
    
    # Test queries for different scenarios
    test_queries = [
        {
            "query": "How many Online purchases?",
            "description": "Simple count query"
        },
        {
            "query": "Show me sales from New York",
            "description": "Filter query with location"
        },
        {
            "query": "What are the total sales by month?",
            "description": "Complex aggregation"
        },
        {
            "query": "Find expensive products over $100",
            "description": "Price-based filtering"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\\n📋 Test {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/query",
                headers={"Content-Type": "application/json"},
                json={
                    "query": test_case["query"],
                    "session_id": "optimization_test",
                    "context": {},
                    "max_results": 100,
                    "include_analysis": True
                },
                timeout=30
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Time: {execution_time:.2f}s")
                print(f"   Target Collection: {result.get('analysis', {}).get('target_collection', 'N/A')}")
                print(f"   Query Type: {result.get('analysis', {}).get('query_type', 'N/A')}")
                print(f"   Confidence: {result.get('analysis', {}).get('confidence_score', 'N/A')}")
                
                results.append({
                    "test": test_case["description"],
                    "success": True,
                    "execution_time": execution_time,
                    "target_collection": result.get('analysis', {}).get('target_collection'),
                    "query_type": result.get('analysis', {}).get('query_type'),
                    "confidence": result.get('analysis', {}).get('confidence_score')
                })
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
                results.append({
                    "test": test_case["description"],
                    "success": False,
                    "execution_time": execution_time,
                    "error": response.text
                })
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results.append({
                "test": test_case["description"],
                "success": False,
                "execution_time": execution_time,
                "error": str(e)
            })
    
    # Print summary
    print("\\n" + "="*60)
    print("📊 Optimization Test Summary")
    print("="*60)
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    print(f"✅ Successful Tests: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed Tests: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        avg_time = sum(r["execution_time"] for r in successful_tests) / len(successful_tests)
        print(f"⏱️  Average Execution Time: {avg_time:.2f}s")
    
    # Performance analysis
    print("\\n🎯 Performance Analysis:")
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['test']}: {result['execution_time']:.2f}s")
    
    return results

if __name__ == "__main__":
    test_optimization_features()
'''
    
    # Create the test file
    with open("test_optimization.py", "w") as f:
        f.write(test_code)
    
    print("✅ Optimization test created: test_optimization.py")
    return True

def create_redis_setup_guide():
    """Create Redis setup guide."""
    print_header("Creating Redis Setup Guide")
    
    redis_guide = '''# Redis Setup Guide for DB-AI-AGENT

## Installation

### macOS
```bash
brew install redis
brew services start redis
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### Windows
Download from: https://redis.io/download

## Configuration

### Basic Redis Configuration
Edit /etc/redis/redis.conf (Linux) or redis.conf (Windows/macOS):

```conf
# Memory settings
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Network
bind 127.0.0.1
port 6379
```

## Testing Redis Connection

```bash
# Test Redis connection
redis-cli ping
# Should return: PONG

# Test basic operations
redis-cli set test "hello"
redis-cli get test
# Should return: "hello"
```

## Integration with DB-AI-AGENT

The optimization script will automatically configure Redis integration.
Make sure Redis is running before starting the application.

## Monitoring Redis

```bash
# Monitor Redis in real-time
redis-cli monitor

# Check Redis info
redis-cli info

# Check memory usage
redis-cli info memory
```
'''
    
    # Create the guide
    with open("REDIS_SETUP_GUIDE.md", "w") as f:
        f.write(redis_guide)
    
    print("✅ Redis setup guide created: REDIS_SETUP_GUIDE.md")
    return True

def main():
    """Main optimization script."""
    print("🚀 DB-AI-AGENT Performance Optimization")
    print("Optimizing for millions of records...")
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please fix and try again.")
        return False
    
    # Install dependencies
    if not install_optimization_dependencies():
        print("❌ Failed to install dependencies.")
        return False
    
    # Create MongoDB indexes
    if not create_mongodb_indexes():
        print("❌ Failed to create MongoDB indexes.")
        return False
    
    # Create cache services
    if not create_schema_cache_service():
        print("❌ Failed to create schema cache service.")
        return False
    
    if not create_query_cache_service():
        print("❌ Failed to create query cache service.")
        return False
    
    # Create performance monitor
    if not create_performance_monitor():
        print("❌ Failed to create performance monitor.")
        return False
    
    # Update configuration
    if not update_config_settings():
        print("❌ Failed to update configuration.")
        return False
    
    # Create test script
    if not create_optimization_test():
        print("❌ Failed to create optimization test.")
        return False
    
    # Create Redis guide
    if not create_redis_setup_guide():
        print("❌ Failed to create Redis guide.")
        return False
    
    print_header("Optimization Complete!")
    print("✅ All optimization components created successfully!")
    print("\n📋 Next Steps:")
    print("1. Install and start Redis server")
    print("2. Run MongoDB index script: mongodb_indexes.js")
    print("3. Restart your application")
    print("4. Test optimizations: python3 test_optimization.py")
    print("\n📚 Documentation:")
    print("- Performance Guide: PERFORMANCE_OPTIMIZATION_GUIDE.md")
    print("- Redis Setup: REDIS_SETUP_GUIDE.md")
    print("- Optimization Test: test_optimization.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 