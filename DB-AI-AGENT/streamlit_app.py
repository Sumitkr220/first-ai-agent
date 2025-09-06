#!/usr/bin/env python3
"""
Streamlit UI for DB-AI-AGENT
Professional interface for natural language database querying and analysis
"""

import streamlit as st
import requests
import json
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
import sys

# Ensure project root is on path so `import app.*` works
PROJECT_ROOT = os.path.dirname(__file__)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

try:
    from app.services.trend_analysis import trend_analysis_service
except Exception:
    trend_analysis_service = None

# Configuration
API_BASE_URL = "http://localhost:8000"
SESSION_ID = "streamlit_session"

# Page configuration
st.set_page_config(
    page_title="DB-AI-AGENT",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
    .info-message {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #bee5eb;
    }
</style>
""", unsafe_allow_html=True)

def check_api_connection():
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"error": str(e)}

def get_database_schema():
    """Get database schema information."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/schema", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result is None:
                st.error("Empty schema response from API")
                return None
            return result
        else:
            st.error(f"Schema API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching schema: {str(e)}")
        return None

def execute_query(query: str, include_analysis: bool = True) -> Dict[str, Any]:
    """Execute a natural language query."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/query",
            headers={"Content-Type": "application/json"},
            json={
                "query": query,
                "session_id": SESSION_ID,
                "context": {},
                "max_results": 1000,
                "include_analysis": include_analysis
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result is None:
                return {"error": "Empty response from API"}
            return result
        else:
            return {"error": f"API Error: {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}


def _safe_number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def fetch_quarterly_trends_via_query(start_year: int, end_year: int) -> Optional[Dict[str, Any]]:
    # Prompt the agent to generate a concrete MongoDB aggregation, not prose
    nl_query = (
        "Generate a MongoDB aggregation pipeline (as strict JSON) over the 'sales' collection "
        f"for quarterly metrics between {start_year} and {end_year}. The pipeline must: "
        "1) match saleDate within the date range, 2) unwind items, 3) group by year and quarter "
        "(quarter = ceil(month/3)), computing: total count of sales as sales_count, sum(items.price*items.quantity) as revenue, and avg(customer.satisfaction) as avg_satisfaction, 4) sort by year,quarter. "
        "Return ONLY the aggregation pipeline as a JSON array in processed_query so it can be executed directly, no commentary."
    )
    # Try agentic path first
    result = execute_query(nl_query)
    if "error" in result or not result.get("query_result"):
        # Fallback: run a deterministic aggregation by sending an override
        override_pipeline = [
            {"$match": {"saleDate": {"$gte": {"$date": f"{start_year}-01-01T00:00:00Z"}, "$lte": {"$date": f"{end_year}-12-31T23:59:59Z"}}}},
            {"$unwind": "$items"},
            {"$group": {
                "_id": {"year": {"$year": "$saleDate"}, "quarter": {"$ceil": {"$divide": [{"$month": "$saleDate"}, 3]}}},
                "sales_count": {"$sum": 1},
                "revenue": {"$sum": {"$multiply": [{"$toDouble": "$items.price"}, "$items.quantity"]}},
                "avg_satisfaction": {"$avg": "$customer.satisfaction"}
            }},
            {"$project": {"_id": 0, "year": "$_id.year", "quarter": "$_id.quarter", "period": {"$concat": ["Q", {"$toString": "$_id.quarter"}, " ", {"$toString": "$_id.year"}]}, "sales_count": 1, "revenue": 1, "avg_satisfaction": 1}},
            {"$sort": {"year": 1, "quarter": 1}}
        ]
        result = execute_query("Run override", include_analysis=False)
        # We need to send context override; use direct POST to API as a fallback path
        try:
            resp = requests.post(
                f"{API_BASE_URL}/api/v1/query",
                headers={"Content-Type": "application/json"},
                json={
                    "query": "Quarterly override",
                    "session_id": SESSION_ID,
                    "context": {
                        "override": {
                            "target_collection": "sales",
                            "query_type": "aggregate",
                            "processed_query": override_pipeline
                        }
                    },
                    "include_analysis": False,
                    "max_results": 1000
                },
                timeout=60
            )
            if resp.status_code == 200:
                result = resp.json()
            else:
                return None
        except Exception:
            return None
    # If the service executed aggregate, results will be in query_result.result
    docs: List[Dict[str, Any]] = result.get("query_result", {}).get("result", [])
    if not isinstance(docs, list) or len(docs) == 0:
        return None

    normalized: List[Dict[str, Any]] = []
    for d in docs:
        year = int(d.get("year") or d.get("Year") or 0)
        quarter = int(d.get("quarter") or d.get("Quarter") or 0)
        period = d.get("period") or f"Q{quarter} {year}"
        sales_count = int(d.get("sales_count") or d.get("total_sales") or d.get("count") or 0)
        revenue = _safe_number(d.get("revenue") or d.get("total_revenue") or 0.0)
        avg_satisfaction = _safe_number(d.get("avg_satisfaction") or d.get("average_satisfaction") or 0.0)
        normalized.append({
            "period": period,
            "year": year,
            "quarter": quarter,
            "sales_count": sales_count,
            "revenue": revenue,
            "avg_satisfaction": round(avg_satisfaction, 2),
        })

    normalized.sort(key=lambda x: (x["year"], x["quarter"]))
    total_sales = sum(x["sales_count"] for x in normalized)
    total_revenue = sum(_safe_number(x["revenue"]) for x in normalized)
    for i in range(1, len(normalized)):
        prev = normalized[i - 1]["sales_count"]
        cur = normalized[i]["sales_count"]
        growth = (100.0 * (cur - prev) / prev) if prev > 0 else 0.0
        normalized[i]["growth_rate"] = round(growth, 2)

    if len(normalized) == 0:
        return None

    return {
        "success": True,
        "period": f"{start_year}-{end_year}",
        "total_sales": total_sales,
        "total_revenue": round(total_revenue, 2),
        "quarterly_data": normalized,
        "summary": {
            "avg_quarterly_sales": round(total_sales / max(1, len(normalized)), 2),
            "avg_quarterly_revenue": round(total_revenue / max(1, len(normalized)), 2),
            "best_quarter": max(normalized, key=lambda x: x["sales_count"]),
            "worst_quarter": min(normalized, key=lambda x: x["sales_count"]),
        },
    }


def fetch_monthly_trends_via_query(year: int) -> Optional[Dict[str, Any]]:
    nl_query = (
        "Generate a MongoDB aggregation pipeline (as strict JSON) over the 'sales' collection "
        f"to compute monthly metrics for {year}. The pipeline must: match saleDate within the year, unwind items, "
        "group by year and month computing: count as sales_count, sum(items.price*items.quantity) as revenue, avg(customer.satisfaction) as avg_satisfaction; sort by month. "
        "Return ONLY the aggregation pipeline as a JSON array in processed_query."
    )
    result = execute_query(nl_query)
    if "error" in result or not result.get("query_result"):
        # Fallback deterministic pipeline
        override_pipeline = [
            {"$match": {"saleDate": {"$gte": {"$date": f"{year}-01-01T00:00:00Z"}, "$lte": {"$date": f"{year}-12-31T23:59:59Z"}}}},
            {"$unwind": "$items"},
            {"$group": {
                "_id": {"year": {"$year": "$saleDate"}, "month": {"$month": "$saleDate"}},
                "sales_count": {"$sum": 1},
                "revenue": {"$sum": {"$multiply": [{"$toDouble": "$items.price"}, "$items.quantity"]}},
                "avg_satisfaction": {"$avg": "$customer.satisfaction"}
            }},
            {"$project": {"_id": 0, "year": "$_id.year", "month": "$_id.month", "month_name": "", "sales_count": 1, "revenue": 1, "avg_satisfaction": 1}},
            {"$sort": {"month": 1}}
        ]
        try:
            resp = requests.post(
                f"{API_BASE_URL}/api/v1/query",
                headers={"Content-Type": "application/json"},
                json={
                    "query": "Monthly override",
                    "session_id": SESSION_ID,
                    "context": {
                        "override": {
                            "target_collection": "sales",
                            "query_type": "aggregate",
                            "processed_query": override_pipeline
                        }
                    },
                    "include_analysis": False,
                    "max_results": 1000
                },
                timeout=60
            )
            if resp.status_code == 200:
                result = resp.json()
            else:
                return None
        except Exception:
            return None
    docs: List[Dict[str, Any]] = result.get("query_result", {}).get("result", [])
    if not isinstance(docs, list) or len(docs) == 0:
        return None

    normalized: List[Dict[str, Any]] = []
    for d in docs:
        month = int(d.get("month") or d.get("Month") or 0)
        month_name = d.get("month_name") or d.get("MonthName") or d.get("name") or str(month)
        sales_count = int(d.get("sales_count") or d.get("count") or d.get("total_sales") or 0)
        revenue = _safe_number(d.get("revenue") or d.get("total_revenue") or 0.0)
        avg_satisfaction = _safe_number(d.get("avg_satisfaction") or d.get("average_satisfaction") or 0.0)
        normalized.append({
            "month": month,
            "month_name": month_name,
            "sales_count": sales_count,
            "revenue": revenue,
            "avg_satisfaction": round(avg_satisfaction, 2),
        })

    normalized.sort(key=lambda x: x["month"])
    return {"success": True, "year": year, "monthly_data": normalized}


def fetch_purchase_method_trends_via_query(start_year: int, end_year: int) -> Optional[Dict[str, Any]]:
    nl_query = (
        "Generate a MongoDB aggregation pipeline (as strict JSON) over 'sales' to compute purchase method trends "
        f"between {start_year} and {end_year}. Match on saleDate, unwind items, group by purchaseMethod, year, quarter (ceil(month/3)) computing count and sum(items.price*items.quantity) as revenue; sort by method,year,quarter. "
        "Return ONLY the pipeline JSON in processed_query."
    )
    result = execute_query(nl_query)
    if "error" in result or not result.get("query_result"):
        override_pipeline = [
            {"$match": {"saleDate": {"$gte": {"$date": f"{start_year}-01-01T00:00:00Z"}, "$lte": {"$date": f"{end_year}-12-31T23:59:59Z"}}}},
            {"$unwind": "$items"},
            {"$group": {
                "_id": {"purchaseMethod": "$purchaseMethod", "year": {"$year": "$saleDate"}, "quarter": {"$ceil": {"$divide": [{"$month": "$saleDate"}, 3]}}},
                "count": {"$sum": 1},
                "revenue": {"$sum": {"$multiply": [{"$toDouble": "$items.price"}, "$items.quantity"]}}
            }},
            {"$project": {"_id": 0, "method": "$_id.purchaseMethod", "year": "$_id.year", "quarter": "$_id.quarter", "period": {"$concat": ["Q", {"$toString": "$_id.quarter"}, " ", {"$toString": "$_id.year"}]}, "count": 1, "revenue": 1}},
            {"$sort": {"method": 1, "year": 1, "quarter": 1}}
        ]
        try:
            resp = requests.post(
                f"{API_BASE_URL}/api/v1/query",
                headers={"Content-Type": "application/json"},
                json={
                    "query": "Method override",
                    "session_id": SESSION_ID,
                    "context": {
                        "override": {
                            "target_collection": "sales",
                            "query_type": "aggregate",
                            "processed_query": override_pipeline
                        }
                    },
                    "include_analysis": False,
                    "max_results": 1000
                },
                timeout=60
            )
            if resp.status_code == 200:
                result = resp.json()
            else:
                return None
        except Exception:
            return None
    docs: List[Dict[str, Any]] = result.get("query_result", {}).get("result", [])
    if not isinstance(docs, list) or len(docs) == 0:
        return None

    method_trends: Dict[str, List[Dict[str, Any]]] = {}
    for d in docs:
        method = (d.get("method") or d.get("purchaseMethod") or "unknown").lower()
        year = int(d.get("year") or 0)
        quarter = int(d.get("quarter") or 0)
        period = d.get("period") or f"Q{quarter} {year}"
        count = int(d.get("count") or d.get("sales_count") or 0)
        revenue = _safe_number(d.get("revenue") or 0.0)
        method_trends.setdefault(method, []).append({
            "period": period,
            "count": count,
            "revenue": revenue,
        })

    for m, arr in method_trends.items():
        arr.sort(key=lambda x: x["period"])  # Qn YYYY sorts OK lexicographically

    return {"success": True, "method_trends": method_trends}


def fetch_product_trends_via_query(start_year: int, end_year: int) -> Optional[Dict[str, Any]]:
    nl_query = (
        "Generate a MongoDB aggregation pipeline (as strict JSON) over 'sales' to compute per-product quarterly performance "
        f"for {start_year}-{end_year}. Match saleDate in range, unwind items, group by items.name, year, quarter; compute sum(items.quantity) as quantity, sum(items.price*items.quantity) as revenue, avg(items.price) as avg_price; sort by product,year,quarter. "
        "Return ONLY the pipeline JSON in processed_query."
    )
    result = execute_query(nl_query)
    if "error" in result or not result.get("query_result"):
        override_pipeline = [
            {"$match": {"saleDate": {"$gte": {"$date": f"{start_year}-01-01T00:00:00Z"}, "$lte": {"$date": f"{end_year}-12-31T23:59:59Z"}}}},
            {"$unwind": "$items"},
            {"$group": {
                "_id": {"product": "$items.name", "year": {"$year": "$saleDate"}, "quarter": {"$ceil": {"$divide": [{"$month": "$saleDate"}, 3]}}},
                "quantity": {"$sum": "$items.quantity"},
                "revenue": {"$sum": {"$multiply": [{"$toDouble": "$items.price"}, "$items.quantity"]}},
                "avg_price": {"$avg": {"$toDouble": "$items.price"}}
            }},
            {"$project": {"_id": 0, "product": "$_id.product", "year": "$_id.year", "quarter": "$_id.quarter", "period": {"$concat": ["Q", {"$toString": "$_id.quarter"}, " ", {"$toString": "$_id.year"}]}, "quantity": 1, "revenue": 1, "avg_price": 1}},
            {"$sort": {"product": 1, "year": 1, "quarter": 1}}
        ]
        try:
            resp = requests.post(
                f"{API_BASE_URL}/api/v1/query",
                headers={"Content-Type": "application/json"},
                json={
                    "query": "Product override",
                    "session_id": SESSION_ID,
                    "context": {
                        "override": {
                            "target_collection": "sales",
                            "query_type": "aggregate",
                            "processed_query": override_pipeline
                        }
                    },
                    "include_analysis": False,
                    "max_results": 1000
                },
                timeout=60
            )
            if resp.status_code == 200:
                result = resp.json()
            else:
                return None
        except Exception:
            return None
    docs: List[Dict[str, Any]] = result.get("query_result", {}).get("result", [])
    if not isinstance(docs, list) or len(docs) == 0:
        return None

    product_trends: Dict[str, List[Dict[str, Any]]] = {}
    for d in docs:
        product = d.get("product") or d.get("name") or "unknown"
        year = int(d.get("year") or 0)
        quarter = int(d.get("quarter") or 0)
        period = d.get("period") or f"Q{quarter} {year}"
        quantity = int(d.get("quantity") or 0)
        revenue = _safe_number(d.get("revenue") or 0.0)
        avg_price = _safe_number(d.get("avg_price") or 0.0)
        product_trends.setdefault(product, []).append({
            "period": period,
            "quantity": quantity,
            "revenue": revenue,
            "avg_price": avg_price,
        })

    for p, arr in product_trends.items():
        arr.sort(key=lambda x: x["period"])  # Qn YYYY sorts OK lexicographically

    return {"success": True, "product_trends": product_trends}

def analyze_query(query: str) -> Dict[str, Any]:
    """Analyze a query without executing it."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/analyze",
            headers={"Content-Type": "application/json"},
            json={
                "query": query,
                "session_id": SESSION_ID,
                "context": {}
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result is None:
                return {"error": "Empty response from API"}
            return result
        else:
            return {"error": f"API Error: {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

def create_visualization(data: List[Dict], query_type: str, query: str):
    """Create visualizations based on query results."""
    if not data or data is None:
        return None
    
    try:
        df = pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error creating DataFrame: {e}")
        return None
    
    # Remove ObjectId columns for visualization
    if '_id' in df.columns:
        df = df.drop('_id', axis=1)
    
    # Create visualizations based on data type and query
    if query_type == "count":
        # Simple count visualization
        fig = go.Figure(data=[
            go.Indicator(
                mode="number",
                value=len(data),
                title={"text": "Total Count"},
                number={'font': {'size': 50}}
            )
        ])
        fig.update_layout(height=300)
        return fig
    
    elif query_type == "aggregate" and "total" in query.lower():
        # Bar chart for aggregations
        if len(df.columns) >= 2:
            x_col = df.columns[0]
            y_col = df.columns[1]
            fig = px.bar(df, x=x_col, y=y_col, title=f"Results for: {query}")
            return fig
    
    elif "price" in query.lower() or "amount" in query.lower():
        # Histogram for price/amount data
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            fig = px.histogram(df, x=numeric_cols[0], title=f"Distribution for: {query}")
            return fig
    
    elif "location" in query.lower() or "store" in query.lower():
        # Map-like visualization for location data
        location_cols = [col for col in df.columns if 'location' in col.lower() or 'store' in col.lower()]
        if location_cols:
            location_counts = df[location_cols[0]].value_counts()
            fig = px.bar(x=location_counts.index, y=location_counts.values, 
                        title=f"Results by {location_cols[0]}")
            return fig
    
    # Default: Show data as table with basic chart
    if len(df.columns) >= 2:
        fig = px.scatter(df, x=df.columns[0], y=df.columns[1], title=f"Results for: {query}")
        return fig
    
    return None

def display_query_results(result: Dict[str, Any], query: str):
    """Display query results with visualizations."""
    if "error" in result:
        st.error(f"❌ Error: {result['error']}")
        if "details" in result:
            st.code(result["details"])
        return
    
    # Display success message
    st.success("✅ Query executed successfully!")
    
    # Display analysis information
    if "analysis" in result and result["analysis"] is not None:
        analysis = result["analysis"]
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Target Collection", analysis.get("target_collection", "N/A"))
        with col2:
            st.metric("Query Type", analysis.get("query_type", "N/A"))
        with col3:
            confidence = analysis.get("confidence_score", 0)
            st.metric("Confidence", f"{confidence:.2%}")
        with col4:
            execution_time = result.get("query_result", {}).get("execution_time", 0) if result.get("query_result") is not None else 0
            st.metric("Execution Time", f"{execution_time:.2f}s")
    
    # Display response
    if "response" in result:
        st.markdown("### 🤖 AI Response")
        st.info(result["response"])
    
    # Display results
    if "query_result" in result and result["query_result"] is not None and "result" in result["query_result"]:
        data = result["query_result"]["result"]
        
        if data and len(data) > 0:
            st.markdown("### 📊 Results")
            
            # Create DataFrame
            try:
                df = pd.DataFrame(data)
                
                # Display data
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating DataFrame: {e}")
                st.json(data)  # Fallback to JSON display
                return
            
            # Create visualization
            try:
                query_type = result.get("analysis", {}).get("query_type", "")
                fig = create_visualization(data, query_type, query)
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating visualization: {e}")
            
            # Download option
            try:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error creating CSV export: {e}")
        else:
            st.info("No results found for this query.")
    elif "query_result" in result and result["query_result"] is not None:
        # Handle case where query_result exists but has no "result" key
        st.info("Query executed but no data returned.")
    else:
        st.info("No query results available.")

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 DB-AI-AGENT</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Natural Language Database Query Assistant</p>', unsafe_allow_html=True)
    
    # Check API connection
    api_connected, health_data = check_api_connection()
    
    if not api_connected:
        st.error("❌ Cannot connect to DB-AI-AGENT API. Please ensure the server is running.")
        st.info("💡 Start the server with: `python3 scripts/start_server.py`")
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🔧 Configuration")
        
        # API Status
        st.markdown("### API Status")
        if api_connected:
            st.success("✅ API Connected")
            if "database" in health_data:
                st.info(f"📊 Database: {health_data.get('database', 'Unknown')}")
        else:
            st.error("❌ API Disconnected")
        
        # Database Schema
        st.markdown("### 📋 Database Schema")
        if st.button("🔄 Refresh Schema"):
            schema = get_database_schema()
            if schema:
                st.session_state.schema = schema
        
        if "schema" not in st.session_state:
            schema = get_database_schema()
            if schema:
                st.session_state.schema = schema
        
        if "schema" in st.session_state and st.session_state.schema is not None:
            schema = st.session_state.schema
            if "schemas" in schema and schema["schemas"]:
                for collection_name, collection_schema in schema["schemas"].items():
                    with st.expander(f"📁 {collection_name}"):
                        if "fields" in collection_schema and collection_schema["fields"]:
                            st.write("**Fields:**")
                            for field in collection_schema["fields"]:
                                st.write(f"• {field}")
                        
                        if "document_count" in collection_schema:
                            st.metric("Documents", collection_schema["document_count"])
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("📊 Show All Collections"):
            st.session_state.quick_query = "Show me all collections in the database"
        
        if st.button("🔢 Count All Documents"):
            st.session_state.quick_query = "How many documents are in each collection"
        
        if st.button("📈 Recent Sales"):
            st.session_state.quick_query = "Show me recent sales data"
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Query Database", "📊 Analysis", "📈 Examples", "ℹ️ Help"])
    
    with tab1:
        st.markdown('<h2 class="sub-header">🔍 Natural Language Query</h2>', unsafe_allow_html=True)
        
        # Query input
        query = st.text_area(
            "Enter your question in natural language:",
            placeholder="e.g., How many Online purchases? Show me sales from New York. What are the total sales by month?",
            height=100,
            key="query_input"
        )
        
        # Quick query from sidebar
        if "quick_query" in st.session_state:
            query = st.session_state.quick_query
            st.session_state.quick_query = None
        
        # Query options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            include_analysis = st.checkbox("Include Analysis", value=True)
        
        with col2:
            if st.button("🚀 Execute Query", type="primary"):
                if query and query.strip():
                    with st.spinner("Processing your query..."):
                        result = execute_query(query, include_analysis)
                        st.session_state.last_result = result
                        st.session_state.last_query = query
                        st.rerun()
                else:
                    st.warning("Please enter a query.")
        
        with col3:
            if st.button("🔍 Analyze Only"):
                if query and query.strip():
                    with st.spinner("Analyzing query..."):
                        result = analyze_query(query)
                        st.session_state.analysis_result = result
                        st.rerun()
                else:
                    st.warning("Please enter a query.")
        
        # Display results
        if "last_result" in st.session_state:
            st.markdown("---")
            display_query_results(st.session_state.last_result, st.session_state.last_query)
        
        # Display analysis only
        if "analysis_result" in st.session_state:
            st.markdown("---")
            st.markdown("### 🔍 Query Analysis")
            analysis = st.session_state.analysis_result
            
            if "error" in analysis:
                st.error(f"❌ Analysis Error: {analysis['error']}")
            elif analysis is not None:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Target Collection", analysis.get("target_collection", "N/A"))
                with col2:
                    st.metric("Query Type", analysis.get("query_type", "N/A"))
                with col3:
                    confidence = analysis.get("confidence_score", 0)
                    st.metric("Confidence", f"{confidence:.2%}")
                
                if "suggested_improvements" in analysis and analysis["suggested_improvements"]:
                    st.markdown("### 💡 Suggestions")
                    for suggestion in analysis["suggested_improvements"]:
                        st.info(f"• {suggestion}")
    
    with tab2:
        st.markdown('<h2 class="sub-header">📊 Database Analysis</h2>', unsafe_allow_html=True)
        
        # Analysis options
        analysis_type = st.selectbox(
            "Choose Analysis Type:",
            ["Collection Overview", "Data Distribution", "Trend Analysis", "Performance Metrics"]
        )
        
        if analysis_type == "Collection Overview":
            st.markdown("### 📋 Collection Overview")
            
            if "schema" in st.session_state:
                schema = st.session_state.schema
                if "schemas" in schema:
                    # Create overview DataFrame
                    overview_data = []
                    for collection_name, collection_schema in schema["schemas"].items():
                        overview_data.append({
                            "Collection": collection_name,
                            "Documents": collection_schema.get("document_count", 0),
                            "Fields": len(collection_schema.get("fields", [])),
                            "Sample Available": "Yes" if "sample_document" in collection_schema else "No"
                        })
                    
                    df = pd.DataFrame(overview_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Visualization
                    fig = px.bar(df, x="Collection", y="Documents", 
                                title="Document Count by Collection")
                    st.plotly_chart(fig, use_container_width=True)
        
        elif analysis_type == "Data Distribution":
            st.markdown("### 📊 Data Distribution Analysis")
            
            query = "Show me the distribution of purchase methods"
            if st.button("Analyze Purchase Methods"):
                with st.spinner("Analyzing data distribution..."):
                    result = execute_query(query)
                    if "error" not in result:
                        display_query_results(result, query)
        
        elif analysis_type == "Trend Analysis":
            st.markdown("### 📈 Trend Analysis")
            
            # Trend analysis options
            trend_type = st.selectbox(
                "Select Trend Type:",
                ["Quarterly Sales", "Monthly Sales", "Purchase Methods", "Product Performance"]
            )
            
            col1, col2 = st.columns(2)
            with col1:
                start_year = st.number_input("Start Year", min_value=2020, max_value=2025, value=2023)
            with col2:
                end_year = st.number_input("End Year", min_value=2020, max_value=2025, value=2024)
            
            if st.button("📊 Generate Trend Report"):
                with st.spinner("Generating trend analysis..."):
                    data = None
                    if trend_type == "Quarterly Sales":
                        data = fetch_quarterly_trends_via_query(start_year, end_year)
                        if data:
                            st.success("✅ Trend analysis completed!")
                            display_quarterly_trends(data)
                        else:
                            st.error("❌ Unable to compute quarterly trends via query API")
                    elif trend_type == "Monthly Sales":
                        data = fetch_monthly_trends_via_query(end_year)
                        if data:
                            st.success("✅ Trend analysis completed!")
                            display_monthly_trends(data)
                        else:
                            st.error("❌ Unable to compute monthly trends via query API")
                    elif trend_type == "Purchase Methods":
                        data = fetch_purchase_method_trends_via_query(start_year, end_year)
                        if data:
                            st.success("✅ Trend analysis completed!")
                            display_purchase_method_trends(data)
                        else:
                            st.error("❌ Unable to compute purchase method trends via query API")
                    elif trend_type == "Product Performance":
                        data = fetch_product_trends_via_query(start_year, end_year)
                        if data:
                            st.success("✅ Trend analysis completed!")
                            display_product_trends(data)
                        else:
                            st.error("❌ Unable to compute product performance trends via query API")
        
        elif analysis_type == "Performance Metrics":
            st.markdown("### ⚡ Performance Metrics")
            
            # Mock performance data
            performance_data = {
                "Metric": ["Average Query Time", "Cache Hit Rate", "Success Rate", "Active Connections"],
                "Value": ["2.3s", "78%", "95%", "12"],
                "Status": ["Good", "Good", "Excellent", "Normal"]
            }
            
            df = pd.DataFrame(performance_data)
            st.dataframe(df, use_container_width=True)
    
    with tab3:
        st.markdown('<h2 class="sub-header">📈 Example Queries</h2>', unsafe_allow_html=True)
        
        # Example queries organized by category
        examples = {
            "Count Queries": [
                "How many Online purchases?",
                "Count all documents in sales collection",
                "How many customers are from New York?",
                "What's the total number of products?"
            ],
            "Filter Queries": [
                "Show me sales from New York",
                "Find expensive products over $100",
                "Display online purchases from last month",
                "Show customers with high satisfaction ratings"
            ],
            "Aggregation Queries": [
                "What are the total sales by month?",
                "Show me average order value by location",
                "Calculate total revenue by product category",
                "Find the top 5 products by sales volume"
            ],
            "Analysis Queries": [
                "Analyze customer satisfaction trends",
                "Show me sales performance by store location",
                "What are the most popular purchase methods?",
                "Analyze sales patterns by customer age"
            ]
        }
        
        for category, queries in examples.items():
            st.markdown(f"### {category}")
            for query in queries:
                if st.button(f"🔍 {query}", key=f"example_{category}_{query}"):
                    st.session_state.quick_query = query
                    st.rerun()
            st.markdown("---")
    
    with tab4:
        st.markdown('<h2 class="sub-header">ℹ️ Help & Documentation</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 🎯 How to Use DB-AI-AGENT
        
        **1. Natural Language Queries**
        - Ask questions in plain English
        - The AI understands context and intent
        - No need to learn complex query syntax
        
        **2. Query Types Supported**
        - **Count Queries**: "How many...?"
        - **Filter Queries**: "Show me... where..."
        - **Aggregation Queries**: "What are the totals...?"
        - **Analysis Queries**: "Analyze... trends"
        
        **3. Best Practices**
        - Be specific about what you want
        - Mention relevant fields or values
        - Use natural language patterns
        
        **4. Tips for Better Results**
        - Include collection names when relevant
        - Specify time periods for temporal data
        - Use descriptive terms for filtering
        - Ask for summaries for large datasets
        """)
        
        st.markdown("### 🔧 Technical Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **API Endpoints:**
            - `/api/v1/query` - Execute queries
            - `/api/v1/analyze` - Analyze queries
            - `/api/v1/schema` - Get database schema
            - `/health` - Health check
            """)
        
        with col2:
            st.markdown("""
            **Features:**
            - Natural language processing
            - Intelligent query generation
            - Result visualization
            - Export capabilities
            - Performance monitoring
            """)
        
        st.markdown("### 📞 Support")
        st.info("""
        For technical support or questions about the DB-AI-AGENT:
        - Check the API documentation
        - Review the performance optimization guide
        - Contact the development team
        """)


def display_quarterly_trends(data):
    """Display quarterly sales trends."""
    st.markdown("### 📈 Quarterly Sales Trends")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"${data['total_revenue']:,.2f}")
    with col2:
        st.metric("Total Sales", f"{data['total_sales']:,}")
    with col3:
        st.metric("Avg Quarterly Sales", f"{data['summary']['avg_quarterly_sales']:.0f}")
    with col4:
        st.metric("Avg Quarterly Revenue", f"${data['summary']['avg_quarterly_revenue']:,.2f}")
    
    # Create DataFrame for visualization
    df = pd.DataFrame(data['quarterly_data'])
    
    # Sales trend chart
    fig1 = px.line(df, x='period', y='sales_count', title='Quarterly Sales Count',
                   labels={'sales_count': 'Sales Count', 'period': 'Quarter'})
    st.plotly_chart(fig1, use_container_width=True)
    
    # Revenue trend chart
    fig2 = px.bar(df, x='period', y='revenue', title='Quarterly Revenue',
                  labels={'revenue': 'Revenue ($)', 'period': 'Quarter'})
    st.plotly_chart(fig2, use_container_width=True)
    
    # Growth rate chart
    if 'growth_rate' in df.columns:
        fig3 = px.line(df, x='period', y='growth_rate', title='Quarterly Growth Rate (%)',
                      labels={'growth_rate': 'Growth Rate (%)', 'period': 'Quarter'})
        st.plotly_chart(fig3, use_container_width=True)
    
    # Summary table
    st.markdown("### 📋 Quarterly Summary")
    st.dataframe(df, use_container_width=True)


def display_monthly_trends(data):
    """Display monthly sales trends."""
    st.markdown("### 📅 Monthly Sales Trends")
    
    # Create DataFrame
    df = pd.DataFrame(data['monthly_data'])
    
    # Monthly sales chart
    fig1 = px.line(df, x='month_name', y='sales_count', title='Monthly Sales Count',
                   labels={'sales_count': 'Sales Count', 'month_name': 'Month'})
    st.plotly_chart(fig1, use_container_width=True)
    
    # Monthly revenue chart
    fig2 = px.bar(df, x='month_name', y='revenue', title='Monthly Revenue',
                  labels={'revenue': 'Revenue ($)', 'month_name': 'Month'})
    st.plotly_chart(fig2, use_container_width=True)
    
    # Summary table
    st.markdown("### 📋 Monthly Summary")
    st.dataframe(df, use_container_width=True)


def display_purchase_method_trends(data):
    """Display purchase method trends."""
    st.markdown("### 💳 Purchase Method Trends")
    
    method_trends = data['method_trends']
    
    # Create combined DataFrame
    all_data = []
    for method, trends in method_trends.items():
        for trend in trends:
            all_data.append({
                'Method': method.title(),
                'Period': trend['period'],
                'Count': trend['count'],
                'Revenue': trend['revenue']
            })
    
    df = pd.DataFrame(all_data)
    
    # Method comparison chart
    fig1 = px.bar(df, x='Period', y='Count', color='Method', 
                  title='Sales Count by Purchase Method',
                  labels={'Count': 'Sales Count', 'Period': 'Quarter'})
    st.plotly_chart(fig1, use_container_width=True)
    
    # Revenue comparison chart
    fig2 = px.bar(df, x='Period', y='Revenue', color='Method',
                  title='Revenue by Purchase Method',
                  labels={'Revenue': 'Revenue ($)', 'Period': 'Quarter'})
    st.plotly_chart(fig2, use_container_width=True)
    
    # Summary table
    st.markdown("### 📋 Purchase Method Summary")
    st.dataframe(df, use_container_width=True)


def display_product_trends(data):
    """Display product performance trends."""
    st.markdown("### 🛍️ Product Performance Trends")
    
    product_trends = data['product_trends']
    
    # Calculate total performance for each product
    product_summary = []
    for product, trends in product_trends.items():
        total_quantity = sum(t['quantity'] for t in trends)
        total_revenue = sum(t['revenue'] for t in trends)
        avg_price = sum(t['avg_price'] for t in trends) / len(trends) if trends else 0
        
        product_summary.append({
            'Product': product,
            'Total Quantity': total_quantity,
            'Total Revenue': total_revenue,
            'Avg Price': avg_price
        })
    
    df = pd.DataFrame(product_summary)
    df = df.sort_values('Total Revenue', ascending=False)
    
    # Top products by revenue
    fig1 = px.bar(df.head(10), x='Product', y='Total Revenue',
                  title='Top Products by Revenue',
                  labels={'Total Revenue': 'Revenue ($)', 'Product': 'Product'})
    st.plotly_chart(fig1, use_container_width=True)
    
    # Product quantity comparison
    fig2 = px.bar(df.head(10), x='Product', y='Total Quantity',
                  title='Product Sales Quantity',
                  labels={'Total Quantity': 'Quantity Sold', 'Product': 'Product'})
    st.plotly_chart(fig2, use_container_width=True)
    
    # Summary table
    st.markdown("### 📋 Product Performance Summary")
    st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    main() 