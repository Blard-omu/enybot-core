"""
Health check API endpoints for the AI Student Support Service.
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from app.models.health import HealthResponse, HealthData
from app.utils.logger import get_logger
from app.utils.service_manager import get_global_services

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Comprehensive health check for all services."""
    try:
        ai_service, rag_service, chroma_service = get_global_services()
        
        health_status = {
            "overall_status": "healthy",
            "timestamp": None,
            "services": {}
        }
        
        # Check AI service health
        if ai_service and hasattr(ai_service, 'get_status'):
            try:
                ai_status = ai_service.get_status()
                health_status["services"]["ai_service"] = ai_status
                if ai_status.get("status") != "available":
                    health_status["overall_status"] = "degraded"
            except Exception as e:
                health_status["services"]["ai_service"] = {"status": "error", "error": str(e)}
                health_status["overall_status"] = "unhealthy"
        
        # Check RAG service health
        if rag_service and hasattr(rag_service, 'get_status'):
            try:
                rag_status = rag_service.get_status()
                health_status["services"]["rag_service"] = rag_status
                if rag_status.get("status") != "available":
                    health_status["overall_status"] = "degraded"
            except Exception as e:
                health_status["services"]["rag_service"] = {"status": "error", "error": str(e)}
                health_status["overall_status"] = "unhealthy"
        
        # Check ChromaDB service health
        if chroma_service and hasattr(chroma_service, 'get_status'):
            try:
                chroma_status = chroma_service.get_status()
                health_status["services"]["chroma_service"] = chroma_status
                if chroma_status.get("status") != "available":
                    health_status["overall_status"] = "degraded"
            except Exception as e:
                health_status["services"]["chroma_service"] = {"status": "error", "error": str(e)}
                health_status["overall_status"] = "unhealthy"
        
        # Build response data
        response_data = HealthData(
            status=health_status["overall_status"],
            services=health_status["services"],
            timestamp=health_status["timestamp"],
            version="2.0.0"
        )
        
        # Build standardized response
        response = HealthResponse(
            success=True,
            message="Health check completed successfully",
            data=response_data
        )
        
        logger.info(f"Health check completed - overall status: {health_status['overall_status']}")
        return response
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")
