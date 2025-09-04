#!/usr/bin/env python3
"""
Model caching script for Docker builds.
Downloads and caches required models if they don't exist.
"""
import os
import sys
from pathlib import Path

def check_model_exists(model_path: str) -> bool:
    """Check if a model already exists in the cache."""
    cache_dir = Path(model_path)
    return cache_dir.exists() and cache_dir.is_dir()

def cache_sentence_transformers():
    """Cache sentence transformers model if it doesn't exist."""
    try:
        from sentence_transformers import SentenceTransformer
        
        model_name = "all-MiniLM-L6-v2"
        cache_path = f"./model_cache/models--sentence-transformers--{model_name.replace('/', '--')}"
        
        if check_model_exists(cache_path):
            print(f"Sentence Transformers model already cached: {model_name}")
            return True
        
        print(f"Downloading Sentence Transformers model: {model_name}")
        model = SentenceTransformer(model_name)
        
        test_embedding = model.encode(["test sentence"])
        print(f"Sentence Transformers model cached successfully: {model_name}")
        print(f"Test embedding shape: {test_embedding.shape}")
        
        del model
        return True
        
    except Exception as e:
        print(f"Failed to cache Sentence Transformers model: {e}")
        return False

def cache_onnx_model():
    """Cache ONNX model if it doesn't exist."""
    try:
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
        
        model_name = "ONNXMiniLM_L6_V2"
        cache_path = "./model_cache/onnx_models"
        
        if check_model_exists(cache_path):
            print(f"ONNX model already cached: {model_name}")
            return True
        
        print(f"Downloading ONNX model: {model_name}")
        ef = ONNXMiniLM_L6_V2()
        
        test_embedding = ef(["warmup"])
        print(f"ONNX model cached successfully: {model_name}")
        print(f"Test embedding shape: {test_embedding.shape}")
        
        del ef
        return True
        
    except Exception as e:
        print(f"Failed to cache ONNX model: {e}")
        return False

def main():
    """Main function to cache all required models."""
    print("Starting model caching process...")
    
    os.makedirs("./model_cache", exist_ok=True)
    os.makedirs("./model_cache/onnx_models", exist_ok=True)
    
    success_count = 0
    total_models = 2
    
    if cache_sentence_transformers():
        success_count += 1
    
    if cache_onnx_model():
        success_count += 1
    
    print(f"Model caching complete: {success_count}/{total_models} models cached")
    
    if success_count == total_models:
        print("All models cached successfully!")
        sys.exit(0)
    else:
        print("Some models failed to cache, but service will continue with fallbacks")
        sys.exit(0)

if __name__ == "__main__":
    main()
