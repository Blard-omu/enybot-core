"""
AI service for the AI Student Support Service.
Uses DeepSeek AI for LLM operations with intelligent escalation.
"""
from typing import Dict, Any, Optional, List
from app.config.settings import get_settings
from app.services.rag_service import RAGService
from app.services.deepseek_service import EnhancedDeepSeekService
from app.prompts.ai_prompts import get_main_system_prompt
from app.utils.logger import get_logger
import json

logger = get_logger(__name__)
settings = get_settings()


class AIService:
    """AI service for LLM operations using DeepSeek with intelligent escalation."""
    
    def __init__(self) -> None:
        """Initialize AI service with enhanced DeepSeek and RAG services."""
        self.enhanced_deepseek_service = EnhancedDeepSeekService()
        self.rag_service = None  # Will be set later
        
        logger.info(f"AI Service initialized - Enhanced DeepSeek: {self.enhanced_deepseek_service.is_available()}")
    
    def set_rag_service(self, rag_service: RAGService) -> None:
        """Set RAG service reference."""
        self.rag_service = rag_service
        if self.rag_service:
            self.rag_service.set_ai_service(self)
    
    def is_available(self) -> bool:
        """Check if AI service is available."""
        return self.enhanced_deepseek_service.is_available()
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive service status information."""
        return {
            "status": "available" if self.is_available() else "unavailable",
            "enhanced_deepseek_available": self.enhanced_deepseek_service.is_available(),
            "rag_service_available": self.rag_service is not None and self.rag_service.is_available(),
            "models_configured": len(settings.get_available_models()),
            "error": None if self.is_available() else "Enhanced DeepSeek service not available"
        }
    
    async def chat_with_ai(
        self, 
        user_message: str, 
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Process user query in single AI call with RAG integration. Returns response dict."""
        try:
            if not self.is_available():
                return {
                    "response": "I'm currently experiencing technical difficulties. Please try again later.",
                    "confidence": 0.0,
                    "escalated": True,
                    "escalation_reason": "AI service unavailable",
                    "rag_documents": [],
                    "rag_scores": [],
                    "llm_used": "none"
                }
            
            # Get RAG results first
            if not self.rag_service:
                return {
                    "response": "Knowledge base service not available. Please try again later.",
                    "confidence": 0.0,
                    "escalated": True,
                    "escalation_reason": "RAG service unavailable",
                    "rag_documents": [],
                    "rag_scores": [],
                    "llm_used": "none"
                }
            
            # Get RAG results
            rag_results = await self.rag_service.retrieve_relevant_documents(user_message, n_results=5)
            
            # Prepare context for AI
            rag_context = ""
            rag_scores = []
            rag_documents = []
            
            if rag_results:
                rag_context = self.rag_service.build_context_from_documents(rag_results)
                rag_scores = [doc.get("similarity_score", 0.0) for doc in rag_results]
                rag_documents = [doc.get("content", "")[:200] + "..." for doc in rag_results]
            
            # Get system prompt from prompts file
            system_prompt = get_main_system_prompt(rag_context if rag_context else "No relevant documents found")
            
            # Prepare messages for AI call, including chat history
            messages = []
            if chat_history:
                # Add chat history in the correct format
                messages.extend(chat_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Make single AI call with chat history
            response = await self.enhanced_deepseek_service.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=500,
                temperature=0.7
            )
            
            # Parse AI response
            try:
                ai_result = json.loads(response.strip())
                
                # Validate required fields
                required_fields = ["response", "confidence", "escalated", "escalation_reason", "message_type", "escalation_message"]
                for field in required_fields:
                    if field not in ai_result:
                        ai_result[field] = None
                
                # Add RAG data
                ai_result["rag_documents"] = rag_documents
                ai_result["rag_scores"] = rag_scores
                ai_result["llm_used"] = "deepseek"
                
                return ai_result
                
            except json.JSONDecodeError:
                # Fallback if AI doesn't return valid JSON
                return {
                    "response": response.strip(),
                    "confidence": 0.7,
                    "escalated": False,
                    "escalation_reason": None,
                    "message_type": "other",
                    "escalation_message": None,
                    "rag_documents": rag_documents,
                    "rag_scores": rag_scores,
                    "llm_used": "deepseek"
                }
                
        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            return {
                "response": "I encountered an error processing your request. Please try again.",
                "confidence": 0.0,
                "escalated": True,
                "escalation_reason": f"Processing error: {str(e)}",
                "rag_documents": [],
                "rag_scores": [],
                "llm_used": "none"
            }
