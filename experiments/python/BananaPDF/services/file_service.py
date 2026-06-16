"""File service (Single Responsibility + Dependency Inversion)"""
import os
import logging
from datetime import datetime
from werkzeug.utils import secure_filename


logger = logging.getLogger(__name__)


class FileService:
    """Service for file operations (Single Responsibility)"""
    
    def __init__(self, upload_folder: str = 'uploads'):
        """
        Initialize file service
        
        Args:
            upload_folder: Directory for uploaded files
        """
        self._upload_folder = upload_folder
        self._ensure_folder_exists(upload_folder)
    
    def save_uploaded_file(self, file_obj, original_filename: str) -> str:
        """
        Save uploaded file
        
        Args:
            file_obj: File object from request.files
            original_filename: Original filename
            
        Returns:
            Path to saved file
            
        Raises:
            ValueError: If filename is invalid or file save fails
        """
        if not original_filename:
            raise ValueError("No filename provided")
        
        # Secure the filename
        secure_name = secure_filename(original_filename)
        if not secure_name:
            raise ValueError(f"Invalid filename: {original_filename}")
        
        # Add timestamp prefix for uniqueness
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + secure_name
        filepath = os.path.join(self._upload_folder, filename)
        
        try:
            file_obj.save(filepath)
            logger.info(f"File saved: {filepath}")
            return filepath
        except Exception as e:
            raise ValueError(f"Failed to save file: {e}")
    
    def cleanup_file(self, filepath: str) -> bool:
        """
        Delete file
        
        Args:
            filepath: Path to file
            
        Returns:
            True if deleted, False if file doesn't exist
        """
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
                logger.info(f"File deleted: {filepath}")
                return True
            return False
        except Exception as e:
            logger.warning(f"Failed to delete file {filepath}: {e}")
            return False
    
    def read_file(self, filepath: str) -> bytes:
        """
        Read file into memory
        
        Args:
            filepath: Path to file
            
        Returns:
            File contents as bytes
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            with open(filepath, 'rb') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Failed to read file {filepath}: {e}")
    
    def file_exists(self, filepath: str) -> bool:
        """Check if file exists"""
        return os.path.isfile(filepath)
    
    def get_file_size(self, filepath: str) -> int:
        """Get file size in bytes"""
        if not os.path.isfile(filepath):
            return 0
        return os.path.getsize(filepath)
    
    def _ensure_folder_exists(self, folder_path: str) -> None:
        """Ensure folder exists"""
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logger.info(f"Created folder: {folder_path}")
