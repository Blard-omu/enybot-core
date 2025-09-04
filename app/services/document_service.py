"""
Document service for managing PDF uploads and text document processing.
"""
import logging
import uuid
from typing import List, Dict, Any, Optional
from fastapi import UploadFile

from app.services.chroma_service import ChromaService
from app.utils.pdf_extractor import PDFExtractor
from app.models.documents import TextDocumentRequest

logger = logging.getLogger(__name__)


class DocumentService:
    """Service class for document management operations."""
    
    def __init__(self):
        """Initialize the document service."""
        self.chroma_service = ChromaService()
        self.last_document_id = None
    
    async def add_text_document(self, content: str, chroma_service: ChromaService) -> bool:
        """Add a text document to the knowledge base. Returns True if successful."""
        try:
            # Generate unique ID
            doc_id = str(uuid.uuid4())
            self.last_document_id = doc_id
            
            # Prepare document data with default metadata
            document_data = {
                "id": doc_id,
                "content": content,
                "metadata": {
                    "type": "text",
                    "title": f"Text Document {doc_id[:8]}",
                    "source": "user_upload",
                    "tags": "text,user_content",  # Convert list to comma-separated string
                    "content_length": len(content),
                    "added_at": "2024-01-15T10:30:00Z"
                }
            }
            
            # Add document to ChromaDB
            success = await chroma_service.add_documents([document_data])
            
            if not success:
                logger.error("Failed to add text document to knowledge base")
                return False
            
            logger.info(f"Successfully added text document with {len(content)} characters")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add text document: {e}")
            return False
    
    async def upload_pdfs(self, files: List[UploadFile]) -> Dict[str, Any]:
        """Upload and process multiple PDF files. Returns upload results and statistics."""
        if not files:
            raise ValueError("No files provided")
        
        logger.info(f"Processing {len(files)} PDF files for upload")
        
        documents_data = []
        pdfs_processed = 0
        pdfs_failed = 0
        
        for pdf_file in files:
            try:
                result = await self._process_single_pdf(pdf_file)
                if result:
                    documents_data.append(result)
                    pdfs_processed += 1
                else:
                    pdfs_failed += 1
            except Exception as e:
                logger.error(f"Failed to process PDF {pdf_file.filename}: {e}")
                pdfs_failed += 1
                continue
        
        if not documents_data:
            raise ValueError("No PDFs could be processed successfully")
        
        # Add documents to ChromaDB
        success = await self.chroma_service.add_documents(documents_data)
        
        if not success:
            raise RuntimeError("Failed to add documents to knowledge base")
        
        total_added = len(documents_data)
        logger.info(f"Successfully added {total_added} PDF documents to knowledge base")
        
        return {
            "success": True,
            "message": f"Successfully processed {pdfs_processed} PDF documents",
            "pdfs_processed": pdfs_processed,
            "pdfs_failed": pdfs_failed,
            "total_documents_added": total_added
        }
    
    async def _process_single_pdf(self, pdf_file: UploadFile) -> Optional[Dict[str, Any]]:
        """Process a single PDF file. Returns document data or None if processing fails."""
        # Validate file type
        if not pdf_file.filename.lower().endswith('.pdf'):
            logger.warning(f"Skipping non-PDF file: {pdf_file.filename}")
            return None
        
        # Read file content
        file_content = await pdf_file.read()
        
        # Validate PDF content
        if not PDFExtractor.is_valid_pdf(file_content):
            logger.warning(f"Invalid PDF file: {pdf_file.filename}")
            return None
        
        # Extract text from PDF
        extracted_text = PDFExtractor.extract_text_from_bytes(file_content)
        
        if not extracted_text:
            logger.warning(f"Failed to extract text from PDF: {pdf_file.filename}")
            return None
        
        # Generate unique ID
        doc_id = str(uuid.uuid4())
        
        # Prepare document data
        document_data = {
            "id": doc_id,
            "content": extracted_text,
            "metadata": {
                "type": "pdf",
                "source": pdf_file.filename,
                "original_filename": pdf_file.filename,
                "file_size": len(file_content),
                "added_at": "2024-01-15T10:30:00Z"
            }
        }
        
        logger.info(f"Successfully processed PDF: {pdf_file.filename}")
        return document_data
    
    async def get_documents(self) -> Dict[str, Any]:
        """Get information about all documents in the knowledge base. Returns document info dict."""
        try:
            # Get collection info
            collection_info = self.chroma_service.get_collection_info()
            
            # Get document count
            document_count = await self.chroma_service.get_document_count()
            
            return {
                "status": "success",
                "knowledge_base_info": collection_info,
                "document_count": document_count,
                "message": "Knowledge base information retrieved successfully"
            }
        except Exception as e:
            logger.error(f"Failed to get documents: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to retrieve knowledge base information"
            }
    
    async def clear_knowledge_base(self) -> Dict[str, Any]:
        """Clear all data from the knowledge base. Returns deletion result dict."""
        try:
            # Get document count before deletion for logging
            document_count = await self.chroma_service.get_document_count()
            
            # Clear all data from ChromaDB
            success = await self.chroma_service.clear_collection()
            
            if success:
                return {
                    "status": "success",
                    "message": f"Successfully cleared all data from knowledge base ({document_count} documents removed)",
                    "documents_removed": document_count,
                    "deletion_type": "clear_all"
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to clear knowledge base"
                }
                
        except Exception as e:
            logger.error(f"Failed to clear knowledge base: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Error clearing knowledge base"
            }
    
    async def delete_document(self) -> Dict[str, Any]:
        """Clear all data from the knowledge base. Returns deletion result dict."""
        return await self.clear_knowledge_base()
