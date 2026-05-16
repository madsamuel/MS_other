"""PDF Handler - handles PDF rendering and basic operations"""
import io
from pypdf import PdfReader, PdfWriter
from PIL import Image, ImageDraw
import fitz  # PyMuPDF for better rendering


class PDFHandler:
    """Handle PDF operations"""
    
    def __init__(self, filepath):
        """Initialize PDF handler with file path"""
        self.filepath = filepath
        self.reader = PdfReader(filepath)
        self.doc = fitz.open(filepath)
        self.page_count = len(self.reader.pages)
    
    def get_page_count(self):
        """Get total number of pages"""
        return self.page_count
    
    def render_page(self, page_num, rotation=0, zoom=1.0):
        """
        Render a PDF page to PNG image
        
        Args:
            page_num: 0-based page index
            rotation: rotation in degrees (0, 90, 180, 270)
            zoom: zoom factor
        
        Returns:
            BytesIO object containing PNG image
        """
        try:
            if page_num < 0 or page_num >= self.page_count:
                raise ValueError(f"Invalid page number: {page_num}")
            
            # Get page from PyMuPDF doc
            page = self.doc[page_num]
            
            # Apply rotation
            if rotation != 0:
                page.set_rotation(rotation)
            
            # Render to image with zoom
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save to BytesIO
            output = io.BytesIO()
            img.save(output, format='PNG')
            output.seek(0)
            
            return output
            
        except Exception as e:
            raise Exception(f"Failed to render page {page_num}: {str(e)}")
    
    def get_page_dimensions(self, page_num):
        """Get page dimensions in points"""
        try:
            page = self.reader.pages[page_num]
            media_box = page.mediabox
            return {
                'width': float(media_box.width),
                'height': float(media_box.height),
            }
        except Exception as e:
            raise Exception(f"Failed to get page dimensions: {str(e)}")
    
    def extract_text(self, page_num):
        """Extract text from a page"""
        try:
            page = self.doc[page_num]
            return page.get_text()
        except Exception as e:
            raise Exception(f"Failed to extract text: {str(e)}")
    
    def get_page_as_image(self, page_num, dpi=150):
        """Get page as PIL Image"""
        try:
            page = self.doc[page_num]
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            return img.convert('RGB')
            
        except Exception as e:
            raise Exception(f"Failed to get page as image: {str(e)}")
