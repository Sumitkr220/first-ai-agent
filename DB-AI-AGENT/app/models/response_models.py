from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.database.schemas import QueryAnalysis, QueryResult


class QueryResponse(BaseModel):
    """Response model for database queries."""
    success: bool = Field(..., description="Whether the query was successful")
    response: str = Field(..., description="AI-generated response to the query")
    query_analysis: Optional[QueryAnalysis] = Field(None, description="Analysis of the query")
    query_result: Optional[QueryResult] = Field(None, description="Raw query results")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")
    execution_time: float = Field(..., description="Total execution time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AnalyzeResponse(BaseModel):
    """Response model for query analysis."""
    success: bool = Field(..., description="Whether the analysis was successful")
    analysis: QueryAnalysis = Field(..., description="Query analysis results")
    execution_time: float = Field(..., description="Analysis execution time in seconds")


class SchemaResponse(BaseModel):
    """Response model for schema information."""
    success: bool = Field(..., description="Whether the schema retrieval was successful")
    collections: List[str] = Field(..., description="List of collection names")
    schemas: Dict[str, Dict[str, Any]] = Field(..., description="Schema information for collections")
    execution_time: float = Field(..., description="Schema retrieval time in seconds")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field("1.0.0", description="API version")
    database_connected: bool = Field(..., description="Database connection status")
    openai_connected: bool = Field(..., description="OpenAI connection status")


class ErrorResponse(BaseModel):
    """Response model for errors."""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details") 