from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for database queries."""
    query: str = Field(..., description="Natural language query or question")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the query")
    max_results: Optional[int] = Field(100, description="Maximum number of results to return")
    include_analysis: Optional[bool] = Field(True, description="Include query analysis in response")


class AnalyzeRequest(BaseModel):
    """Request model for query analysis."""
    query: str = Field(..., description="Query to analyze")
    target_collection: Optional[str] = Field(None, description="Target collection for the query")


class SchemaRequest(BaseModel):
    """Request model for schema information."""
    collection_name: Optional[str] = Field(None, description="Specific collection name, if not provided returns all")
    include_sample: Optional[bool] = Field(True, description="Include sample documents in response") 