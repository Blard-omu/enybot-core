"""
Enhanced DeepSeek AI service for the AI Student Support Service.
Provides LLM operations using multiple DeepSeek API keys with load balancing and fallback.
"""
import asyncio
import random
import time
import requests
from typing import Dict, Any, Optional, List
from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class DeepSeekModelConfig:
    """Configuration for a single DeepSeek model instance."""
    
    def __init__(self, name: str, api_key: str, api_url: str, model: str, priority: int):
        self.name = name
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.priority = priority
        self.last_used = 0
        self.error_count = 0
        self.rate_limit_reset = 0
        self.is_available = True
    
    def mark_used(self):
        """Mark this model as used."""
        self.last_used = time.time()
    
    def mark_error(self, is_rate_limit: bool = False):
        """Mark this model as having an error."""
        self.error_count += 1
        if is_rate_limit:
            # Rate limit typically resets in 1 minute
            self.rate_limit_reset = time.time() + 60
            self.is_available = False
        elif self.error_count >= 3:
            # Mark as unavailable after 3 consecutive errors
            self.is_available = False
    
    def reset_errors(self):
        """Reset error count and availability."""
        self.error_count = 0
        self.is_available = True
    
    def can_use(self) -> bool:
        """Check if this model can be used."""
        if not self.is_available:
            # Check if rate limit has reset
            if time.time() > self.rate_limit_reset:
                self.reset_errors()
            return self.is_available
        return True


class EnhancedDeepSeekService:
    """Enhanced DeepSeek service with multiple API keys, load balancing, and fallback."""
    
    def __init__(self) -> None:
        """Initialize enhanced DeepSeek service with multiple API key configurations."""
        self.models: List[DeepSeekModelConfig] = []
        self._available = False
        self._initialize_models()
        
        # Set as available if models are configured (no API testing to save quota)
        if self.models:
            self._available = True
            logger.info(f"DeepSeek service initialized with {len(self.models)} models")
    
    def _initialize_models(self) -> None:
        """Initialize available DeepSeek models from settings."""
        available_models = settings.get_available_models()
        
        if not available_models:
            logger.error("No DeepSeek models configured")
            return
        
        for model_config in available_models:
            model = DeepSeekModelConfig(
                name=model_config["name"],
                api_key=model_config["api_key"],
                api_url=model_config["api_url"],
                model=model_config["model"],
                priority=model_config["priority"]
            )
            self.models.append(model)
            logger.info(f"Initialized DeepSeek model: {model.name}")
        
        # Sort by priority
        self.models.sort(key=lambda x: x.priority)
    
    def is_available(self) -> bool:
        """Check if any DeepSeek service is available."""
        return self._available and any(model.can_use() for model in self.models)
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status for all DeepSeek models."""
        model_statuses = {}
        for model in self.models:
            model_statuses[model.name] = {
                "status": "available" if model.can_use() else "unavailable",
                "model": model.model,
                "api_url": model.api_url,
                "api_key_configured": bool(model.api_key),
                "error_count": model.error_count,
                "last_used": model.last_used,
                "rate_limit_reset": model.rate_limit_reset
            }
        
        return {
            "overall_status": "available" if self._available else "unavailable",
            "available_models": len([m for m in self.models if m.can_use()]),
            "total_models": len(self.models),
            "models": model_statuses
        }
    
    def _select_model(self, exclude_attempted: set = set()) -> Optional[DeepSeekModelConfig]:
        """Select the best available DeepSeek model using load balancing and priority."""
        available_models = [m for m in self.models if m.can_use() and m.name not in exclude_attempted]
        
        if not available_models:
            return None
        
        if settings.enable_load_balancing and len(available_models) > 1:
            # Load balancing: select random model from available ones
            return random.choice(available_models)
        else:
            # Priority-based: select first available model
            return available_models[0]
    
    async def _make_request(self, model: DeepSeekModelConfig, messages: List[Dict[str, str]], 
                           max_tokens: int, temperature: float) -> str:
        """Make API request to a specific DeepSeek model."""
        try:
            headers = {
                "Authorization": f"Bearer {model.api_key}",
                "Content-Type": "application/json",
            }
            
            data = {
                "model": model.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            logger.info(f"Sending request to DeepSeek {model.name}")
            
            response = requests.post(
                model.api_url, 
                json=data, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code == 429:  # Rate limit
                logger.warning(f"Rate limit hit for DeepSeek {model.name}")
                model.mark_error(is_rate_limit=True)
                available_count = len([m for m in self.models if m.can_use()])
                logger.info(f"DeepSeek {model.name} rate limited. {available_count} models still available")
                raise RuntimeError(f"Rate limit exceeded for DeepSeek {model.name}")
            
            response.raise_for_status()
            result = response.json()
            
            # Extract response content
            if (result.get("choices") and 
                result["choices"][0].get("message") and 
                result["choices"][0]["message"].get("content")):
                
                content = result["choices"][0]["message"]["content"]
                model.mark_used()
                model.reset_errors()
                logger.info(f"Response received from DeepSeek {model.name}: {len(content)} characters")
                return content.strip()
            else:
                logger.error(f"Invalid response structure from DeepSeek {model.name}")
                raise RuntimeError(f"Invalid response structure from DeepSeek {model.name}")
                
        except requests.RequestException as e:
            logger.error(f"API request failed for DeepSeek {model.name}: {e}")
            model.mark_error()
            raise RuntimeError(f"API request failed for DeepSeek {model.name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error with DeepSeek {model.name}: {e}")
            model.mark_error()
            raise RuntimeError(f"Service error with DeepSeek {model.name}: {e}")
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Generate response using available DeepSeek models with fallback."""
        if not self.is_available():
            raise RuntimeError("No DeepSeek services are available")
        
        # Prepare messages
        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.extend(messages)
        
        # Track which models we've already tried
        attempted_models = set()
        
        # Try each available model with retries
        for attempt in range(settings.max_retries):
            # Get next available model (excluding already attempted ones)
            model = self._select_model(exclude_attempted=attempted_models)
            if not model:
                raise RuntimeError("No available DeepSeek models")
            
            # Mark this model as attempted
            attempted_models.add(model.name)
            
            try:
                return await self._make_request(model, api_messages, max_tokens, temperature)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed with DeepSeek {model.name}: {e}")
                if attempt < settings.max_retries - 1:
                    # Check if we still have other models to try
                    remaining_models = [m for m in self.models if m.can_use() and m.name not in attempted_models]
                    if not remaining_models:
                        logger.error("No more DeepSeek models available to try")
                        raise RuntimeError("All DeepSeek models are unavailable")
                    
                    await asyncio.sleep(settings.retry_delay)
                    continue
                else:
                    raise RuntimeError(f"All DeepSeek models failed after {settings.max_retries} attempts")
        
        raise RuntimeError("Failed to generate response")
