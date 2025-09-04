"""
ChromaDB service for vector database operations and document management.
"""
import os
import hashlib
from typing import List, Dict, Any, Optional
from chromadb import PersistentClient, Collection
from sentence_transformers import SentenceTransformer
from app.config.settings import get_settings
from app.models.chat import DocumentContext
from app.utils.logger import get_logger
from app.utils.text_chunker import TextChunker
import uuid

logger = get_logger(__name__)


class ChromaService:
    """Service for managing ChromaDB operations and document embeddings."""
    
    def __init__(self) -> None:
        """Initialize ChromaDB service with configuration."""
        self.settings = get_settings()
        self.client: Optional[PersistentClient] = None
        self.collection: Optional[Collection] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self.text_chunker = TextChunker(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap
        )
        self._initialize_client()
        self._initialize_collection()
        self._initialize_embedding_model()
    
    def _initialize_client(self) -> None:
        """Initialize ChromaDB client."""
        try:
            # Use persistent directory for ChromaDB
            persist_directory = self.settings.chroma_persist_directory
            
            # Ensure directory exists
            os.makedirs(persist_directory, exist_ok=True)
            
            # Initialize client with persistent storage - using PersistentClient like the working example
            self.client = PersistentClient(path=persist_directory)
            
            logger.info(f"ChromaDB client initialized successfully with persistent directory: {persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise
    
    def _initialize_collection(self) -> None:
        """Initialize or get existing collection."""
        try:
            if not self.client:
                raise RuntimeError("ChromaDB client not initialized")
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.settings.chroma_collection_name,
                metadata={"description": "Business Analysis School Documents"}
            )
            
            logger.info(f"Collection '{self.settings.chroma_collection_name}' initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise
    
    def _initialize_embedding_model(self) -> None:
        """Initialize embedding model."""
        try:
            logger.info(f"Initializing embedding model: {self.settings.embedding_model}")
            self.embedding_model = SentenceTransformer(self.settings.embedding_model, use_auth_token=self.settings.huggingface_token)
            logger.info("Embedding model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if ChromaDB service is available."""
        return (
            self.client is not None and 
            self.collection is not None and 
            self.embedding_model is not None
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status."""
        return {
            "status": "available" if self.is_available() else "unavailable",
            "client_initialized": self.client is not None,
            "collection_initialized": self.collection is not None,
            "embedding_model_initialized": self.embedding_model is not None,
            "collection_name": self.settings.chroma_collection_name,
            "persist_directory": self.settings.chroma_persist_directory
        }
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text."""
        if not self.embedding_model:
            raise RuntimeError("Embedding model not initialized")
        
        return self.embedding_model.encode(text).tolist()
    
    async def add_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add a single document to collection with chunking. Returns original document ID."""
        if not self.collection:
            raise RuntimeError("Collection not initialized")
        
        try:
            # Generate unique ID for the original document
            original_doc_id = str(uuid.uuid4())
            
            # Chunk the content
            chunks = self.text_chunker.chunk_text(content, metadata)
            
            if not chunks:
                logger.warning("No chunks created from document content")
                return original_doc_id
            
            # Prepare batch data for all chunks
            contents = []
            metadatas = []
            embeddings = []
            ids = []
            
            for chunk in chunks:
                chunk_content = chunk["content"]
                chunk_metadata = chunk["metadata"]
                chunk_id = chunk["id"]
                
                # Get embedding for this chunk
                embedding = self.get_embedding(chunk_content)
                
                contents.append(chunk_content)
                metadatas.append(chunk_metadata)
                embeddings.append(embedding)
                ids.append(chunk_id)
            
            # Add all chunks to collection
            self.collection.add(
                documents=contents,
                metadatas=metadatas,
                embeddings=embeddings,
                ids=ids
            )
            
            logger.info(f"Successfully added document with {len(content)} characters as {len(chunks)} chunks")
            return original_doc_id
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            raise
    
    async def add_documents(self, documents_data: List[Dict[str, Any]]) -> bool:
        """Add multiple documents to collection with chunking. Returns True if successful."""
        if not self.collection:
            raise RuntimeError("Collection not initialized")
        
        try:
            if not documents_data:
                logger.warning("No documents provided to add")
                return False
            
            # Prepare batch data for all chunks from all documents
            all_contents = []
            all_metadatas = []
            all_embeddings = []
            all_ids = []
            total_chunks = 0
            
            for doc_data in documents_data:
                content = doc_data.get("content", "")
                metadata = doc_data.get("metadata", {})
                doc_id = doc_data.get("id", str(uuid.uuid4()))
                
                if not content:
                    logger.warning(f"Skipping document {doc_id} with empty content")
                    continue
                
                # Chunk this document
                chunks = self.text_chunker.chunk_text(content, metadata)
                
                if not chunks:
                    logger.warning(f"No chunks created from document {doc_id}")
                    continue
                
                # Add all chunks from this document
                for chunk in chunks:
                    chunk_content = chunk["content"]
                    chunk_metadata = chunk["metadata"]
                    chunk_id = chunk["id"]
                    
                    # Get embedding for this chunk
                    embedding = self.get_embedding(chunk_content)
                    
                    all_contents.append(chunk_content)
                    all_metadatas.append(chunk_metadata)
                    all_embeddings.append(embedding)
                    all_ids.append(chunk_id)
                    total_chunks += 1
            
            if not all_contents:
                logger.warning("No valid chunks to add after processing")
                return False
            
            # Add all chunks to collection in one batch
            self.collection.add(
                documents=all_contents,
                metadatas=all_metadatas,
                embeddings=all_embeddings,
                ids=all_ids
            )
            
            logger.info(f"Successfully added {len(documents_data)} documents as {total_chunks} chunks to collection")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
    
    async def search_documents(self, query: str, n_results: int = 5) -> List[DocumentContext]:
        """Search for relevant documents. Returns list of DocumentContext objects."""
        if not self.collection:
            raise RuntimeError("Collection not initialized")
        
        try:
            # Get query embedding
            query_embedding = self.get_embedding(query)
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            documents = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    doc_context = DocumentContext(
                        document_id=results["ids"][0][i] if results["ids"] and results["ids"][0] else f"doc_{i}",
                        content=doc,
                        title=results["metadatas"][0][i].get("title", "Unknown Document") if results["metadatas"] and results["metadatas"][0] else "Unknown Document",
                        source=results["metadatas"][0][i].get("source", "Unknown Source") if results["metadatas"] and results["metadatas"][0] else "Unknown Source",
                        similarity_score=1.0 - (results["distances"][0][i] if results["distances"] and results["distances"][0] else 0.0)
                    )
                    documents.append(doc_context)
            
            logger.info(f"Found {len(documents)} relevant documents")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            raise
    
    async def get_document_count(self) -> int:
        """Get total document count."""
        if not self.collection:
            return 0
        
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Failed to get document count: {e}")
            return 0
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information."""
        if not self.collection:
            return {"error": "Collection not initialized"}
        
        try:
            count = self.collection.count()
            settings = get_settings()
            
            return {
                "collection_name": self.collection.name,
                "document_count": count,
                "embedding_model": settings.embedding_model,
                "similarity_threshold": settings.similarity_threshold,
                "status": "available"
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"error": str(e)}
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete document by ID. Returns True if successful."""
        if not self.collection:
            return False
        
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Document {doc_id} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    async def clear_collection(self) -> bool:
        """Clear all documents from collection. Returns True if successful."""
        if not self.collection:
            return False
        
        try:
            # Get all document IDs first
            all_docs = self.collection.get()
            
            if all_docs["ids"]:
                # Delete all documents by their IDs
                self.collection.delete(ids=all_docs["ids"])
                logger.info(f"Collection cleared successfully - {len(all_docs['ids'])} documents removed")
            else:
                logger.info("Collection is already empty")
            
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
