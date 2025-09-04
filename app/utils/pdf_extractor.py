"""
PDF text extraction utility for the AI Student Support-svc.
"""
import io
from typing import Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyPDF2 not available. PDF extraction will be limited.")


class PDFExtractor:
    """Utility class for extracting text from PDF files."""
    
    @staticmethod
    def extract_text_from_bytes(pdf_bytes: bytes) -> Optional[str]:
        """Extract text from PDF bytes with error handling."""
        if not PDF_AVAILABLE:
            logger.error("PDF extraction not available - PyPDF2 not installed")
            return None
            
        try:
            # Create PDF reader from bytes
            pdf_stream = io.BytesIO(pdf_bytes)
            pdf_reader = PdfReader(pdf_stream)
            
            # Extract text from all pages
            text_parts = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_parts.append(page_text.strip())
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue
            
            if not text_parts:
                logger.warning("No text could be extracted from PDF")
                return None
            
            # Combine all text parts
            full_text = "\n\n".join(text_parts)
            
            # Clean up text
            cleaned_text = PDFExtractor._clean_text(full_text)
            
            logger.info(f"Successfully extracted {len(cleaned_text)} characters from PDF")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF bytes: {e}")
            return None
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean extracted text by removing excessive whitespace and formatting."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Clean each line
            cleaned_line = ' '.join(line.split())
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        
        # Join lines with proper spacing
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove multiple consecutive newlines
        while '\n\n\n' in cleaned_text:
            cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
        
        return cleaned_text.strip()
    
    @staticmethod
    def is_valid_pdf(pdf_bytes: bytes) -> bool:
        """Check if bytes represent a valid PDF file."""
        if not PDF_AVAILABLE:
            return pdf_bytes.startswith(b'%PDF')
            
        try:
            # Check if it starts with PDF magic number
            if pdf_bytes.startswith(b'%PDF'):
                return True
            
            # Try to read as PDF
            pdf_stream = io.BytesIO(pdf_bytes)
            PdfReader(pdf_stream)
            return True
            
        except Exception:
            return False
