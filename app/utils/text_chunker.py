"""
Text chunking utility for the AI Student Support Service.
Splits documents into appropriate chunks for better RAG performance.
"""
import re
from typing import List, Dict, Any
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TextChunker:
    """Utility class for chunking text documents."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize text chunker.
        
        Args:
            chunk_size: Target size for each chunk in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            metadata: Original document metadata
            
        Returns:
            List of chunk dictionaries with content and metadata
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking")
            return []
        
        # Clean and normalize text
        cleaned_text = self._clean_text(text)
        
        # Split into sentences first (better semantic boundaries)
        sentences = self._split_into_sentences(cleaned_text)
        
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_data = self._create_chunk_data(
                    current_chunk.strip(), 
                    chunk_id, 
                    metadata,
                    len(chunks)
                )
                chunks.append(chunk_data)
                chunk_id += 1
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0 and chunks:
                    # Get last part of previous chunk for overlap
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + " " + sentence
                else:
                    current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add final chunk if there's content
        if current_chunk.strip():
            chunk_data = self._create_chunk_data(
                current_chunk.strip(), 
                chunk_id, 
                metadata,
                len(chunks)
            )
            chunks.append(chunk_data)
        
        logger.info(f"Chunked text into {len(chunks)} chunks (target size: {self.chunk_size}, overlap: {self.chunk_overlap})")
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with chunking
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', ' ', text)
        
        # Normalize spacing around punctuation
        text = re.sub(r'\s+([\.\,\!\?\;\:])', r'\1', text)
        
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex patterns."""
        # Split on sentence endings followed by space or end of text
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(sentence_pattern, text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # Filter out very short fragments
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _create_chunk_data(self, content: str, chunk_id: int, metadata: Dict[str, Any], chunk_index: int) -> Dict[str, Any]:
        """Create chunk data structure."""
        import uuid
        
        # Create unique ID for this chunk
        chunk_uuid = str(uuid.uuid4())
        
        # Prepare chunk metadata
        chunk_metadata = {
            "type": "chunk",
            "chunk_id": chunk_id,
            "chunk_index": chunk_index,
            "chunk_size": len(content),
            "is_chunk": True
        }
        
        # Merge with original metadata
        if metadata:
            # Remove any conflicting keys
            for key in ["id", "chunk_id", "chunk_index", "chunk_size", "is_chunk"]:
                metadata.pop(key, None)
            chunk_metadata.update(metadata)
        
        return {
            "id": chunk_uuid,
            "content": content,
            "metadata": chunk_metadata
        }
    
    def get_chunk_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about the chunking process."""
        if not chunks:
            return {"total_chunks": 0, "avg_chunk_size": 0, "total_content": 0}
        
        total_content = sum(len(chunk["content"]) for chunk in chunks)
        avg_chunk_size = total_content / len(chunks)
        
        return {
            "total_chunks": len(chunks),
            "avg_chunk_size": round(avg_chunk_size, 2),
            "total_content": total_content,
            "chunk_size_range": {
                "min": min(len(chunk["content"]) for chunk in chunks),
                "max": max(len(chunk["content"]) for chunk in chunks)
            }
        }
