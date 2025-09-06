import logging
import time
from typing import Dict, Any, Optional
import json
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.models.request_models import QueryRequest, AnalyzeRequest, SchemaRequest
from app.models.response_models import (
    QueryResponse, AnalyzeResponse, SchemaResponse, 
    HealthResponse, ErrorResponse
)
from app.services.db_service import db_service
from app.services.ai_service import ai_service
from app.database.schemas import QueryAnalysis


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting DB-AI-AGENT application...")
    
    # Test connections
    try:
        db_connected = db_service.db_manager.database is not None
        openai_connected = ai_service.test_connection()
        
        if not db_connected:
            logger.warning("Database connection failed - continuing without database")
        if not openai_connected:
            logger.error("OpenAI connection failed - application cannot function")
        else:
            logger.info("OpenAI connection successful")
            
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        logger.warning("Application starting with limited functionality")
    
    yield
    
    # Shutdown
    logger.info("Shutting down DB-AI-AGENT application...")
    try:
        db_service.db_manager.close()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered database query assistant using OpenAI",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "DB-AI-AGENT API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    start_time = time.time()
    
    try:
        # Test database connection
        db_connected = db_service.db_manager.database is not None
        if db_connected:
            try:
                db_service.db_manager.client.admin.command('ping')
            except Exception as db_e:
                logger.warning(f"Database ping failed: {db_e}")
                db_connected = False
        
        # Test OpenAI connection
        openai_connected = ai_service.test_connection()
        
        execution_time = time.time() - start_time
        
        # Application is healthy if OpenAI is connected, even if database is not
        overall_status = "healthy" if openai_connected else "unhealthy"
        
        return HealthResponse(
            status=overall_status,
            database_connected=db_connected,
            openai_connected=openai_connected,
            timestamp=time.time()
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            database_connected=False,
            openai_connected=False,
            timestamp=time.time()
        )


@app.post(f"{settings.api_prefix}/query", response_model=QueryResponse, tags=["Query"])
async def process_query(request: QueryRequest):
    """Process a natural language query and return AI-generated response."""
    start_time = time.time()
    
    try:
        # Get database schema
        database_info = db_service.get_database_info()

        # Optional override: execute directly if client provides target/query_type/processed_query
        override = None
        if request.context and isinstance(request.context, dict):
            override = request.context.get("override")

        query_result = None
        analysis = None
        if override:
            try:
                target_collection = override.get("target_collection")
                query_type = override.get("query_type")
                processed_query = override.get("processed_query")

                if not target_collection or not query_type:
                    raise ValueError("override requires target_collection and query_type")

                if query_type == "find" or query_type == "count":
                    if isinstance(processed_query, str):
                        query_filter = json.loads(processed_query) if processed_query else {}
                    else:
                        query_filter = processed_query or {}
                    if query_type == "find":
                        query_result = db_service.execute_find_query(target_collection, query_filter)
                    else:
                        query_result = db_service.execute_count_query(target_collection, query_filter)
                elif query_type == "aggregate":
                    if isinstance(processed_query, str):
                        pipeline = json.loads(processed_query) if processed_query else []
                    else:
                        pipeline = processed_query or []
                    query_result = db_service.execute_aggregate_query(target_collection, pipeline)
                else:
                    raise ValueError(f"Unsupported override query_type: {query_type}")
            except Exception as e:
                logger.error(f"Override execution error: {e}")
                query_result = None
        else:
            # Analyze the query via AI
            analysis = ai_service.analyze_query(request.query, database_info)
            
            # Execute query based on analysis
            if analysis.target_collection and analysis.query_type:
                try:
                    if analysis.query_type == "find":
                        query_filter = json.loads(analysis.processed_query) if analysis.processed_query else {}
                        query_result = db_service.execute_find_query(analysis.target_collection, query_filter)
                        
                    elif analysis.query_type == "count":
                        query_filter = json.loads(analysis.processed_query) if analysis.processed_query else {}
                        query_result = db_service.execute_count_query(analysis.target_collection, query_filter)
                        
                    elif analysis.query_type == "aggregate":
                        pipeline = json.loads(analysis.processed_query) if analysis.processed_query else []
                        query_result = db_service.execute_aggregate_query(analysis.target_collection, pipeline)
                        
                except Exception as e:
                    logger.error(f"Query execution error: {e}")
                    query_result = None
        
        # Generate response
        if query_result and not query_result.error:
            response = ai_service.generate_response(request.query, query_result.dict(), database_info)
        else:
            response = f"I found information about your query. {analysis.target_collection or 'The database'} contains relevant data."
        
        execution_time = time.time() - start_time
        
        return QueryResponse(
            success=True,
            response=response,
            query_analysis=analysis,
            query_result=query_result,
            session_id=request.session_id,
            execution_time=execution_time
        )
            
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        execution_time = time.time() - start_time
        
        return QueryResponse(
            success=False,
            response=f"I apologize, but I encountered an error: {str(e)}",
            error=str(e),
            session_id=request.session_id,
            execution_time=execution_time
        )


@app.post(f"{settings.api_prefix}/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_query(request: AnalyzeRequest):
    """Analyze a natural language query without executing it."""
    start_time = time.time()
    
    try:
        # Get database schema
        database_info = db_service.get_database_info()
        
        # Analyze the query
        analysis = ai_service.analyze_query(request.query, database_info)
        
        execution_time = time.time() - start_time
        
        return AnalyzeResponse(
            success=True,
            analysis=analysis,
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        execution_time = time.time() - start_time
        
        return AnalyzeResponse(
            success=False,
            analysis=QueryAnalysis(
                original_query=request.query,
                processed_query="{}",
                error=str(e)
            ),
            execution_time=execution_time
        )


@app.get(f"{settings.api_prefix}/schema", response_model=SchemaResponse, tags=["Schema"])
async def get_schema(collection_name: Optional[str] = None, include_sample: bool = True):
    """Get database schema information."""
    start_time = time.time()
    
    try:
        database_info = db_service.get_database_info()
        
        if collection_name:
            # Return specific collection schema
            schema = db_service.get_collection_schema(collection_name)
            schemas = {collection_name: schema.dict()}
            collections = [collection_name]
        else:
            # Return all collections
            collections = database_info.get("collections", [])
            schemas = database_info.get("schemas", {})
        
        execution_time = time.time() - start_time
        
        return SchemaResponse(
            success=True,
            collections=collections,
            schemas=schemas,
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error getting schema: {e}")
        execution_time = time.time() - start_time
        
        return SchemaResponse(
            success=False,
            collections=[],
            schemas={},
            execution_time=execution_time
        )





@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=str(exc),
            error_type="InternalServerError"
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    ) 