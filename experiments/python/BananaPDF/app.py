"""BananaPDF - A comprehensive PDF editor"""
import os
import json
import io
import tempfile
import shutil
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pdf_handler import PDFHandler
from annotation_manager import AnnotationManager
import fitz  # PyMuPDF
from PIL import Image

# Setup logging to both file and console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flask_debug.log'),
        logging.StreamHandler()
    ]
)

# Also enable verbose Flask logging
app_logger = logging.getLogger('werkzeug')
app_logger.setLevel(logging.DEBUG)

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Global state management
current_session = None
pdf_handler = None
annotation_manager = None


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Serve main app"""
    return render_template('index.html')


@app.route('/api/reset-session', methods=['POST'])
def reset_session():
    """Clear the current session (useful for starting fresh)"""
    global pdf_handler, annotation_manager, current_session
    try:
        # Close and cleanup the current PDF
        if pdf_handler and current_session:
            filepath = current_session.get('filepath')
            if filepath and os.path.isfile(filepath):
                try:
                    os.remove(filepath)
                    logging.info(f"Cleaned up PDF file: {filepath}")
                except Exception as e:
                    logging.warning(f"Could not delete PDF file: {e}")
        
        # Reset all global state
        pdf_handler = None
        annotation_manager = None
        current_session = None
        
        logging.info("Session reset successfully")
        return jsonify({'message': 'Session reset'}), 200
    except Exception as e:
        logging.error(f"Error resetting session: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        print(f"\n--- UPLOAD ---")
        print(f"Original filename: {file.filename}")
        print(f"Secure filename: {filename}")
        print(f"Saving to: {filepath}")
        
        file.save(filepath)
        
        print(f"File saved successfully")
        file_exists = os.path.isfile(filepath)
        file_size = os.path.getsize(filepath) if file_exists else 0
        print(f"Verify - file exists: {file_exists}, size: {file_size} bytes")
        
        # Clean up previous uploaded file if one exists
        global pdf_handler, annotation_manager, current_session
        if current_session and current_session.get('filepath'):
            old_filepath = current_session.get('filepath')
            if old_filepath != filepath and os.path.isfile(old_filepath):
                try:
                    os.remove(old_filepath)
                    print(f"Cleaned up previous upload: {old_filepath}")
                except Exception as cleanup_error:
                    print(f"⚠ Warning: Failed to delete previous upload: {cleanup_error}")
        
        # Initialize PDF handler and annotation manager
        pdf_handler = PDFHandler(filepath)
        annotation_manager = AnnotationManager()
        
        # Get PDF info
        page_count = pdf_handler.get_page_count()
        
        current_session = {
            'filename': filename,
            'filepath': filepath,
            'originalFilename': file.filename,
            'pageCount': page_count,
            'isModified': False,
            'createdAt': datetime.now().isoformat(),
            'pages': [{'index': i, 'rotation': 0, 'deleted': False} for i in range(page_count)],
            'annotations': {},
            'textBoxes': {},
        }
        
        return jsonify({
            'success': True,
            'session': current_session,
            'pageCount': page_count,
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/debug-ping', methods=['POST', 'GET'])
def debug_ping():
    """Simple debug endpoint to test if requests are reaching Flask"""
    method = request.method
    data = request.get_json() if method == 'POST' else None
    print(f"\n{'='*60}")
    print(f"DEBUG PING - Method: {method}")
    if data:
        print(f"Data received: {json.dumps(data, indent=2)}")
    print(f"{'='*60}\n")
    return jsonify({
        'success': True,
        'message': f'Debug ping received via {method}',
        'data': data,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/render-page/<int:page_num>')
def render_page(page_num):
    """Render a specific page as PNG"""
    try:
        if pdf_handler is None:
            return jsonify({'error': 'No PDF loaded'}), 400
        
        # Get page rotation from session
        rotation = 0
        if current_session and page_num < len(current_session['pages']):
            rotation = current_session['pages'][page_num].get('rotation', 0)
        
        image_data = pdf_handler.render_page(page_num, rotation=rotation)
        
        return send_file(
            image_data,
            mimetype='image/png',
            as_attachment=False,
        ), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get-pdf-data')
def get_pdf_data():
    """Get PDF metadata"""
    try:
        global current_session, pdf_handler
        
        # Check if there's a valid session and PDF loaded
        if pdf_handler is None or current_session is None:
            return jsonify({'error': 'No PDF loaded'}), 400
        
        # Also verify the file actually exists
        filepath = current_session.get('filepath')
        if not filepath or not os.path.isfile(filepath):
            # Reset the session if file doesn't exist
            current_session = None
            pdf_handler = None
            return jsonify({'error': 'PDF file not found'}), 400
        
        return jsonify({
            'pageCount': pdf_handler.get_page_count(),
            'fileName': current_session['originalFilename'],
            'filePath': current_session['filename'],
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get-pdf')
def get_pdf():
    """Serve the current PDF file for client-side loading (e.g., after modifications)"""
    try:
        global pdf_handler, current_session
        
        if pdf_handler is None or current_session is None:
            return jsonify({'error': 'No PDF loaded'}), 400
        
        filepath = current_session.get('filepath')
        if not filepath or not os.path.isfile(filepath):
            return jsonify({'error': 'PDF file not found'}), 404
        
        print(f"Serving PDF: {filepath}")
        
        return send_file(
            filepath,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=current_session.get('originalFilename', 'document.pdf')
        ), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/page-dimensions/<int:page_num>')
def get_page_dimensions(page_num):
    """Get actual PDF page dimensions for coordinate calculations"""
    try:
        if pdf_handler is None:
            return jsonify({'error': 'No PDF loaded'}), 400
        
        # page_num is 1-indexed from frontend, convert to 0-indexed
        page_idx = page_num - 1
        
        if page_idx < 0 or page_idx >= pdf_handler.get_page_count():
            return jsonify({'error': f'Invalid page number: {page_num}'}), 400
        
        dimensions = pdf_handler.get_page_dimensions(page_idx)
        
        return jsonify({
            'pageNum': page_num,
            'width': dimensions['width'],
            'height': dimensions['height'],
            'success': True
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add-annotation', methods=['POST'])
def add_annotation():
    """Add annotation to PDF"""
    try:
        if annotation_manager is None:
            annotation_manager = AnnotationManager()
        
        data = request.get_json()
        annotation = annotation_manager.add_annotation(data)
        
        # Store in session
        if current_session:
            page_num = data.get('pageNum')
            if page_num not in current_session['annotations']:
                current_session['annotations'][page_num] = []
            current_session['annotations'][page_num].append(annotation)
            current_session['isModified'] = True
        
        return jsonify({
            'success': True,
            'annotation': annotation,
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add-textbox', methods=['POST'])
def add_textbox():
    """Add text box directly to PDF and return updated page for display"""
    try:
        global pdf_handler, current_session
        
        logging.info(f"\n{'='*60}")
        logging.info("ADD-TEXTBOX ENDPOINT CALLED")
        
        if pdf_handler is None:
            logging.error('No PDF loaded')
            return jsonify({'error': 'No PDF loaded'}), 400
            
        if current_session is None:
            logging.error('No session active')
            return jsonify({'error': 'No session active'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request body'}), 400
        
        page_num = data.get('pageNum', 0)
        text_content = data.get('text', '').strip()
        
        # Validate page number
        if page_num < 0 or page_num >= pdf_handler.get_page_count():
            return jsonify({'error': f'Invalid page number: {page_num}'}), 400
        
        # Validate text content
        if not text_content:
            return jsonify({'error': 'Text content cannot be empty'}), 400
        
        if len(text_content) > 1000:
            return jsonify({'error': 'Text content too long (max 1000 characters)'}), 400
        
        logging.info(f"Page: {page_num}, Text: {text_content}")
        
        # Create text box object
        textbox = {
            'id': f"text_{int(datetime.now().timestamp() * 1000)}",
            'pageNum': page_num,
            'x': float(data.get('x', 50)),
            'y': float(data.get('y', 50)),
            'width': float(data.get('width', 150)),
            'height': float(data.get('height', 30)),
            'text': text_content,
            'fontSize': int(data.get('fontSize', 12)),
            'fontFamily': data.get('fontFamily', 'Arial'),
            'color': data.get('color', '#000000'),
        }
        
        logging.info(f"Text box: {textbox}")
        
        # Store in session
        logging.info(f"Storing in session...")
        if 'textBoxes' not in current_session:
            current_session['textBoxes'] = {}
        
        current_session['textBoxes'][textbox['id']] = textbox
        current_session['isModified'] = True
        logging.info(f"✓ Text box stored in session")
        
        # Add text box directly to PDF in memory
        logging.info(f"Adding text box to PDF in memory...")
        try:
            page = pdf_handler.doc[page_num]
            
            # Convert color hex to RGB
            color_hex = textbox['color'].lstrip('#')
            if len(color_hex) != 6:
                color_hex = '000000'  # Default to black if invalid
            
            try:
                color_rgb = tuple(int(color_hex[i:i+2], 16) / 255.0 for i in (0, 2, 4))
            except ValueError:
                color_rgb = (0, 0, 0)  # Default to black if conversion fails
            
            # Insert text box
            rect = fitz.Rect(textbox['x'], textbox['y'], 
                           textbox['x'] + textbox['width'], 
                           textbox['y'] + textbox['height'])
            
            logging.info(f"DEBUG: Creating textbox:")
            logging.info(f"  Rect: {rect}")
            logging.info(f"  Text: {textbox['text']}")
            logging.info(f"  FontSize: {textbox['fontSize']}")
            logging.info(f"  Color RGB: {color_rgb}")
            
            page.insert_textbox(rect, textbox['text'], fontsize=textbox['fontSize'], 
                              color=color_rgb)
            
            logging.info(f"✓ Text box added to PDF in memory")
            
            # Save the PDF file with changes using a temporary file
            # (direct save to original fails with encryption changes)
            logging.info(f"DEBUG: Saving PDF to {pdf_handler.filepath}")
            
            temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
            os.close(temp_fd)
            
            try:
                pdf_handler.doc.save(temp_path)
                shutil.move(temp_path, pdf_handler.filepath)
                logging.info(f"✓ PDF file saved with text box changes")
                
                # Verify the save
                file_size = os.path.getsize(pdf_handler.filepath)
                logging.info(f"DEBUG: PDF file size after save: {file_size} bytes")
                
                # Reload the PDF document to ensure subsequent operations see the updated file
                logging.info(f"Reloading PDF document...")
                pdf_handler.reload()
                logging.info(f"✓ PDF document reloaded")
                
            except Exception as save_err:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise save_err
            
        except Exception as pdf_err:
            logging.error(f"ERROR: Could not add to PDF in memory: {pdf_err}")
            import traceback
            traceback.print_exc()
            # Continue anyway - will be added at save time
        
        # Re-render the page to show the updated PDF with text box
        logging.info(f"Re-rendering page with text box...")
        image_base64 = None
        try:
            import base64
            page_image = pdf_handler.render_page(page_num)
            image_base64 = base64.b64encode(page_image.getvalue()).decode('utf-8')
            logging.info(f"✓ Page re-rendered")
            
        except Exception as render_err:
            logging.warning(f"Warning: Could not re-render page: {render_err}")
        
        logging.info(f"{'='*60}\n")
        
        response = {
            'success': True,
            'textbox': textbox,
            'message': 'Text box added to PDF'
        }
        
        # Include updated page image if rendering succeeded
        if image_base64:
            response['pageImage'] = f'data:image/png;base64,{image_base64}'
        
        return jsonify(response), 200
        
    except Exception as e:
        error_msg = str(e)
        logging.error(f"EXCEPTION in add_textbox: {error_msg}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        return jsonify({'error': f'Failed to add text box: {error_msg}'}), 500


@app.route('/api/add-comment', methods=['POST'])
def add_comment():
    """Add comment annotation to PDF"""
    try:
        global pdf_handler, current_session
        
        if pdf_handler is None:
            return jsonify({'error': 'No PDF loaded'}), 400
        
        data = request.get_json()
        page_num = data.get('pageNum', 0)
        
        if page_num < 0 or page_num >= pdf_handler.get_page_count():
            return jsonify({'error': f'Invalid page number: {page_num}'}), 400
        
        comment = {
            'id': f"comment_{int(datetime.now().timestamp() * 1000)}",
            'pageNum': page_num,
            'type': 'comment',
            'x': float(data.get('x', 50)),
            'y': float(data.get('y', 50)),
            'width': 24,
            'height': 24,
            'color': '#FF0000',
            'text': data.get('text', '')
        }
        
        logging.info(f"Comment: {comment['text']} at ({comment['x']}, {comment['y']})")
        
        # Store in session
        if 'annotations' not in current_session:
            current_session['annotations'] = {}
        if page_num not in current_session['annotations']:
            current_session['annotations'][page_num] = []
        
        current_session['annotations'][page_num].append(comment)
        current_session['isModified'] = True
        
        return jsonify({
            'success': True,
            'comment': comment,
            'message': 'Comment added'
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error adding comment: {error_msg}")
        return jsonify({'error': f'Failed to add comment: {error_msg}'}), 500


@app.route('/api/add-drawing', methods=['POST'])
def add_drawing():
    """Add drawing to PDF"""
    try:
        global pdf_handler, current_session
        
        logging.info("ADD-DRAWING ENDPOINT CALLED")
        
        if pdf_handler is None:
            return jsonify({'error': 'No PDF loaded'}), 400
        
        data = request.get_json()
        page_num = data.get('pageNum', 0)
        
        if page_num < 0 or page_num >= pdf_handler.get_page_count():
            return jsonify({'error': f'Invalid page number: {page_num}'}), 400
        
        # Extract image data (base64)
        image_data = data.get('imageData', '')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Convert base64 to image bytes
        import base64
        from PIL import Image
        from io import BytesIO
        
        try:
            # Remove data URI prefix if present
            if image_data.startswith('data:image/'):
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            
            logging.info(f"Image size: {image.size}")
        except Exception as img_err:
            logging.error(f"Error processing image: {img_err}")
            return jsonify({'error': f'Invalid image data: {img_err}'}), 400
        
        # Add to PDF using PyMuPDF
        try:
            page = pdf_handler.doc[page_num]
            
            x = float(data.get('x', 50))
            y = float(data.get('y', 50))
            width = float(data.get('width', 200))
            height = float(data.get('height', 150))
            
            # Save image to temporary file
            temp_img_path = os.path.join(tempfile.gettempdir(), f'drawing_{int(datetime.now().timestamp() * 1000)}.png')
            image.save(temp_img_path, 'PNG')
            
            # Insert image into PDF
            rect = fitz.Rect(x, y, x + width, y + height)
            page.insert_image(rect, filename=temp_img_path, overlay=True)
            
            logging.info(f"Drawing inserted at ({x}, {y})")
            
            # Save PDF
            temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
            os.close(temp_fd)
            
            try:
                pdf_handler.doc.save(temp_path)
                shutil.move(temp_path, pdf_handler.filepath)
                logging.info(f"✓ PDF saved with drawing")
                
                pdf_handler.reload()
                logging.info(f"✓ PDF reloaded")
                
            except Exception as save_err:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise save_err
            finally:
                # Clean up temp image
                if os.path.exists(temp_img_path):
                    os.remove(temp_img_path)
            
            # Store in session
            if 'drawings' not in current_session:
                current_session['drawings'] = {}
            if page_num not in current_session['drawings']:
                current_session['drawings'][page_num] = []
            
            drawing_info = {
                'id': f"drawing_{int(datetime.now().timestamp() * 1000)}",
                'x': x, 'y': y, 'width': width, 'height': height
            }
            current_session['drawings'][page_num].append(drawing_info)
            current_session['isModified'] = True
            
            # Re-render page
            page_image = pdf_handler.render_page(page_num)
            image_base64 = base64.b64encode(page_image.getvalue()).decode('utf-8')
            
            return jsonify({
                'success': True,
                'drawing': drawing_info,
                'pageImage': f'data:image/png;base64,{image_base64}',
                'message': 'Drawing added'
            }), 200
            
        except Exception as pdf_err:
            logging.error(f"Error adding drawing to PDF: {pdf_err}")
            raise pdf_err
        
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error in add-drawing: {error_msg}")
        return jsonify({'error': f'Failed to add drawing: {error_msg}'}), 500


@app.route('/api/add-signature', methods=['POST'])
def add_signature():
    """Add signature to PDF"""
    try:
        global pdf_handler, current_session
        
        logging.info("ADD-SIGNATURE ENDPOINT CALLED")
        
        if pdf_handler is None:
            return jsonify({'error': 'No PDF loaded'}), 400
        
        data = request.get_json()
        page_num = data.get('pageNum', 0)
        
        if page_num < 0 or page_num >= pdf_handler.get_page_count():
            return jsonify({'error': f'Invalid page number: {page_num}'}), 400
        
        # Extract image data (base64)
        image_data = data.get('imageData', '')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Convert base64 to image bytes
        import base64
        from PIL import Image
        from io import BytesIO
        
        try:
            # Remove data URI prefix if present
            if image_data.startswith('data:image/'):
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            
            logging.info(f"Signature image size: {image.size}")
        except Exception as img_err:
            logging.error(f"Error processing signature image: {img_err}")
            return jsonify({'error': f'Invalid image data: {img_err}'}), 400
        
        # Add to PDF using PyMuPDF
        try:
            page = pdf_handler.doc[page_num]
            
            x = float(data.get('x', 50))
            y = float(data.get('y', 50))
            width = float(data.get('width', 150))
            height = float(data.get('height', 100))
            
            # Save image to temporary file
            temp_img_path = os.path.join(tempfile.gettempdir(), f'signature_{int(datetime.now().timestamp() * 1000)}.png')
            image.save(temp_img_path, 'PNG')
            
            # Insert image into PDF
            rect = fitz.Rect(x, y, x + width, y + height)
            page.insert_image(rect, filename=temp_img_path)
            
            logging.info(f"Signature inserted at ({x}, {y})")
            
            # Save PDF
            temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
            os.close(temp_fd)
            
            try:
                pdf_handler.doc.save(temp_path)
                shutil.move(temp_path, pdf_handler.filepath)
                logging.info(f"✓ PDF saved with signature")
                
                pdf_handler.reload()
                logging.info(f"✓ PDF reloaded")
                
            except Exception as save_err:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise save_err
            finally:
                # Clean up temp image
                if os.path.exists(temp_img_path):
                    os.remove(temp_img_path)
            
            # Store in session
            if 'signatures' not in current_session:
                current_session['signatures'] = {}
            if page_num not in current_session['signatures']:
                current_session['signatures'][page_num] = []
            
            signature_info = {
                'id': f"signature_{int(datetime.now().timestamp() * 1000)}",
                'x': x, 'y': y, 'width': width, 'height': height
            }
            current_session['signatures'][page_num].append(signature_info)
            current_session['isModified'] = True
            
            # Re-render page
            page_image = pdf_handler.render_page(page_num)
            image_base64 = base64.b64encode(page_image.getvalue()).decode('utf-8')
            
            return jsonify({
                'success': True,
                'signature': signature_info,
                'pageImage': f'data:image/png;base64,{image_base64}',
                'message': 'Signature added'
            }), 200
            
        except Exception as pdf_err:
            logging.error(f"Error adding signature to PDF: {pdf_err}")
            raise pdf_err
        
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error in add-signature: {error_msg}")
        return jsonify({'error': f'Failed to add signature: {error_msg}'}), 500


@app.route('/api/rotate-page', methods=['POST'])
def rotate_page():
    """Rotate a page"""
    try:
        data = request.get_json()
        page_num = data.get('pageNum')
        
        if current_session and page_num < len(current_session['pages']):
            current_session['pages'][page_num]['rotation'] = \
                (current_session['pages'][page_num].get('rotation', 0) + 90) % 360
            current_session['isModified'] = True
            
            return jsonify({
                'success': True,
                'rotation': current_session['pages'][page_num]['rotation'],
            }), 200
        
        return jsonify({'error': 'Invalid page number'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete-page', methods=['POST'])
def delete_page():
    """Delete a page"""
    try:
        data = request.get_json()
        page_num = data.get('pageNum')
        
        if current_session and page_num < len(current_session['pages']):
            current_session['pages'][page_num]['deleted'] = True
            current_session['isModified'] = True
            
            return jsonify({'success': True}), 200
        
        return jsonify({'error': 'Invalid page number'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reorder-pages', methods=['POST'])
def reorder_pages():
    """Reorder pages"""
    try:
        data = request.get_json()
        new_order = data.get('pageOrder', [])
        
        if current_session:
            # Reorder pages based on new order
            original_pages = current_session['pages'].copy()
            for new_idx, orig_idx in enumerate(new_order):
                if 0 <= orig_idx < len(original_pages):
                    current_session['pages'][new_idx] = original_pages[orig_idx]
            
            current_session['isModified'] = True
            
            return jsonify({'success': True}), 200
        
        return jsonify({'error': 'No PDF loaded'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/save', methods=['POST'])
def save_pdf():
    """Save PDF with annotations and page modifications"""
    try:
        data = request.get_json()
        flatten = data.get('flatten', False)
        pages_data = data.get('pages', [])
        annotations = data.get('annotations', [])
        original_filename = data.get('originalFilename')
        
        global pdf_handler, current_session
        
        # Get text boxes from request (sent by frontend) or fallback to session
        text_boxes = data.get('textBoxes', {})
        if not text_boxes and current_session and 'textBoxes' in current_session:
            text_boxes = current_session['textBoxes']
        
        print(f"\n{'='*60}")
        print(f"SAVE REQUEST")
        print(f"{'='*60}")
        print(f"Original filename from frontend: {original_filename}")
        print(f"PDF handler exists: {pdf_handler is not None}")
        print(f"Session exists: {current_session is not None}")
        print(f"\nAnnotations received (type={type(annotations)}, len={len(annotations) if isinstance(annotations, (list, dict)) else 'N/A'}):")
        print(f"  Data: {annotations}")
        print(f"\nText boxes from session (type={type(text_boxes)}, len={len(text_boxes) if isinstance(text_boxes, (list, dict)) else 'N/A'}):")
        print(f"  Data: {text_boxes}")
        
        # Check the uploads folder contents RIGHT NOW
        print(f"\nUploads folder: {os.path.abspath(UPLOAD_FOLDER)}")
        print(f"Uploads folder exists: {os.path.exists(UPLOAD_FOLDER)}")
        
        if os.path.exists(UPLOAD_FOLDER):
            files_in_folder = os.listdir(UPLOAD_FOLDER)
            print(f"Files in uploads folder ({len(files_in_folder)} total):")
            for f in files_in_folder:
                full_path = os.path.join(UPLOAD_FOLDER, f)
                size = os.path.getsize(full_path) if os.path.isfile(full_path) else 0
                print(f"  - {f} ({size} bytes)")
        else:
            print("Uploads folder does NOT exist!")
        
        # If session is still valid, just use it
        if pdf_handler is not None and current_session is not None:
            print(f"\n✓ Session is valid, using stored filepath:")
            print(f"  Filepath: {current_session.get('filepath')}")
            file_exists = os.path.isfile(current_session.get('filepath', ''))
            print(f"  File exists: {file_exists}")
        else:
            print(f"\n✗ Session is lost, attempting recovery...")
            
            if not original_filename:
                print("ERROR: No filename provided by frontend")
                return jsonify({
                    'error': 'Cannot recover session - no filename provided. Please reload and upload the PDF again.'
                }), 400
            
            # Search for the file
            found_file = None
            if os.path.exists(UPLOAD_FOLDER):
                print(f"Searching for file ending with: {original_filename}")
                for filename in os.listdir(UPLOAD_FOLDER):
                    if filename.endswith(original_filename):
                        found_file = os.path.join(UPLOAD_FOLDER, filename)
                        print(f"✓ Found: {found_file}")
                        break
                    else:
                        print(f"  No match: {filename} does not end with {original_filename}")
            
            if not found_file or not os.path.isfile(found_file):
                files_in_folder = []
                if os.path.exists(UPLOAD_FOLDER):
                    files_in_folder = os.listdir(UPLOAD_FOLDER)
                
                error_msg = f'PDF file not found. Looking for: "{original_filename}". '
                if files_in_folder:
                    error_msg += f'Available files: {", ".join(files_in_folder[:5])}'
                else:
                    error_msg += 'The uploads folder is empty.'
                
                print(f"ERROR: {error_msg}")
                return jsonify({'error': error_msg}), 400
            
            # Recover the session
            try:
                print(f"Recovering from: {found_file}")
                pdf_handler = PDFHandler(found_file)
                page_count = pdf_handler.get_page_count()
                current_session = {
                    'filename': os.path.basename(found_file),
                    'filepath': found_file,
                    'originalFilename': original_filename,
                    'pageCount': page_count,
                    'pages': [{'index': i, 'rotation': 0, 'deleted': False} for i in range(page_count)],
                    'annotations': {},
                    'textBoxes': {},
                }
                print(f"✓ Session recovered. Pages: {page_count}")
            except Exception as e:
                print(f"ERROR recovering session: {str(e)}")
                return jsonify({'error': f'Failed to recover PDF: {str(e)}'}), 400
        
        # Validate pages
        if not pages_data:
            return jsonify({'error': 'No page data provided'}), 400
        
        # Filter deleted pages
        pages_to_export = []
        for page_info in pages_data:
            page_num = page_info.get('pageNum')
            is_deleted = page_info.get('deleted', False)
            
            if is_deleted or page_num is None:
                continue
            
            # pageNum is 1-indexed from frontend, convert to 0-indexed
            orig_page_idx = page_num - 1
            
            # Validate page index against actual PDF page count
            if orig_page_idx < 0 or orig_page_idx >= pdf_handler.get_page_count():
                print(f"ERROR: Invalid page index {orig_page_idx} (PDF has {pdf_handler.get_page_count()} pages, received pageNum={page_num})")
                return jsonify({'error': f'Invalid page index {page_num}'}), 400
            
            pages_to_export.append((orig_page_idx, page_info))
        
        if not pages_to_export:
            return jsonify({'error': 'Cannot save: all pages have been deleted.'}), 400
        
        print(f"\nExporting {len(pages_to_export)} pages (from {len(pages_data)} total)")
        
        # Create output PDF
        from pdf_exporter import PDFExporter
        exporter = PDFExporter(pdf_handler)
        pdf_buffer = exporter.export(
            pages_to_export,
            annotations,
            text_boxes,
            flatten=flatten,
        )
        
        print(f"✓ Export successful: {pdf_buffer.tell()} bytes in memory")
        
        # Clean up the uploaded file
        uploaded_filepath = current_session.get('filepath')
        if uploaded_filepath and os.path.isfile(uploaded_filepath):
            try:
                os.remove(uploaded_filepath)
                print(f"✓ Cleaned up uploaded file: {uploaded_filepath}")
            except Exception as cleanup_error:
                print(f"⚠ Warning: Failed to delete uploaded file: {cleanup_error}")
        
        print(f"{'='*60}\n")
        
        # Send BytesIO buffer directly as PDF response using response object
        pdf_buffer.seek(0)
        pdf_data = pdf_buffer.read()
        
        response = app.response_class(
            response=pdf_data,
            status=200,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="edited_{current_session.get("originalFilename", "document.pdf")}"'
            }
        )
        return response
        
    except Exception as e:
        error_msg = str(e)
        print(f"SAVE ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        return jsonify({'error': f'Failed to save PDF: {error_msg}'}), 500


@app.route('/api/session', methods=['GET'])
def get_session():
    """Get current session"""
    try:
        if current_session is None:
            return jsonify({'error': 'No session active'}), 400
        
        return jsonify(current_session), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/debug/uploads', methods=['GET'])
def debug_uploads():
    """Debug endpoint: list all files in uploads folder"""
    try:
        uploads_path = os.path.abspath(UPLOAD_FOLDER)
        exists = os.path.exists(uploads_path)
        
        files_list = []
        if exists:
            for filename in os.listdir(uploads_path):
                full_path = os.path.join(uploads_path, filename)
                if os.path.isfile(full_path):
                    size = os.path.getsize(full_path)
                    files_list.append({
                        'name': filename,
                        'size': size,
                        'exists': True
                    })
        
        return jsonify({
            'uploads_folder': uploads_path,
            'folder_exists': exists,
            'file_count': len(files_list),
            'files': files_list,
            'global_pdf_handler': pdf_handler is not None,
            'global_session': current_session is not None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001, use_reloader=False)
