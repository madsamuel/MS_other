"""BananaPDF - A comprehensive PDF editor"""
import os
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pdf_handler import PDFHandler
from annotation_manager import AnnotationManager

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

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
        file.save(filepath)
        
        # Initialize PDF handler and annotation manager
        global pdf_handler, annotation_manager, current_session
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
        if pdf_handler is None:
            return jsonify({'error': 'No PDF loaded'}), 400
        
        return jsonify({
            'pageCount': pdf_handler.get_page_count(),
            'fileName': current_session['originalFilename'],
            'filePath': current_session['filename'],
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
    """Add text box to PDF"""
    try:
        data = request.get_json()
        textbox = {
            'id': f"text_{len(current_session['textBoxes'])}",
            'pageNum': data.get('pageNum'),
            'x': data.get('x'),
            'y': data.get('y'),
            'width': data.get('width', 150),
            'height': data.get('height', 30),
            'text': data.get('text', ''),
            'fontSize': data.get('fontSize', 12),
            'fontFamily': data.get('fontFamily', 'Arial'),
            'color': data.get('color', '#000000'),
            'createdAt': datetime.now().isoformat(),
        }
        
        if current_session:
            current_session['textBoxes'][textbox['id']] = textbox
            current_session['isModified'] = True
        
        return jsonify({
            'success': True,
            'textbox': textbox,
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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


@app.route('/api/export', methods=['POST'])
def export_pdf():
    """Export PDF with annotations"""
    try:
        data = request.get_json()
        flatten = data.get('flatten', False)
        
        if pdf_handler is None or current_session is None:
            return jsonify({'error': 'No PDF loaded'}), 400
        
        # Create output PDF
        from pdf_exporter import PDFExporter
        exporter = PDFExporter(pdf_handler)
        
        # Apply page operations
        pages_to_export = [
            (i, current_session['pages'][i])
            for i in range(len(current_session['pages']))
            if not current_session['pages'][i].get('deleted', False)
        ]
        
        # Export with annotations
        output_path = exporter.export(
            pages_to_export,
            current_session['annotations'],
            current_session['textBoxes'],
            flatten=flatten,
        )
        
        return send_file(
            output_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"edited_{current_session['originalFilename']}",
        ), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/session', methods=['GET'])
def get_session():
    """Get current session"""
    try:
        if current_session is None:
            return jsonify({'error': 'No session active'}), 400
        
        return jsonify(current_session), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
