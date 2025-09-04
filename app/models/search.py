"""
Search-related Pydantic models for the AI Student Support Service.
"""
from typing import List
from pydantic import BaseModel, Field, ConfigDict

from app.models.chat import DocumentContext


class SearchRequest(BaseModel):
    """Request model for search endpoint."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "Business Analysis certification requirements",
                "n_results": 5
            }
        }
    )
    
    query: str = Field(..., description="Search query text")
    n_results: int = Field(default=5, description="Number of results to return", ge=1, le=20)


class SearchData(BaseModel):
    """Search response data model."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "Business Analysis certification requirements",
                "results_count": 3,
                "documents": [
                    {
                        "document_id": "doc_123",
                        "title": "Certification Requirements",
                        "content": "To obtain Business Analysis certification...",
                        "similarity_score": 0.92,
                        "source": "certification_guide.pdf"
                    }
                ]
            }
        }
    )
    
    query: str = Field(..., description="Original search query")
    results_count: int = Field(..., description="Number of documents found")
    documents: List[DocumentContext] = Field(..., description="List of relevant documents")


class SearchResponse(BaseModel):
    """Response model for search endpoint."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Search completed successfully",
                "data": {
                    "query": "Business Analysis certification requirements",
                    "results_count": 3,
                    "documents": [
                        {
                            "document_id": "doc_123",
                            "title": "Certification Requirements",
                            "content": "To obtain Business Analysis certification...",
                            "similarity_score": 0.92,
                            "source": "certification_guide.pdf"
                        }
                    ]
                }
            }
        }
    )
    
    success: bool = Field(True, description="Always true for success responses")
    message: str = Field(..., description="Success message")
    data: SearchData = Field(..., description="Search results data")
