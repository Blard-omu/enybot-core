"""
Configuration settings for the AI Student Support Service.
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # DeepSeek Configuration
    deepseek_api_key: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    deepseek_api_key_2: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY_2")
    deepseek_api_url: str = Field(default="https://openrouter.ai/api/v1/chat/completions", env="DEEPSEEK_API_URL")
    deepseek_model: str = Field(default="deepseek/deepseek-chat-v3.1:free", env="DEEPSEEK_MODEL")
    deepseek_model_2: str = Field(default="deepseek/deepseek-chat-v3.1:free", env="DEEPSEEK_MODEL_2")
    
    # Load Balancing Configuration
    enable_load_balancing: bool = Field(default=True, env="ENABLE_LOAD_BALANCING")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    retry_delay: float = Field(default=1.0, env="RETRY_DELAY")
    
    # Hugging Face Configuration
    huggingface_token: Optional[str] = Field(default=None, env="HUGGINGFACE_TOKEN")  # Added for Hugging Face authentication
    
    # ChromaDB Configuration
    chroma_host: str = Field(default="localhost", env="CHROMA_HOST")
    chroma_port: int = Field(default=8001, env="CHROMA_PORT")
    chroma_persist_directory: str = Field(default="./chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    chroma_collection_name: str = Field(default="business_analysis_school", env="CHROMA_COLLECTION_NAME")
    
    # Embedding Model Configuration
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    similarity_threshold: float = Field(default=0.6, env="SIMILARITY_THRESHOLD")
    
    # Document Chunking Configuration
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    def get_available_models(self) -> List[dict]:
        """Get list of available DeepSeek models with their configurations."""
        models = []
        
        # Primary DeepSeek
        if self.deepseek_api_key:
            models.append({
                "name": "deepseek_primary",
                "api_key": self.deepseek_api_key,
                "api_url": self.deepseek_api_url,
                "model": self.deepseek_model,
                "provider": "deepseek",
                "priority": 1
            })
        
        # Secondary DeepSeek
        if self.deepseek_api_key_2:
            models.append({
                "name": "deepseek_secondary",
                "api_key": self.deepseek_api_key_2,
                "api_url": self.deepseek_api_url,
                "model": self.deepseek_model_2,
                "provider": "deepseek",
                "priority": 2
            })
        
        return models


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

