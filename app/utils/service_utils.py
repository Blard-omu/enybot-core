"""
Utility functions for service management.
"""
from fastapi import HTTPException
from app.services.ai_service import AIService
from app.services.rag_service import RAGService
from app.services.chroma_service import ChromaService
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_services() -> tuple[AIService, RAGService, ChromaService]:
    """Get initialized service instances with error handling."""
    try:
        # Initialize services
        ai_service = AIService()
        rag_service = RAGService()
        chroma_service = ChromaService()
        
        # Set up service dependencies
        rag_service.set_ai_service(ai_service)
        
        return ai_service, rag_service, chroma_service
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise HTTPException(status_code=503, detail="Service initialization failed")
