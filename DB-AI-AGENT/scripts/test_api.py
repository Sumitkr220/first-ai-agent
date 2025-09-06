#!/usr/bin/env python3
"""
API testing script for DB-AI-AGENT
Tests all endpoints and functionality
"""

import requests
import json
import time
from typing import Dict, Any

class APITester:
    """API testing class"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = f"test_session_{int(time.time())}"
    
    def test_health(self) -> bool:
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_query(self, query: str) -> bool:
        """Test query endpoint"""
        try:
            payload = {
                "query": query,
                "session_id": self.session_id
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/query",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Query test passed: {query}")
                print(f"   Response: {data.get('response', 'No response')}")
                return True
            else:
                print(f"❌ Query test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Query test error: {e}")
            return False
    
    def test_analyze(self, query: str) -> bool:
        """Test analyze endpoint"""
        try:
            payload = {
                "query": query,
                "session_id": self.session_id
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/analyze",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"✅ Analyze test passed: {query}")
                return True
            else:
                print(f"❌ Analyze test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Analyze test error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 Running API tests...")
        
        tests = [
            ("Health Check", self.test_health),
            ("Query - Document Count", lambda: self.test_query("How many documents are in the sales collection")),
            ("Query - Purchase Method", lambda: self.test_query("How many purchaseMethod is Online")),
            ("Query - Unique Values", lambda: self.test_query("Show me all unique purchaseMethod values")),
            ("Analyze - Simple Query", lambda: self.test_analyze("Find all sales")),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 Testing: {test_name}")
            if test_func():
                passed += 1
        
        print(f"\n📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Check the logs above.")

def main():
    """Main function"""
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 