"""PDF service (Single Responsibility + Dependency Inversion)"""
import os
import logging
from typing import Optional
from pdf_handler import PDFHandler


logger = logging.getLogger(__name__)


class PDFService:
    """Service for PDF operations (Single Responsibility)"""
    
    def __init__(self, pdf_handler: Optional[PDFHandler] = None):
        """
        Initialize PDF service
        
        Args:
            pdf_handler: PDFHandler instance (Dependency Injection)
        """
        self._pdf_handler = pdf_handler
    
    def load_pdf(self, filepath: str) -> int:
        """
        Load PDF from file
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            Number of pages in PDF
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a valid PDF
        """
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"PDF file not found: {filepath}")
        
        try:
            self._pdf_handler = PDFHandler(filepath)
            page_count = self._pdf_handler.get_page_count()
            logger.info(f"Loaded PDF with {page_count} pages: {filepath}")
            return page_count
        except Exception as e:
            raise ValueError(f"Failed to load PDF: {e}")
    
    def get_page_count(self) -> int:
        """Get number of pages in PDF"""
        if not self._pdf_handler:
            raise RuntimeError("No PDF loaded")
        return self._pdf_handler.get_page_count()
    
    def get_handler(self) -> PDFHandler:
        """Get underlying PDF handler"""
        if not self._pdf_handler:
            raise RuntimeError("No PDF loaded")
        return self._pdf_handler
    
    def is_loaded(self) -> bool:
        """Check if PDF is loaded"""
        return self._pdf_handler is not None
    
    def close(self) -> None:
        """Close PDF"""
        if self._pdf_handler:
            # PDFHandler doesn't have close, but we can clear it
            self._pdf_handler = None
            logger.info("PDF closed")
