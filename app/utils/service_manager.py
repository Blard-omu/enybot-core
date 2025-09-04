"""
Global service manager for the AI Student Support Service.
This module manages global service instances to avoid circular imports.
"""
from typing import Optional, Tuple
from app.utils.logger import get_logger

# Import service types for type hints
from app.services.ai_service import AIService
from app.services.rag_service import RAGService
from app.services.chroma_service import ChromaService

logger = get_logger(__name__)

# Global service instances with proper types
_ai_service: Optional[AIService] = None
_rag_service: Optional[RAGService] = None
_chroma_service: Optional[ChromaService] = None


def set_global_services(ai_service: AIService, rag_service: RAGService, chroma_service: ChromaService) -> None:
    """Set the global service instances."""
    global _ai_service, _rag_service, _chroma_service
    _ai_service = ai_service
    _rag_service = rag_service
    _chroma_service = chroma_service
    logger.info("Global services set successfully")


def get_global_services() -> Tuple[AIService, RAGService, ChromaService]:
    """Get the global service instances."""
    return _ai_service, _rag_service, _chroma_service


def is_services_initialized() -> bool:
    """Check if all services are initialized."""
    return all([_ai_service, _rag_service, _chroma_service])


def get_ai_service() -> Optional[AIService]:
    """Get the AI service instance."""
    return _ai_service


def get_rag_service() -> Optional[RAGService]:
    """Get the RAG service instance."""
    return _rag_service


def get_chroma_service() -> Optional[ChromaService]:
    """Get the ChromaDB service instance."""
    return _chroma_service


def is_ai_service_available() -> bool:
    """Check if AI service is available and ready."""
    return _ai_service is not None and hasattr(_ai_service, 'is_available') and _ai_service.is_available()


def is_rag_service_available() -> bool:
    """Check if RAG service is available and ready."""
    return _rag_service is not None and hasattr(_rag_service, 'is_available') and _rag_service.is_available()


def is_chroma_service_available() -> bool:
    """Check if ChromaDB service is available and ready."""
    return _chroma_service is not None and hasattr(_chroma_service, 'is_available') and _chroma_service.is_available()
