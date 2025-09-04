"""
Chat API endpoints for the AI Student Support Service.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from app.models.chat import ChatRequest, ChatResponse, ServicesStatusResponse, ChatData, ServicesStatusData
from app.utils.logger import get_logger
from app.utils.service_manager import get_global_services

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest) -> ChatResponse:
    """Chat with AI using simplified single-call RAG-enhanced responses."""
    try:
        ai_service, _ , chroma_service = get_global_services()
        
        # Check service availability
        if not ai_service or not ai_service.is_available():
            raise HTTPException(status_code=503, detail="AI service not available")
        
        if not chroma_service or not chroma_service.is_available():
            raise HTTPException(status_code=503, detail="Knowledge base not available")
        
        # Use the main chat method
        result = await ai_service.chat_with_ai(
            user_message=request.message,
            chat_history=request.chat_history
        )
        
        # Validate result
        if not result:
            raise HTTPException(status_code=500, detail="AI service returned no response")
        
        # Extract values from simplified response
        answer = result.get("response", "Sorry, I couldn't generate a response.")
        confidence = result.get("confidence", 0.0)
        escalated = result.get("escalated", False)
        escalation_reason = result.get("escalation_reason")
        escalation_message = result.get("escalation_message")
        message_type = result.get("message_type", "other")
        llm_used = result.get("llm_used", "unknown")
        rag_documents = result.get("rag_documents", [])
        rag_scores = result.get("rag_scores", [])
        
        # Build response data
        response_data = ChatData(
            response=answer,
            confidence_score=confidence,
            escalated=escalated,
            escalation_reason=escalation_reason,
            context_used=[f"Document {i+1}" for i in range(len(rag_documents))],
            metadata={
                "llm_used": llm_used,
                "message_type": message_type,
                "rag_documents_count": len(rag_documents),
                "rag_scores": rag_scores,
                "rag_documents": rag_documents,
                "escalation_message": escalation_message
            }
        )
        
        # Build standardized response
        response = ChatResponse(
            success=True,
            message="Chat response generated successfully",
            data=response_data
        )
        
        # Log escalation if it occurred
        if escalated:
            logger.info(f"Query escalated: {escalation_reason}")
            logger.info(f"Escalation data generated for backend processing")
        
        logger.info(f"Chat response generated successfully (confidence: {confidence:.2f}, escalated: {escalated}, type: {message_type})")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status", response_model=ServicesStatusResponse)
async def get_services_status() -> ServicesStatusResponse:
    """Get comprehensive status of all services."""
    try:
        ai_service, rag_service, chroma_service = get_global_services()
        
        services_status = {}
        
        # Get AI service status
        if ai_service and hasattr(ai_service, 'get_status'):
            try:
                services_status["ai_service"] = ai_service.get_status()
            except Exception as e:
                services_status["ai_service"] = {"status": "error", "error": str(e)}
        
        # Get RAG service status
        if rag_service and hasattr(rag_service, 'get_status'):
            try:
                services_status["rag_service"] = rag_service.get_status()
            except Exception as e:
                services_status["rag_service"] = {"status": "error", "error": str(e)}
        
        # Get ChromaDB service status
        if chroma_service and hasattr(chroma_service, 'get_status'):
            try:
                services_status["chroma_service"] = chroma_service.get_status()
            except Exception as e:
                services_status["chroma_service"] = {"status": "error", "error": str(e)}
        
        # Build response data
        status_data = ServicesStatusData(services=services_status)
        
        # Build standardized response
        response = ServicesStatusResponse(
            success=True,
            message="Services status retrieved successfully",
            data=status_data
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting services status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve services status")
