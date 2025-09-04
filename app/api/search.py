"""
Search API endpoints for the AI Student Support Service.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from app.models.search import SearchRequest, SearchResponse, SearchData
from app.utils.logger import get_logger
from app.utils.service_manager import get_global_services

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=SearchResponse)
async def search_documents(request: SearchRequest) -> SearchResponse:
    """Search for documents using semantic similarity."""
    try:
        _, _, chroma_service = get_global_services()
        
        if not chroma_service or not chroma_service.is_available():
            raise HTTPException(status_code=503, detail="Knowledge base not available")
        
        # Perform semantic search
        results = await chroma_service.search_documents(
            query=request.query,
            n_results=request.n_results
        )
        
        # Build response data
        response_data = SearchData(
            query=request.query,
            results_count=len(results),
            documents=results
        )
        
        # Build standardized response
        response = SearchResponse(
            success=True,
            message="Search completed successfully",
            data=response_data
        )
        
        logger.info(f"Search completed for query: '{request.query}' - {len(results)} results")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
