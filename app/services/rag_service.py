"""
RAG service for the AI Student Support Service.
Handles document retrieval and context building for AI responses.
"""
from typing import List, Dict, Any, Optional
from app.services.chroma_service import ChromaService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RAGService:
    """RAG service for document retrieval and context building."""
    
    def __init__(self) -> None:
        """Initialize RAG service."""
        self.chroma_service = None  # Will be set later
        self._ai_service = None
    
    def set_chroma_service(self, chroma_service: ChromaService) -> None:
        """Set ChromaDB service reference."""
        self.chroma_service = chroma_service
    
    def set_ai_service(self, ai_service: Any) -> None:
        """Set AI service reference to avoid circular dependency."""
        self._ai_service = ai_service
    
    def is_available(self) -> bool:
        """Check if RAG service is available."""
        return self.chroma_service is not None and self.chroma_service.is_available()
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status."""
        return {
            "status": "available" if self.is_available() else "unavailable",
            "chroma_service_available": self.chroma_service is not None and self.chroma_service.is_available(),
            "error": None if self.is_available() else "ChromaDB service not available"
        }
    
    async def retrieve_relevant_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query with metadata."""
        try:
            if not self.chroma_service or not self.chroma_service.is_available():
                logger.warning("ChromaDB service not available")
                return []
            
            # Search for relevant documents
            results = await self.chroma_service.search_documents(query, n_results)
            
            if not results:
                logger.info("No relevant documents found")
                return []
            
            # Format results - DocumentContext objects have attributes, not dict methods
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "document_id": getattr(doc, "document_id", "unknown"),
                    "content": getattr(doc, "content", ""),
                    "title": getattr(doc, "title", "Unknown Document"),
                    "source": getattr(doc, "source", "Unknown Source"),
                    "similarity_score": getattr(doc, "similarity_score", 0.0),
                    "metadata": {
                        "title": getattr(doc, "title", "Unknown Document"),
                        "source": getattr(doc, "source", "Unknown Source"),
                        "type": "document"
                    }
                })
            
            logger.info(f"Retrieved {len(formatted_results)} relevant documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error retrieving relevant documents: {e}")
            return []
    
    def build_context_from_documents(self, documents: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents."""
        if not documents:
            return ""
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            title = doc.get("title", "Unknown Document")
            content = doc.get("content", "")
            source = doc.get("source", "Unknown Source")
            score = doc.get("similarity_score", 0.0)
            
            context_parts.append(f"Document {i}: {title}")
            context_parts.append(f"Source: {source}")
            context_parts.append(f"Relevance Score: {score:.3f}")
            context_parts.append(f"Content: {content}")
            context_parts.append("---")
        
        return "\n".join(context_parts)

