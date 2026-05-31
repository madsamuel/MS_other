"""PDF Exporter - exports PDFs with annotations"""
import base64
import io
import os
from datetime import datetime
from PIL import Image
import fitz  # PyMuPDF for PDF manipulation


class PDFExporter:
    """Export PDF with annotations"""
    
    def __init__(self, pdf_handler):
        """Initialize exporter"""
        self.pdf_handler = pdf_handler
        self.output_path = None
    

    def export(self, pages_to_export, annotations_dict, textboxes_dict, flatten=False):
        """
        Export PDF with annotations
        
        Args:
            pages_to_export: list of (original_index, page_data)
            annotations_dict: {page_num: [annotation_list]}
            textboxes_dict: {textbox_id: textbox_data}
            flatten: whether to flatten annotations into PDF
        
        Returns:
            Path to output PDF
        """
        try:
            print(f"\n--- PDF EXPORT ---")
            print(f"Annotations dict type: {type(annotations_dict)}")
            print(f"Annotations dict keys: {list(annotations_dict.keys()) if isinstance(annotations_dict, dict) else 'N/A'}")
            print(f"Annotations content: {annotations_dict}")
            print(f"Textboxes dict type: {type(textboxes_dict)}")
            print(f"Textboxes content: {textboxes_dict}")
            
            # Open the original PDF for modification
            doc = fitz.open(self.pdf_handler.filepath)
            print(f"Original PDF has {len(doc)} pages")
            new_doc = fitz.open()  # Create new document
            
            # Process selected pages
            for new_page_idx, (orig_page_idx, page_data) in enumerate(pages_to_export):
                print(f"\nProcessing page {orig_page_idx} (new index: {new_page_idx})")
                
                # Validate page index
                if orig_page_idx < 0 or orig_page_idx >= len(doc):
                    print(f"  ERROR: Page index {orig_page_idx} is out of range (PDF has {len(doc)} pages)")
                    raise Exception(f"Page {orig_page_idx} not found in PDF")
                
                # Get original page
                orig_page = doc[orig_page_idx]
                
                # Apply rotation if needed
                rotation = page_data.get('rotation', 0)
                if rotation != 0:
                    orig_page.set_rotation(rotation)
                
                # Insert into new document
                new_doc.insert_pdf(doc, from_page=orig_page_idx, to_page=orig_page_idx)
                new_page = new_doc[new_page_idx]
                
                # Add annotations for this page
                # Note: JSON converts numeric keys to strings, so check both string and int keys
                page_key = str(orig_page_idx)
                if page_key in annotations_dict:
                    print(f"  Found {len(annotations_dict[page_key])} annotations for page {orig_page_idx}")
                    for annotation in annotations_dict[page_key]:
                        print(f"    Adding annotation: {annotation}")
                        self._add_annotation_to_page(new_page, annotation)
                elif orig_page_idx in annotations_dict:
                    # Fallback for integer keys
                    print(f"  Found {len(annotations_dict[orig_page_idx])} annotations for page {orig_page_idx}")
                    for annotation in annotations_dict[orig_page_idx]:
                        print(f"    Adding annotation: {annotation}")
                        self._add_annotation_to_page(new_page, annotation)
                else:
                    print(f"  No annotations for page {orig_page_idx} (keys in dict: {list(annotations_dict.keys())})")
                
                # Add text boxes for this page
                print(f"  Processing text boxes. Type: {type(textboxes_dict)}, Length: {len(textboxes_dict) if hasattr(textboxes_dict, '__len__') else 'N/A'}")
                
                if isinstance(textboxes_dict, dict) and textboxes_dict:
                    # textboxes_dict is a dict with IDs as keys
                    for tb_id, textbox in textboxes_dict.items():
                        if isinstance(textbox, dict) and textbox.get('pageNum') == orig_page_idx:
                            print(f"    Adding textbox '{tb_id}': {textbox}")
                            self._add_textbox_to_page(new_page, textbox)
                elif isinstance(textboxes_dict, list) and textboxes_dict:
                    # Fallback: if it's a list of textboxes
                    for textbox in textboxes_dict:
                        if isinstance(textbox, dict) and textbox.get('pageNum') == orig_page_idx:
                            print(f"    Adding textbox from list: {textbox}")
                            self._add_textbox_to_page(new_page, textbox)
                else:
                    if not textboxes_dict:
                        print(f"  No text boxes to add (empty or None)")
            
            # Save document to BytesIO buffer (in-memory, no disk files)
            print("DEBUG: Creating BytesIO buffer for in-memory PDF...")
            pdf_buffer = io.BytesIO()
            print("DEBUG: Saving PyMuPDF document to BytesIO...")
            new_doc.save(pdf_buffer)
            print(f"DEBUG: Successfully saved to buffer, size={pdf_buffer.tell()} bytes")
            new_doc.close()
            doc.close()
            
            # Reset buffer position to start
            pdf_buffer.seek(0)
            print("DEBUG: Buffer position reset, returning BytesIO object")
            
            self.output_buffer = pdf_buffer
            return pdf_buffer
            
        except Exception as e:
            raise Exception(f"Failed to export PDF: {str(e)}")
    
    def _add_annotation_to_page(self, page, annotation):
        """Add annotation to page"""
        try:
            ann_type = annotation.get('type')
            x = annotation.get('x')
            y = annotation.get('y')
            width = annotation.get('width')
            height = annotation.get('height')
            color = self._hex_to_rgb(annotation.get('color', '#FFFF00'))
            text = annotation.get('text', '')
            
            # Convert hex color to RGB (0-1 range)
            color_normalized = tuple(c / 255.0 for c in color)
            
            # Create rectangle for various annotation types
            rect = fitz.Rect(x, y, x + width, y + height)
            
            if ann_type == 'highlight':
                # Use proper PDF highlight annotation (like Adobe)
                page.add_highlight_annot(rect)
            elif ann_type in ('drawing', 'signature'):
                image_data = annotation.get('imageData', '')
                if not image_data:
                    raise ValueError(f"Missing imageData for annotation type: {ann_type}")
                self._insert_base64_image(page, rect, image_data)
            elif ann_type == 'rectangle':
                page.draw_rect(rect, color=color_normalized, width=2)
            elif ann_type == 'circle':
                page.draw_circle(
                    fitz.Point(x + width/2, y + height/2),
                    min(width, height) / 2,
                    color=color_normalized,
                    width=2,
                )
            elif ann_type == 'comment':
                annot = page.add_text_annot(fitz.Point(x, y), text, icon='Comment')
                if annot:
                    annot.set_colors({'stroke': color_normalized})
            elif ann_type == 'freehand':
                # For freehand, we would draw paths
                # This is simplified - you'd need to draw actual path data
                points = annotation.get('points', [])
                if len(points) > 1:
                    for i in range(len(points) - 1):
                        p1 = fitz.Point(points[i][0], points[i][1])
                        p2 = fitz.Point(points[i+1][0], points[i+1][1])
                        page.draw_line(p1, p2, color=color_normalized, width=2)
            elif ann_type == 'line':
                page.draw_line(
                    fitz.Point(x, y),
                    fitz.Point(x + width, y + height),
                    color=color_normalized,
                    width=2,
                )
            
        except Exception as e:
            print(f"Warning: Failed to add annotation: {str(e)}")

    def _insert_base64_image(self, page, rect, image_data):
        """Insert a base64-encoded drawing/signature image into the page."""
        if image_data.startswith('data:image/'):
            image_data = image_data.split(',', 1)[1]

        image_bytes = base64.b64decode(image_data)

        # Normalize to PNG bytes so PyMuPDF receives a consistent raster format.
        image = Image.open(io.BytesIO(image_bytes))
        png_buffer = io.BytesIO()
        image.save(png_buffer, format='PNG')
        page.insert_image(rect, stream=png_buffer.getvalue())
    
    def _add_textbox_to_page(self, page, textbox):
        """Add text box to page"""
        try:
            x = textbox.get('x')
            y = textbox.get('y')
            width = textbox.get('width', 150)
            height = textbox.get('height', 30)
            text = textbox.get('text', '')
            color = self._hex_to_rgb(textbox.get('color', '#000000'))
            font_size = textbox.get('fontSize', 12)
            
            print(f"      Text: '{text}', Position: ({x}, {y}), Size: {width}x{height}, Color: {color}, FontSize: {font_size}")
            
            # Convert hex color to RGB (0-1 range)
            color_normalized = tuple(c / 255.0 for c in color)
            
            # Add text to page using insert_textbox
            rect = fitz.Rect(x, y, x + width, y + height)
            result = page.insert_textbox(
                rect,
                text,
                fontsize=font_size,
                color=color_normalized,
                align=fitz.TEXT_ALIGN_LEFT,
                fontname='helv',  # helvetica
            )
            print(f"      ✓ Text box added successfully, boundary box: {result}")
            
        except Exception as e:
            print(f"      ✗ Failed to add textbox: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple (0-255)"""
        try:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            return (0, 0, 0)
