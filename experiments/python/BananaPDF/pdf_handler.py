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
    
    def reload(self):
        """Reload the PDF document from disk"""
        try:
            # Close current document if open
            if self.doc:
                self.doc.close()
            
            # Reopen the document
            self.doc = fitz.open(self.filepath)
            self.reader = PdfReader(self.filepath)
            self.page_count = len(self.reader.pages)
            print(f"✓ PDF document reloaded from {self.filepath}")
        except Exception as e:
            raise Exception(f"Failed to reload PDF: {str(e)}")
    
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
            width = float(media_box.width)
            height = float(media_box.height)
            print(f"  PDFHandler.get_page_dimensions(page {page_num}):")
            print(f"    MediaBox: {media_box}")
            print(f"    Width: {width}, Height: {height} points")
            # Also check PyMuPDF dimensions
            mupdf_page = self.doc[page_num]
            mupdf_rect = mupdf_page.rect
            print(f"    PyMuPDF rect: {mupdf_rect}")
            return {
                'width': width,
                'height': height,
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
    
    def add_textbox_to_pdf(self, page_num, x, y, width, height, text, fontsize=12, color='#000000'):
        """Add text box directly to PDF page"""
        try:
            print(f"  PDFHandler.add_textbox_to_pdf() called")
            print(f"    Page: {page_num}")
            print(f"    Position: ({x}, {y})")
            print(f"    Size: {width}x{height}")
            print(f"    Text: {text}")
            
            # Get page from PyMuPDF
            page = self.doc[page_num]
            
            # Convert color hex to RGB tuple
            color_hex = color.lstrip('#')
            color_rgb = tuple(int(color_hex[i:i+2], 16) / 255.0 for i in (0, 2, 4))
            
            # Create rect in PDF coordinates
            rect = fitz.Rect(x, y, x + width, y + height)
            print(f"    Rect: {rect}")
            
            # Insert text box directly into PDF
            page.insert_textbox(rect, text, fontsize=fontsize, color=color_rgb, borders=0)
            
            print(f"  ✓ Text box added to PDF page {page_num}")
            
            # Save changes to the PDF file
            self.doc.save(self.filepath, incremental=False)
            print(f"  ✓ PDF file saved")
            
        except Exception as e:
            print(f"  ✗ Error adding text box: {str(e)}")
            raise Exception(f"Failed to add text box: {str(e)}")

