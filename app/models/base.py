"""
Base response models for standardized API responses.
"""
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "message": "An error occurred",
                "error": "Detailed error information",
                "error_code": "VALIDATION_ERROR"
            }
        }
    )
    
    success: bool = Field(False, description="Always false for error responses")
    message: str = Field(..., description="Human-readable error message")
    error: str = Field(..., description="Detailed error information")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
