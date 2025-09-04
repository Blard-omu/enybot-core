"""
Chat-related Pydantic models for the AI Student Support Service.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.status import ServicesStatusData, ServicesStatusResponse


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "What are the admission requirements for the Business Analysis program?",
                "chat_history": [
                    {"role": "user", "content": "Hello, I'm interested in your programs"},
                    {"role": "assistant", "content": "Hello! I'd be happy to help you learn about our programs."}
                ]
            }
        }
    )
    
    message: str = Field(..., description="User's message or question")
    chat_history: List[Dict[str, str]] = Field(default=[], description="Previous chat messages")


class ChatData(BaseModel):
    """Chat response data model."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": "The admission requirements for our Business Analysis program include...",
                "confidence_score": 0.85,
                "escalated": False,
                "escalation_reason": None,
                "context_used": ["Document 1", "Document 2"],
                "metadata": {
                    "llm_used": "deepseek",
                    "message_type": "question",
                    "rag_documents_count": 2,
                    "rag_scores": [0.92, 0.87],
                    "rag_documents": ["Business Analysis is the practice of...", "Our program covers..."],
                    "escalation_message": None
                }
            }
        }
    )
    
    response: str = Field(..., description="AI-generated response")
    confidence_score: float = Field(..., description="Confidence score of the response (0.0 to 1.0)")
    escalated: bool = Field(..., description="Whether the query was escalated to human agent")
    escalation_reason: Optional[str] = Field(None, description="Reason for escalation if applicable")
    context_used: List[str] = Field(..., description="Document references used as context")
    metadata: Dict[str, Any] = Field(..., description="Additional response metadata")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Chat response generated successfully",
                "data": {
                    "response": "The admission requirements for our Business Analysis program include...",
                    "confidence_score": 0.85,
                    "escalated": False,
                    "escalation_reason": None,
                    "context_used": ["Document 1", "Document 2"],
                    "metadata": {
                        "llm_used": "deepseek",
                        "message_type": "question",
                        "rag_documents_count": 2,
                        "rag_scores": [0.92, 0.87],
                        "rag_documents": ["Business Analysis is the practice of...", "Our program covers..."],
                        "escalation_message": None
                    }
                }
            }
        }
    )
    
    success: bool = Field(True, description="Always true for success responses")
    message: str = Field(..., description="Success message")
    data: ChatData = Field(..., description="Chat response data")


class DocumentContext(BaseModel):
    """Model for document context in search results."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_id": "doc_123",
                "title": "Business Analysis Fundamentals",
                "content": "Business analysis is the practice of...",
                "similarity_score": 0.92,
                "source": "course_materials.pdf"
            }
        }
    )
    
    document_id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title or name")
    content: str = Field(..., description="Document content or excerpt")
    similarity_score: float = Field(..., description="Similarity score (0.0 to 1.0)")
    source: str = Field(..., description="Document source or filename")
