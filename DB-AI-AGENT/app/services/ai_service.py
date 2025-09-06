import logging
import time
import json
from typing import Dict, List, Any, Optional
import openai
from openai import OpenAI

from app.config import settings
from app.database.schemas import QueryAnalysis

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI operations and OpenAI integration."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    def analyze_query(self, query: str, database_schema: Dict[str, Any]) -> QueryAnalysis:
        """Analyze a natural language query and convert it to database operations."""
        start_time = time.time()
        
        try:
            # Create system prompt for query analysis
            system_prompt = f"""
            You are a database query analyzer. Your job is to:
            1. Analyze the user's natural language query
            2. Understand the database schema
            3. Determine the appropriate collection to query
            4. Generate the appropriate MongoDB query or aggregation pipeline
            5. Provide confidence score and suggestions
            
            Database Schema:
            {database_schema}
            
            Return your analysis in the following JSON format:
            {{
                "target_collection": "collection_name",
                "query_type": "find|aggregate|count",
                "processed_query": "the processed query or pipeline as a JSON string",
                "confidence_score": 0.0-1.0,
                "suggested_improvements": ["suggestion1", "suggestion2"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Query: {query}"}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse the response
            content = response.choices[0].message.content
            analysis_data = self._parse_json_response(content)
            
            execution_time = time.time() - start_time
            
            return QueryAnalysis(
                original_query=query,
                processed_query=analysis_data.get("processed_query", "{}"),
                target_collection=analysis_data.get("target_collection"),
                query_type=analysis_data.get("query_type", "unknown"),
                confidence_score=analysis_data.get("confidence_score", 0.0),
                suggested_improvements=analysis_data.get("suggested_improvements", [])
            )
            
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return QueryAnalysis(
                original_query=query,
                processed_query="{}",
                error=f"Analysis error: {str(e)}"
            )
    
    def generate_response(self, query: str, query_result: Dict[str, Any], 
                        database_schema: Dict[str, Any]) -> str:
        """Generate a natural language response based on query results."""
        try:
            # Create system prompt for response generation
            system_prompt = f"""
            You are a helpful database assistant. Your job is to:
            1. Understand the user's question
            2. Analyze the database results
            3. Provide a clear, helpful response in natural language
            4. Format the response appropriately based on the data type
            
            Database Schema:
            {database_schema}
            
            Query Results:
            {query_result}
            
            Provide a helpful, conversational response that answers the user's question.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Question: {query}"}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    def process_natural_language_query(self, query: str, database_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Process a natural language query end-to-end."""
        start_time = time.time()
        
        try:
            # Step 1: Analyze the query
            analysis = self.analyze_query(query, database_schema)
            
            # Step 2: Generate response based on analysis
            response = self.generate_response(query, {"analysis": analysis.dict()}, database_schema)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "response": response,
                "analysis": analysis.dict(),
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Error processing natural language query: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from OpenAI."""
        import re
        
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # If no JSON found, return empty dict
                return {}
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON response: {content}")
            return {}
    
    def test_connection(self) -> bool:
        """Test OpenAI connection."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False


# Global AI service instance
ai_service = AIService() 