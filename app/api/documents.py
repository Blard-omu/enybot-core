"""
Document management API endpoints for the AI Student Support Service.
"""
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.documents import (
    PDFUploadResponse, PDFUploadData, TextDocumentRequest, 
    TextDocumentResponse, TextDocumentData, GetDocumentsResponse, 
    GetDocumentsData, DeleteDocumentResponse
)
from app.services.document_service import DocumentService
from app.utils.logger import get_logger
from app.utils.service_manager import get_global_services

logger = get_logger(__name__)
router = APIRouter()

# Initialize document service
document_service = DocumentService()


@router.post("/text", response_model=TextDocumentResponse)
async def add_text_document(request: TextDocumentRequest) -> TextDocumentResponse:
    """Add a text document to the knowledge base."""
    try:
        _, _, chroma_service = get_global_services()
        
        if not chroma_service or not chroma_service.is_available():
            raise HTTPException(status_code=503, detail="Knowledge base not available")
        
        # Add text document (only content is required)
        success = await document_service.add_text_document(
            content=request.content,
            chroma_service=chroma_service
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add text document")
        
        # Build response data
        response_data = TextDocumentData(
            document_id=document_service.last_document_id,
            content_length=len(request.content),
            message="Document processed successfully"
        )
        
        # Build standardized response
        response = TextDocumentResponse(
            success=True,
            message="Text document added successfully",
            data=response_data
        )
        
        logger.info(f"Text document added successfully with {len(request.content)} characters")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding text document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/pdfs", response_model=PDFUploadResponse)
async def upload_pdfs(files: List[UploadFile] = File(...)) -> PDFUploadResponse:
    """Upload PDF files and extract text for the knowledge base."""
    try:
        _, _, chroma_service = get_global_services()
        
        if not chroma_service or not chroma_service.is_available():
            raise HTTPException(status_code=503, detail="Knowledge base not available")
        
        # Upload and process PDFs
        result = await document_service.upload_pdfs(files)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Build response data
        response_data = PDFUploadData(
            pdfs_processed=result["pdfs_processed"],
            pdfs_failed=result["pdfs_failed"],
            total_documents_added=result["total_documents_added"]
        )
        
        # Build standardized response
        response = PDFUploadResponse(
            success=True,
            message="PDFs uploaded and processed successfully",
            data=response_data
        )
        
        logger.info(f"PDFs uploaded successfully: {result['pdfs_processed']} files processed")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading PDFs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=GetDocumentsResponse)
async def get_documents() -> GetDocumentsResponse:
    """Get all documents from the knowledge base."""
    try:
        _, _, chroma_service = get_global_services()
        
        if not chroma_service or not chroma_service.is_available():
            raise HTTPException(status_code=503, detail="Knowledge base not available")
        
        # Get documents
        documents = await document_service.get_documents()
        
        # Build response data
        response_data = GetDocumentsData(
            knowledge_base_info=documents["knowledge_base_info"],
            document_count=documents["document_count"]
        )
        
        # Build standardized response
        response = GetDocumentsResponse(
            success=True,
            message="Documents retrieved successfully",
            data=response_data
        )
        
        logger.info(f"Retrieved {len(documents)} documents")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/", response_model=DeleteDocumentResponse)
async def clear_knowledge_base() -> DeleteDocumentResponse:
    """Clear all data from the knowledge base."""
    try:
        _, _, chroma_service = get_global_services()
        
        if not chroma_service or not chroma_service.is_available():
            raise HTTPException(status_code=503, detail="Knowledge base not available")
        
        # Clear all data from knowledge base
        result = await document_service.clear_knowledge_base()
        
        if result["status"] != "success":
            raise HTTPException(status_code=500, detail=result["message"])
        
        # Build standardized response
        response = DeleteDocumentResponse(
            success=True,
            message=result["message"],
            data=None
        )
        
        logger.info(f"Knowledge base cleared successfully: {result.get('documents_removed', 0)} documents removed")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing knowledge base: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
