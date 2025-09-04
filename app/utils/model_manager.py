"""
Model management utility for embedding models.
"""
import os
import asyncio
from typing import Optional, Dict, Any
from sentence_transformers import SentenceTransformer
from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ModelManager:
    """Manages embedding model downloads, caching, and availability."""
    
    def __init__(self):
        """Initialize the model manager."""
        self.settings = get_settings()
        self.model_cache_dir = "./model_cache"
        self.hf_cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        
        # Ensure cache directory exists
        os.makedirs(self.model_cache_dir, exist_ok=True)
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get comprehensive model status information."""
        try:
            model_name = self.settings.embedding_model
            local_cache_path = os.path.join(self.model_cache_dir, model_name.replace("/", "_"))
            hf_cache_path = os.path.join(self.hf_cache_dir, "models--" + model_name.replace("/", "_"))
            
            # Check local cache
            local_available = os.path.exists(local_cache_path)
            hf_available = os.path.exists(hf_cache_path)
            
            # Try to load model
            model_loaded = False
            model_error = None
            try:
                if local_available or hf_available:
                    model = SentenceTransformer(model_name, cache_folder=self.model_cache_dir)
                    model_loaded = True
                    del model  # Clean up
            except Exception as e:
                model_error = str(e)
            
            return {
                "model_name": model_name,
                "local_cache_available": local_available,
                "huggingface_cache_available": hf_available,
                "model_loadable": model_loaded,
                "model_error": model_error,
                "cache_directories": {
                    "local": os.path.abspath(self.model_cache_dir),
                    "huggingface": os.path.abspath(self.hf_cache_dir)
                },
                "status": "available" if model_loaded else "unavailable"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def ensure_model_available(self, force_download: bool = False) -> Optional[SentenceTransformer]:
        """Ensure embedding model is available, downloading if necessary."""
        try:
            model_name = self.settings.embedding_model
            
            # Check if model is already available
            if not force_download:
                try:
                    model = SentenceTransformer(model_name, cache_folder=self.model_cache_dir)
                    logger.info(f"Model {model_name} loaded from cache")
                    return model
                except Exception as e:
                    logger.info(f"Model not in cache: {e}")
            
            # Download the model
            logger.info(f"Downloading model: {model_name}")
            logger.info("This may take several minutes on first run...")
            
            # Download with progress tracking
            model = SentenceTransformer(
                model_name,
                cache_folder=self.model_cache_dir
            )
            
            logger.info(f"Model {model_name} downloaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to ensure model availability: {e}")
            return None
    
    def cleanup_old_models(self, keep_recent: int = 2) -> Dict[str, Any]:
        """Clean up old model versions to save disk space."""
        try:
            cleaned_models = []
            total_space_saved = 0
            
            # List all cached models
            if os.path.exists(self.model_cache_dir):
                for item in os.listdir(self.model_cache_dir):
                    item_path = os.path.join(self.model_cache_dir, item)
                    if os.path.isdir(item_path):
                        # Get directory size
                        size = self._get_directory_size(item_path)
                        cleaned_models.append({
                            "name": item,
                            "size_mb": round(size / (1024 * 1024), 2),
                            "path": item_path
                        })
            
            # Sort by modification time (newest first)
            cleaned_models.sort(key=lambda x: os.path.getmtime(x["path"]), reverse=True)
            
            # Remove old models (keep the most recent ones)
            for model_info in cleaned_models[keep_recent:]:
                try:
                    import shutil
                    shutil.rmtree(model_info["path"])
                    total_space_saved += model_info["size_mb"]
                    logger.info(f"Cleaned up old model: {model_info['name']} ({model_info['size_mb']} MB)")
                except Exception as e:
                    logger.warning(f"Failed to clean up model {model_info['name']}: {e}")
            
            return {
                "status": "success",
                "models_cleaned": len(cleaned_models) - keep_recent,
                "space_saved_mb": round(total_space_saved, 2),
                "models_kept": keep_recent,
                "total_models_found": len(cleaned_models)
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup models: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _get_directory_size(self, path: str) -> int:
        """Calculate directory size in bytes."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception:
            pass
        return total_size
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information for model cache."""
        try:
            if not os.path.exists(self.model_cache_dir):
                return {
                    "cache_directory": self.model_cache_dir,
                    "exists": False,
                    "size_mb": 0,
                    "free_space_mb": 0
                }
            
            # Get cache directory size
            cache_size = self._get_directory_size(self.model_cache_dir)
            
            # Get free disk space
            import shutil
            total, used, free = shutil.disk_usage(self.model_cache_dir)
            
            return {
                "cache_directory": self.model_cache_dir,
                "exists": True,
                "cache_size_mb": round(cache_size / (1024 * 1024), 2),
                "free_space_mb": round(free / (1024 * 1024), 2),
                "total_space_mb": round(total / (1024 * 1024), 2),
                "used_space_mb": round(used / (1024 * 1024), 2)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check of the model system."""
        try:
            # Get model status
            model_status = self.get_model_status()
            
            # Get disk usage
            disk_usage = self.get_disk_usage()
            
            # Try to load model
            model_test = await self.ensure_model_available()
            model_working = model_test is not None
            
            if model_test:
                del model_test  # Clean up
            
            return {
                "status": "healthy" if model_working else "degraded",
                "model_status": model_status,
                "disk_usage": disk_usage,
                "model_working": model_working,
                "recommendations": self._get_recommendations(model_status, disk_usage, model_working)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def _get_recommendations(self, model_status: Dict, disk_usage: Dict, model_working: bool) -> list:
        """Get recommendations based on system status."""
        recommendations = []
        
        if not model_working:
            recommendations.append("Model is not working - check internet connection and model configuration")
        
        if disk_usage.get("free_space_mb", 0) < 1000:  # Less than 1GB free
            recommendations.append("Low disk space - consider cleaning up old models")
        
        if not model_status.get("local_cache_available") and not model_status.get("huggingface_cache_available"):
            recommendations.append("No cached models found - first run will download models")
        
        if model_status.get("model_error"):
            recommendations.append(f"Model loading error: {model_status['model_error']}")
        
        if not recommendations:
            recommendations.append("System is healthy - no action needed")
        
        return recommendations
