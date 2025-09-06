import logging
from typing import Dict, List, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from app.config import settings
from app.services.db_service import db_service
from app.services.ai_service import ai_service
from app.database.schemas import QueryAnalysis, QueryResult

logger = logging.getLogger(__name__)


class DatabaseAgent:
    """LangGraph agent for database operations and query processing."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.1,
            api_key=settings.openai_api_key
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Define the state schema
        workflow = StateGraph({
            "messages": List[Any],
            "query": str,
            "database_schema": Dict[str, Any],
            "analysis": Optional[QueryAnalysis],
            "query_result": Optional[QueryResult],
            "response": str,
            "error": Optional[str]
        })
        
        # Add nodes
        workflow.add_node("analyze_query", self._analyze_query_node)
        workflow.add_node("execute_query", self._execute_query_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Define edges
        workflow.add_edge("analyze_query", "execute_query")
        workflow.add_edge("execute_query", "generate_response")
        workflow.add_edge("generate_response", END)
        workflow.add_edge("handle_error", END)
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "analyze_query",
            self._should_execute_query,
            {
                "execute": "execute_query",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "execute_query",
            self._should_generate_response,
            {
                "generate": "generate_response",
                "error": "handle_error"
            }
        )
        
        return workflow.compile()
    
    def _analyze_query_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the natural language query."""
        try:
            query = state["query"]
            database_schema = state["database_schema"]
            
            # Use AI service to analyze the query
            analysis = ai_service.analyze_query(query, database_schema)
            
            # Add analysis to state
            state["analysis"] = analysis
            
            # Add analysis message
            state["messages"].append(
                AIMessage(content=f"Query analyzed. Target collection: {analysis.target_collection}, Type: {analysis.query_type}")
            )
            
            return state
            
        except Exception as e:
            logger.error(f"Error in analyze_query_node: {e}")
            state["error"] = f"Query analysis failed: {str(e)}"
            return state
    
    def _execute_query_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the database query based on analysis."""
        try:
            analysis = state["analysis"]
            
            if not analysis or not analysis.target_collection:
                state["error"] = "No valid analysis or target collection found"
                return state
            
            # Execute query based on type
            if analysis.query_type == "find":
                # Parse the processed query (assuming it's a JSON string)
                import json
                query_filter = json.loads(analysis.processed_query) if analysis.processed_query else {}
                result = db_service.execute_find_query(analysis.target_collection, query_filter)
                
            elif analysis.query_type == "aggregate":
                # Parse the aggregation pipeline
                import json
                pipeline = json.loads(analysis.processed_query) if analysis.processed_query else []
                result = db_service.execute_aggregate_query(analysis.target_collection, pipeline)
                
            elif analysis.query_type == "count":
                # Parse the count query
                import json
                query_filter = json.loads(analysis.processed_query) if analysis.processed_query else {}
                result = db_service.execute_count_query(analysis.target_collection, query_filter)
                
            else:
                state["error"] = f"Unsupported query type: {analysis.query_type}"
                return state
            
            state["query_result"] = result
            
            # Add execution message
            state["messages"].append(
                AIMessage(content=f"Query executed. Found {result.total_count} results in {result.execution_time:.2f}s")
            )
            
            return state
            
        except Exception as e:
            logger.error(f"Error in execute_query_node: {e}")
            state["error"] = f"Query execution failed: {str(e)}"
            return state
    
    def _generate_response_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate natural language response based on query results."""
        try:
            query = state["query"]
            query_result = state["query_result"]
            database_schema = state["database_schema"]
            
            if not query_result or query_result.error:
                state["error"] = query_result.error if query_result else "No query result available"
                return state
            
            # Generate response using AI service
            response = ai_service.generate_response(query, query_result.dict(), database_schema)
            state["response"] = response
            
            # Add response message
            state["messages"].append(AIMessage(content=response))
            
            return state
            
        except Exception as e:
            logger.error(f"Error in generate_response_node: {e}")
            state["error"] = f"Response generation failed: {str(e)}"
            return state
    
    def _handle_error_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors in the workflow."""
        error = state.get("error", "Unknown error occurred")
        
        # Generate error response
        error_response = f"I apologize, but I encountered an error while processing your request: {error}"
        state["response"] = error_response
        
        # Add error message
        state["messages"].append(AIMessage(content=error_response))
        
        return state
    
    def _should_execute_query(self, state: Dict[str, Any]) -> str:
        """Determine if we should execute the query or handle error."""
        if state.get("error"):
            return "error"
        return "execute"
    
    def _should_generate_response(self, state: Dict[str, Any]) -> str:
        """Determine if we should generate response or handle error."""
        if state.get("error"):
            return "error"
        return "generate"
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a natural language query through the agent workflow."""
        try:
            # Get database schema
            database_info = db_service.get_database_info()
            
            # Initialize state
            initial_state = {
                "messages": [HumanMessage(content=query)],
                "query": query,
                "database_schema": database_info,
                "analysis": None,
                "query_result": None,
                "response": "",
                "error": None
            }
            
            # Execute the workflow
            final_state = self.graph.invoke(initial_state)
            
            return {
                "success": not final_state.get("error"),
                "response": final_state.get("response", ""),
                "analysis": final_state.get("analysis"),
                "query_result": final_state.get("query_result"),
                "error": final_state.get("error"),
                "messages": final_state.get("messages", [])
            }
            
        except Exception as e:
            logger.error(f"Error in process_query: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": f"I apologize, but I encountered an error: {str(e)}"
            }


# Global database agent instance
db_agent = DatabaseAgent() 