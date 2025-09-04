"""
AI Student Support Service - Main Application Entry Point
"""
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

from app.utils.logger import get_logger
from app.utils.exception_handler import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)

# Configure logging
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    logger.info("Starting AI Student Support Service...")
    
    # Initialize all services during startup
    try:
        from app.utils.service_utils import get_services
        from app.utils.service_manager import set_global_services
        
        logger.info("Initializing AI services...")
        ai_service, rag_service, chroma_service = get_services()
        
        # Wire up service dependencies
        logger.info("Wiring up service dependencies...")
        rag_service.set_chroma_service(chroma_service)
        ai_service.set_rag_service(rag_service)
        
        # Set global services in the service manager
        set_global_services(ai_service, rag_service, chroma_service)
        
        # ChromaDB service is already initialized in __init__
        logger.info("ChromaDB service initialized successfully")
        
        # Initialize AI service (this will also initialize RAG service)
        logger.info("Initializing AI service...")
        if hasattr(ai_service, 'ensure_initialized'):
            await ai_service.ensure_initialized()
        logger.info("AI service initialized successfully")
        
        logger.info("All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        logger.warning("Service will continue but may not function properly")
    
    yield
    
    logger.info("Shutting down AI Student Support Service...")


# Create FastAPI app
app = FastAPI(
    title="AI Student Support Service",
    description="""
    AI-powered student support using DeepSeek AI and RAG capabilities.
    
    Features:
    - DeepSeek Chat v3.1 integration
    - Document management (text and PDF)
    - Semantic search and retrieval
    - Intelligent escalation system
    - Vector database storage
    
    Architecture:
    - AI microservice generates responses and escalation data
    - Backend microservice handles storage and business logic
    """,
    version="2.0.0",
    contact={
        "name": "AI Student Support Team",
        "email": "support@businessanalysisschool.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "Chat",
            "description": "AI-powered chat with RAG and escalation data generation"
        },
        {
            "name": "Documents",
            "description": "Document management for text and PDF files"
        },
        {
            "name": "Search",
            "description": "Semantic search and document retrieval"
        },
        {
            "name": "Health",
            "description": "System health and service status checks"
        }
    ],
    lifespan=lifespan
)

# Add exception handlers for standardized error responses
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers (moved here to avoid circular imports)
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.search import router as search_router
from app.api.health import router as health_router

# Include routers
app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(documents_router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(search_router, prefix="/api/v1/search", tags=["Search"])
app.include_router(health_router, prefix="/health", tags=["Health"])


@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root endpoint providing service information."""
    # Get global services from service manager
    from app.utils.service_manager import get_global_services
    ai_service, rag_service, chroma_service = get_global_services()
    
    # Check service status
    services_status = {}
    if ai_service:
        services_status["ai_service"] = ai_service.get_status() if hasattr(ai_service, 'get_status') else {"status": "initialized"}
    if rag_service:
        services_status["rag_service"] = rag_service.get_status() if hasattr(rag_service, 'get_status') else {"status": "initialized"}
    if chroma_service:
        services_status["chroma_service"] = chroma_service.get_status() if hasattr(chroma_service, 'get_status') else {"status": "initialized"}
    
    return {
        "service": "AI Student Support Service",
        "version": "2.0.0",
        "status": "running",
        "description": "AI-powered student support with RAG and DeepSeek AI capabilities",
        "services_status": services_status,
        "features": [
            "DeepSeek AI v3.1 integration",
            "RAG (Retrieval-Augmented Generation)",
            "Intelligent escalation data generation",
            "LLM-generated escalation messages",
            "ChromaDB vector database",
            "Document management system",
            "Semantic search capabilities",
            "Real-time service monitoring"
        ],
        "endpoints": {
            "chat": "/api/v1/chat",
            "documents": "/api/v1/documents",
            "search": "/api/v1/search",
            "health": "/health",
            "docs": "/docs"
        },
        "ai_provider": "DeepSeek Chat v3.1 (via OpenRouter)",
        "escalation": "Data generation only - backend handles storage and triggering",
        "architecture": "AI microservice - backend handles business logic"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

