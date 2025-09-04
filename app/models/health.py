"""
Health check Pydantic models for the AI Student Support Service.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class HealthData(BaseModel):
    """Health check response data model."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "services": {
                    "ai_service": {"status": "available"},
                    "rag_service": {"status": "available"},
                    "chroma_service": {"status": "available"}
                },
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "2.0.0"
            }
        }
    )
    
    status: str = Field(..., description="Overall health status (healthy, degraded, unhealthy)")
    services: Dict[str, Any] = Field(..., description="Individual service statuses")
    timestamp: Optional[str] = Field(None, description="Health check timestamp")
    version: str = Field(..., description="Service version")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Health check completed successfully",
                "data": {
                    "status": "healthy",
                    "services": {
                        "ai_service": {"status": "available"},
                        "rag_service": {"status": "available"},
                        "chroma_service": {"status": "available"}
                    },
                    "timestamp": "2024-01-15T10:30:00Z",
                    "version": "2.0.0"
                }
            }
        }
    )
    
    success: bool = Field(True, description="Always true for success responses")
    message: str = Field(..., description="Success message")
    data: HealthData = Field(..., description="Health check data")
