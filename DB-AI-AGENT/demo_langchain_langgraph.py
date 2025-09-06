#!/usr/bin/env python3
"""
Demo Script: LangChain, LangGraph & NLP in DB-AI-AGENT
Showcases the practical implementation of LangChain and LangGraph
"""

import json
import time
import requests
from typing import Dict, Any

# Demo configuration
API_BASE_URL = "http://localhost:8000"
SESSION_ID = "langchain_demo"

def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def print_step(step: str, description: str):
    """Print a step with description."""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def demo_langchain_basics():
    """Demo 1: Basic LangChain Concepts"""
    print_header("LangChain Basics - Natural Language Processing")
    
    print_step("1", "Query Analysis (NLP)")
    print("User Query: 'How many Online purchases?'")
    print("LangChain Task: Intent Recognition + Entity Extraction")
    
    # Simulate LangChain processing
    analysis = {
        "intent": "count_query",
        "entities": {
            "purchase_method": "Online",
            "collection": "sales",
            "operation": "count"
        },
        "confidence": 0.95
    }
    print(f"AI Analysis: {json.dumps(analysis, indent=2)}")
    
    print_step("2", "Schema Understanding (LangChain Context)")
    print("LangChain analyzes database schema:")
    schema_example = {
        "sales": {
            "fields": ["_id", "purchaseMethod", "customer", "items", "saleDate"],
            "sample_document": {
                "purchaseMethod": "Online",
                "customer": {"age": 25, "gender": "F"},
                "items": [{"name": "Laptop", "price": "999.99"}]
            }
        }
    }
    print(f"Database Schema: {json.dumps(schema_example, indent=2)}")
    
    print_step("3", "Query Generation (NLP to MongoDB)")
    print("LangChain converts natural language to MongoDB query:")
    mongodb_query = {"purchaseMethod": "Online"}
    print(f"MongoDB Query: {json.dumps(mongodb_query, indent=2)}")

def demo_langgraph_workflow():
    """Demo 2: LangGraph Workflow Orchestration"""
    print_header("LangGraph Workflow - Multi-Step Processing")
    
    print_step("1", "State Graph Definition")
    print("LangGraph defines state schema:")
    state_schema = {
        "messages": "List[Any]",
        "query": "str",
        "database_schema": "Dict[str, Any]",
        "analysis": "Optional[QueryAnalysis]",
        "query_result": "Optional[QueryResult]",
        "response": "str",
        "error": "Optional[str]"
    }
    print(f"State Schema: {json.dumps(state_schema, indent=2)}")
    
    print_step("2", "Workflow Nodes")
    print("LangGraph workflow nodes:")
    nodes = {
        "analyze_query": "NLP processing + query analysis",
        "execute_query": "Database operations",
        "generate_response": "Natural language response generation",
        "handle_error": "Error recovery and user feedback"
    }
    for node, description in nodes.items():
        print(f"  • {node}: {description}")
    
    print_step("3", "Conditional Edges")
    print("LangGraph conditional routing:")
    edges = {
        "analyze_query → execute_query": "If analysis successful",
        "analyze_query → handle_error": "If analysis fails",
        "execute_query → generate_response": "If query successful",
        "execute_query → handle_error": "If query fails"
    }
    for edge, condition in edges.items():
        print(f"  • {edge}: {condition}")

def demo_real_api_calls():
    """Demo 3: Real API Calls Showing LangChain & LangGraph in Action"""
    print_header("Real API Calls - LangChain & LangGraph in Action")
    
    # Test queries to demonstrate different NLP capabilities
    test_queries = [
        {
            "query": "How many Online purchases?",
            "description": "Simple count query with entity extraction"
        },
        {
            "query": "Show me sales from New York",
            "description": "Filter query with location entity"
        },
        {
            "query": "What are the total sales by month?",
            "description": "Complex aggregation with temporal grouping"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print_step(f"{i}", f"Testing: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        
        try:
            # Make API call
            response = requests.post(
                f"{API_BASE_URL}/api/v1/query",
                headers={"Content-Type": "application/json"},
                json={
                    "query": test_case["query"],
                    "session_id": SESSION_ID,
                    "context": {},
                    "max_results": 10,
                    "include_analysis": True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"Target Collection: {result.get('analysis', {}).get('target_collection', 'N/A')}")
                print(f"Query Type: {result.get('analysis', {}).get('query_type', 'N/A')}")
                print(f"Confidence: {result.get('analysis', {}).get('confidence_score', 'N/A')}")
                print(f"Response: {result.get('response', 'N/A')[:100]}...")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        print()

def demo_nlp_techniques():
    """Demo 4: NLP Techniques Used"""
    print_header("NLP Techniques - Natural Language Understanding")
    
    print_step("1", "Intent Recognition")
    intents = {
        "How many Online purchases?": "count_query",
        "Show me expensive products": "find_query", 
        "What are the total sales by month?": "aggregate_query",
        "Analyze customer satisfaction": "analyze_query"
    }
    for query, intent in intents.items():
        print(f"  • '{query}' → {intent}")
    
    print_step("2", "Entity Extraction")
    entities = {
        "purchase_method": ["Online", "In store", "Phone"],
        "location": ["New York", "Los Angeles", "Chicago"],
        "price_range": ["expensive", "cheap", "over $100"],
        "time_period": ["this month", "last year", "by month"]
    }
    for entity_type, examples in entities.items():
        print(f"  • {entity_type}: {', '.join(examples)}")
    
    print_step("3", "Context Understanding")
    context_examples = [
        "Database schema awareness",
        "Collection field mapping", 
        "Data type understanding",
        "Relationship recognition"
    ]
    for example in context_examples:
        print(f"  • {example}")

def demo_langchain_components():
    """Demo 5: LangChain Components in Our Code"""
    print_header("LangChain Components - Code Implementation")
    
    print_step("1", "LangChain OpenAI Integration")
    langchain_code = '''
# app/services/ai_service.py
from langchain_openai import ChatOpenAI

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    '''
    print(langchain_code)
    
    print_step("2", "LangChain Core Messages")
    message_code = '''
# app/agents/db_agent.py
from langchain_core.messages import HumanMessage, AIMessage

messages = [
    HumanMessage(content="How many Online purchases?"),
    AIMessage(content="Query analyzed. Target collection: sales")
]
    '''
    print(message_code)
    
    print_step("3", "LangGraph State Management")
    langgraph_code = '''
# app/agents/db_agent.py
from langgraph.graph import StateGraph, END

workflow = StateGraph({
    "messages": List[Any],
    "query": str,
    "database_schema": Dict[str, Any],
    "analysis": Optional[QueryAnalysis],
    "query_result": Optional[QueryResult],
    "response": str,
    "error": Optional[str]
})
    '''
    print(langgraph_code)

def demo_advanced_features():
    """Demo 6: Advanced LangChain & LangGraph Features"""
    print_header("Advanced Features - Future Capabilities")
    
    print_step("1", "Multi-Agent Coordination")
    agents = {
        "Query Analyzer": "Understands user intent and entities",
        "Schema Expert": "Analyzes database structure",
        "Query Builder": "Generates optimized MongoDB queries",
        "Response Generator": "Creates natural language responses"
    }
    for agent, role in agents.items():
        print(f"  • {agent}: {role}")
    
    print_step("2", "Memory Management")
    memory_features = [
        "Conversation history persistence",
        "Context awareness across sessions",
        "Learning from user preferences",
        "Adaptive response generation"
    ]
    for feature in memory_features:
        print(f"  • {feature}")
    
    print_step("3", "Tool Integration")
    tools = [
        "External API calls",
        "Database operations",
        "File system access",
        "Web scraping capabilities"
    ]
    for tool in tools:
        print(f"  • {tool}")

def main():
    """Run all demos."""
    print("🚀 LangChain, LangGraph & NLP Demo")
    print("DB-AI-AGENT Project")
    print("="*60)
    
    try:
        # Check if server is running
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running!")
        else:
            print("⚠️  Server may not be running. Some demos may fail.")
    except:
        print("⚠️  Server not accessible. Running demos without API calls.")
    
    # Run all demos
    demos = [
        demo_langchain_basics,
        demo_langgraph_workflow,
        demo_nlp_techniques,
        demo_langchain_components,
        demo_advanced_features,
        demo_real_api_calls  # Run this last as it depends on server
    ]
    
    for demo in demos:
        try:
            demo()
            time.sleep(1)  # Brief pause between demos
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")
    
    print_header("Demo Complete!")
    print("🎉 All LangChain, LangGraph & NLP demos completed!")
    print("\nKey Takeaways:")
    print("  • LangChain provides modular LLM components")
    print("  • LangGraph enables complex workflow orchestration") 
    print("  • NLP enables natural language database queries")
    print("  • The combination creates powerful AI applications")

if __name__ == "__main__":
    main() 