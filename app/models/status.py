"""
Status models for the AI Student Support Service.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class ServiceStatus(BaseModel):
    """Individual service status model."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "available",
                "error": None
            }
        }
    )

    status: str = Field(..., description="Service status (available/unavailable/error)")
    error: Optional[str] = Field(None, description="Error message if status is error")


class AIServiceStatus(ServiceStatus):
    """AI service specific status model."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "available",
                "error": None,
                "deepseek_available": True,
                "rag_service_available": True,
                "api_key_configured": True
            }
        }
    )

    deepseek_available: bool = Field(..., description="Whether DeepSeek API is accessible")
    rag_service_available: bool = Field(..., description="Whether RAG service is available")
    api_key_configured: bool = Field(..., description="Whether DeepSeek API key is configured")


class ChromaServiceStatus(ServiceStatus):
    """ChromaDB service specific status model."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "available",
                "error": None,
                "initialized": True,
                "client_available": True,
                "embedding_model_status": "available",
                "embedding_model_name": "all-MiniLM-L6-v2",
                "collection_available": True
            }
        }
    )

    initialized: bool = Field(..., description="Whether ChromaDB service is initialized")
    client_available: bool = Field(..., description="Whether ChromaDB client is available")
    embedding_model_status: str = Field(..., description="Status of embedding model")
    embedding_model_name: str = Field(..., description="Name of embedding model being used")
    collection_available: bool = Field(..., description="Whether collection is available")


class ServicesStatusData(BaseModel):
    """Services status data model for API responses."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "services": {
                    "ai_service": {"status": "available", "model": "deepseek"},
                    "rag_service": {"status": "available", "context_window": 4096},
                    "chroma_service": {"status": "available", "document_count": 150}
                }
            }
        }
    )
    
    services: Dict[str, Any] = Field(..., description="Status of all services")


class ServicesStatusResponse(BaseModel):
    """Response model for services status endpoint."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Services status retrieved successfully",
                "data": {
                    "services": {
                        "ai_service": {"status": "available", "model": "deepseek"},
                        "rag_service": {"status": "available", "context_window": 4096},
                        "chroma_service": {"status": "available", "document_count": 150}
                    }
                }
            }
        }
    )
    
    success: bool = Field(True, description="Always true for success responses")
    message: str = Field(..., description="Success message")
    data: ServicesStatusData = Field(..., description="Services status information")


class LegacyServicesStatusResponse(BaseModel):
    """Legacy services status response model (for internal use)."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "services": {
                    "ai_service": {
                        "status": "available",
                        "error": None,
                        "deepseek_available": True,
                        "rag_service_available": True,
                        "api_key_configured": True
                    },
                    "rag_service": {
                        "status": "available",
                        "error": None
                    },
                    "chroma_service": {
                        "status": "available",
                        "error": None,
                        "initialized": True,
                        "client_available": True,
                        "embedding_model_status": "available",
                        "embedding_model_name": "all-MiniLM-L6-v2",
                        "collection_available": True
                    }
                },
                "timestamp": 1756914636.867542
            }
        }
    )

    status: str = Field(..., description="Overall operation status")
    services: Dict[str, Any] = Field(..., description="Status of all services")
    timestamp: Optional[float] = Field(None, description="Timestamp of status check")
