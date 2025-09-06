from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class DatabaseSchema(BaseModel):
    """Schema for database structure information."""
    collections: List[str] = Field(default_factory=list)
    schemas: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class CollectionSchema(BaseModel):
    """Schema for collection structure information."""
    collection_name: str
    fields: List[str] = Field(default_factory=list)
    sample_document: Optional[Dict[str, Any]] = None
    document_count: Optional[int] = None


class QueryResult(BaseModel):
    """Schema for query results."""
    query: str
    result: List[Dict[str, Any]] = Field(default_factory=list)
    total_count: int = 0
    execution_time: float = 0.0
    error: Optional[str] = None


class QueryAnalysis(BaseModel):
    """Schema for query analysis results."""
    original_query: str
    processed_query: str
    target_collection: Optional[str] = None
    query_type: str = "unknown"  # find, aggregate, count, etc.
    confidence_score: float = 0.0
    suggested_improvements: List[str] = Field(default_factory=list)


class ConversationHistory(BaseModel):
    """Schema for conversation history."""
    session_id: str
    user_query: str
    ai_response: str
    query_analysis: Optional[QueryAnalysis] = None
    query_result: Optional[QueryResult] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time: float = 0.0 