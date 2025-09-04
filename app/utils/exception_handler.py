"""
Custom exception handler for standardized error responses.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.models.base import ErrorResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with standardized response format."""
    logger.warning(f"Validation error: {exc.errors()}")
    
    error_response = ErrorResponse(
        success=False,
        message="Request validation failed",
        error="Invalid request data provided",
        error_code="VALIDATION_ERROR"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump()
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with standardized response format."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    error_response = ErrorResponse(
        success=False,
        message="Request failed",
        error=str(exc.detail),
        error_code=f"HTTP_{exc.status_code}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with standardized response format."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    error_response = ErrorResponse(
        success=False,
        message="Internal server error",
        error="An unexpected error occurred",
        error_code="INTERNAL_ERROR"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )
