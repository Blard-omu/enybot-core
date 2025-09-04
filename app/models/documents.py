"""
Document management Pydantic models for the AI Student Support Service.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class TextDocumentRequest(BaseModel):
    """Request model for adding text documents."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "Business Analysis is the practice of enabling change in an organizational context..."
            }
        }
    )
    
    content: str = Field(..., description="Document text content")


class PDFUploadData(BaseModel):
    """PDF upload response data model."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pdfs_processed": 2,
                "pdfs_failed": 0,
                "total_documents_added": 2
            }
        }
    )
    
    pdfs_processed: int = Field(..., description="Number of PDFs successfully processed")
    pdfs_failed: int = Field(..., description="Number of PDFs that failed processing")
    total_documents_added: int = Field(..., description="Total number of documents added to knowledge base")


class PDFUploadResponse(BaseModel):
    """Response model for PDF upload operations."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Successfully processed 2 PDF documents",
                "data": {
                    "pdfs_processed": 2,
                    "pdfs_failed": 0,
                    "total_documents_added": 2
                }
            }
        }
    )
    
    success: bool = Field(True, description="Always true for success responses")
    message: str = Field(..., description="Success message")
    data: PDFUploadData = Field(..., description="PDF upload results")


class TextDocumentData(BaseModel):
    """Text document response data model."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_id": "doc_123",
                "content_length": 1250,
                "message": "Document processed successfully"
            }
        }
    )
    
    document_id: str = Field(..., description="Unique document identifier")
    content_length: int = Field(..., description="Length of document content in characters")
    message: str = Field(..., description="Processing status message")


class TextDocumentResponse(BaseModel):
    """Response model for text document operations."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Text document added successfully",
                "data": {
                    "document_id": "doc_123",
                    "title": "Business Analysis Fundamentals",
                    "content_length": 1250,
                    "source": "course_materials",
                    "tags": ["fundamentals", "business-analysis"]
                }
            }
        }
    )
    
    success: bool = Field(True, description="Always true for success responses")
    message: str = Field(..., description="Success message")
    data: TextDocumentData = Field(..., description="Text document information")


class KnowledgeBaseInfo(BaseModel):
    """Knowledge base information data model."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "collection_name": "business_analysis_kb",
                "document_count": 150,
                "embedding_model": "all-MiniLM-L6-v2",
                "similarity_threshold": 0.7,
                "status": "available"
            }
        }
    )
    
    collection_name: str = Field(..., description="Name of the ChromaDB collection")
    document_count: int = Field(..., description="Total number of documents in the collection")
    embedding_model: str = Field(..., description="Name of the embedding model being used")
    similarity_threshold: float = Field(..., description="Similarity threshold for document retrieval")
    status: str = Field(..., description="Status of the knowledge base")


class GetDocumentsData(BaseModel):
    """Get documents response data model."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "knowledge_base_info": {
                    "collection_name": "business_analysis_kb",
                    "document_count": 150,
                    "embedding_model": "all-MiniLM-L6-v2",
                    "similarity_threshold": 0.7,
                    "status": "available"
                },
                "document_count": 150
            }
        }
    )
    
    knowledge_base_info: KnowledgeBaseInfo = Field(..., description="Knowledge base information")
    document_count: int = Field(..., description="Total number of documents")


class GetDocumentsResponse(BaseModel):
    """Response model for getting documents information."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Knowledge base information retrieved successfully",
                "data": {
                    "knowledge_base_info": {
                        "collection_name": "business_analysis_kb",
                        "document_count": 150,
                        "embedding_model": "all-MiniLM-L6-v2",
                        "similarity_threshold": 0.7,
                        "status": "available"
                    },
                    "document_count": 150
                }
            }
        }
    )
    
    success: bool = Field(True, description="Always true for success responses")
    message: str = Field(..., description="Success message")
    data: GetDocumentsData = Field(..., description="Knowledge base information")


class DeleteDocumentResponse(BaseModel):
    """Response model for document deletion operations."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Document 123 deleted successfully",
                "data": None
            }
        }
    )
    
    success: bool = Field(True, description="Always true for success responses")
    message: str = Field(..., description="Success message")
    data: None = Field(None, description="No data for deletion operations")
