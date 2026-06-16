"""Export service (Single Responsibility + Dependency Inversion)"""
import os
import logging
from typing import Dict, List, Any, Tuple
from pdf_exporter import PDFExporter
from pdf_handler import PDFHandler


logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting PDFs (Single Responsibility)"""
    
    def __init__(self, exports_folder: str = 'exports'):
        """
        Initialize export service
        
        Args:
            exports_folder: Directory for exported files
        """
        self._exports_folder = exports_folder
        self._ensure_folder_exists(exports_folder)
    
    def export_pdf(
        self,
        pdf_handler: PDFHandler,
        pages_to_export: List[Tuple[int, Dict[str, Any]]],
        annotations: Dict[str, List[Dict[str, Any]]],
        textboxes: Dict[str, Dict[str, Any]],
        flatten: bool = False,
    ) -> str:
        """
        Export PDF with annotations and text boxes
        
        Args:
            pdf_handler: PDFHandler instance
            pages_to_export: List of (page_index, page_data) tuples
            annotations: Dictionary of annotations by page
            textboxes: Dictionary of text boxes by ID
            flatten: Whether to flatten annotations
            
        Returns:
            Path to exported PDF file
            
        Raises:
            ValueError: If export fails
        """
        try:
            logger.info(f"Exporting PDF with {len(pages_to_export)} pages")
            
            # Validate inputs
            if not pages_to_export:
                raise ValueError("No pages to export")
            
            # Use PDFExporter to create the PDF
            exporter = PDFExporter(pdf_handler)
            output_path = exporter.export(pages_to_export, annotations, textboxes, flatten)
            
            # Verify export
            if not os.path.isfile(output_path):
                raise ValueError(f"Export failed: Output file not created at {output_path}")
            
            file_size = os.path.getsize(output_path)
            logger.info(f"PDF exported successfully: {output_path} ({file_size} bytes)")
            
            return output_path
            
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            raise ValueError(f"Failed to export PDF: {e}")
    
    def get_export_path(self, filename: str) -> str:
        """
        Get full path for export file
        
        Args:
            filename: Export filename
            
        Returns:
            Full path to export file
        """
        return os.path.join(self._exports_folder, filename)
    
    def _ensure_folder_exists(self, folder_path: str) -> None:
        """Ensure folder exists"""
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logger.info(f"Created exports folder: {folder_path}")
