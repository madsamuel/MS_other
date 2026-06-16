"""BananaPDF - A comprehensive PDF editor (Refactored with SOLID principles)"""
import os
import io
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from services import PDFService, AnnotationService, FileService, ExportService
from models import annotation_factory

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flask_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize services with dependency injection (Dependency Inversion)
file_service = FileService(UPLOAD_FOLDER)
annotation_service = AnnotationService()
pdf_service = PDFService()
export_service = ExportService('exports')

# Session state (this could be moved to a SessionRepository)
current_session = None


def _create_session(filepath: str, original_filename: str) -> dict:
    """Create a new session (Single Responsibility extracted)"""
    page_count = pdf_service.get_page_count()
    return {
        'filename': os.path.basename(filepath),
        'filepath': filepath,
        'originalFilename': original_filename,
        'pageCount': page_count,
        'isModified': False,
        'createdAt': datetime.now().isoformat(),
        'pages': [{'index': i, 'rotation': 0, 'deleted': False} for i in range(page_count)],
    }


def _validate_page_number(page_num: int) -> bool:
    """Validate page number (Single Responsibility extracted)"""
    if pdf_service.is_loaded():
        return 0 <= page_num < pdf_service.get_page_count()
    return False


@app.route('/')
def index():
    """Serve main app"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF upload (Dependency Inversion: uses injected services)"""
    try:
        global current_session
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file using FileService
        filepath = file_service.save_uploaded_file(file, file.filename)
        logger.info(f"File saved: {filepath}")
        
        # Load PDF using PDFService
        page_count = pdf_service.load_pdf(filepath)
        
        # Create session
        current_session = _create_session(filepath, file.filename)
        
        # Reset annotation service
        annotation_service._annotations = {}
        
        logger.info(f"Upload successful: {page_count} pages")
        
        return jsonify({
            'success': True,
            'pageCount': page_count,
            'originalFilename': file.filename,
        }), 200
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/get-pdf', methods=['GET'])
def get_pdf():
    """Get PDF page (delegated to pdf_service)"""
    try:
        if not pdf_service.is_loaded():
            return jsonify({'error': 'No PDF loaded'}), 400
        
        page_num = request.args.get('pageNum', 0, type=int)
        
        if not _validate_page_number(page_num):
            return jsonify({'error': f'Invalid page number: {page_num}'}), 400
        
        # Get PDF from PDFService
        pdf_handler = pdf_service.get_handler()
        img_path = pdf_handler.render_page(page_num)
        
        if not os.path.isfile(img_path):
            return jsonify({'error': 'Failed to render page'}), 500
        
        with open(img_path, 'rb') as f:
            img_data = f.read()
        
        return img_data, 200, {'Content-Type': 'image/png'}
        
    except Exception as e:
        logger.error(f"Get PDF failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/page-dimensions/<int:page_num>', methods=['GET'])
def get_page_dimensions(page_num):
    """Get page dimensions (delegated to pdf_service)"""
    try:
        if not pdf_service.is_loaded():
            return jsonify({'error': 'No PDF loaded'}), 400
        
        if not _validate_page_number(page_num):
            return jsonify({'error': f'Invalid page number: {page_num}'}), 400
        
        # Get dimensions from PDFService
        pdf_handler = pdf_service.get_handler()
        page = pdf_handler.doc[page_num]
        rect = page.rect
        
        return jsonify({
            'width': rect.width,
            'height': rect.height,
            'pageNum': page_num,
        }), 200
        
    except Exception as e:
        logger.error(f"Get page dimensions failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/add-annotation', methods=['POST'])
def add_annotation():
    """Add annotation (uses AnnotationService)"""
    try:
        data = request.get_json()
        
        # Validate page
        page_num = data.get('pageNum', 0)
        if not _validate_page_number(page_num):
            return jsonify({'error': f'Invalid page number: {page_num}'}), 400
        
        # Add annotation using AnnotationService
        annotation = annotation_service.add_annotation(data)
        
        logger.info(f"Added annotation: {annotation.id} ({annotation.__class__.__name__})")
        
        return jsonify({
            'success': True,
            'annotation': annotation.to_dict(),
        }), 200
        
    except ValueError as ve:
        logger.warning(f"Invalid annotation: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logger.error(f"Add annotation failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/save', methods=['POST'])
def save_pdf():
    """Save PDF with annotations (orchestrates multiple services)"""
    try:
        global current_session
        
        data = request.get_json()
        pages_data = data.get('pages', [])
        annotations_data = data.get('annotations', {})
        textboxes_data = data.get('textBoxes', {})
        original_filename = data.get('originalFilename')
        
        logger.info(f"Save request for: {original_filename}")
        
        # Validate session
        if not current_session:
            return jsonify({'error': 'No active session'}), 400
        
        if not pdf_service.is_loaded():
            return jsonify({'error': 'No PDF loaded'}), 400
        
        # Validate pages
        pages_to_export = []
        for page_info in pages_data:
            page_num = page_info.get('pageNum', 0)
            if not _validate_page_number(page_num - 1):  # Frontend uses 1-indexed
                return jsonify({'error': f'Invalid page number: {page_num}'}), 400
            
            if not page_info.get('deleted', False):
                pages_to_export.append((page_num - 1, page_info))
        
        if not pages_to_export:
            return jsonify({'error': 'All pages have been deleted'}), 400
        
        # Get current annotations
        current_annotations = annotation_service.get_all_annotations()
        
        # Use ExportService to export PDF (orchestration)
        logger.info(f"Exporting {len(pages_to_export)} pages...")
        output_path = export_service.export_pdf(
            pdf_service.get_handler(),
            pages_to_export,
            current_annotations,
            textboxes_data,
            flatten=data.get('flatten', False),
        )
        
        # Read file into memory to avoid locking issues
        logger.info(f"Reading exported file: {output_path}")
        file_data = file_service.read_file(output_path)
        
        # Clean up uploaded file
        if current_session['filepath']:
            file_service.cleanup_file(current_session['filepath'])
        
        # Return file to user
        file_stream = io.BytesIO(file_data)
        download_name = f"edited_{current_session['originalFilename']}"
        
        logger.info(f"Sending file to client: {download_name} ({len(file_data)} bytes)")
        
        return send_file(
            file_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=download_name,
        ), 200
        
    except ValueError as ve:
        logger.warning(f"Save validation failed: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logger.error(f"Save failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to save PDF: {str(e)}'}), 500


@app.route('/api/reset-session', methods=['POST'])
def reset_session():
    """Reset session and cleanup (orchestrates multiple services)"""
    try:
        global current_session
        
        # Cleanup uploaded file
        if current_session and current_session.get('filepath'):
            file_service.cleanup_file(current_session['filepath'])
        
        # Reset services
        pdf_service.close()
        annotation_service._annotations = {}
        current_session = None
        
        logger.info("Session reset")
        return jsonify({'message': 'Session reset'}), 200
        
    except Exception as e:
        logger.error(f"Reset failed: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001, use_reloader=False)
