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


@app.route('/api/save', methods=['POST'])
def save_pdf():
    """Save PDF with annotations and page modifications"""
    try:
        data = request.get_json()
        flatten = data.get('flatten', False)
        pages_data = data.get('pages', [])
        annotations = data.get('annotations', [])
        text_boxes = data.get('textBoxes', [])
        original_filename = data.get('originalFilename')
        
        global pdf_handler, current_session
        
        print(f"\n{'='*60}")
        print(f"SAVE REQUEST")
        print(f"{'='*60}")
        print(f"Original filename from frontend: {original_filename}")
        print(f"PDF handler exists: {pdf_handler is not None}")
        print(f"Session exists: {current_session is not None}")
        
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
            
            pages_to_export.append((page_num - 1, page_info))
        
        if not pages_to_export:
            return jsonify({'error': 'Cannot save: all pages have been deleted.'}), 400
        
        print(f"\nExporting {len(pages_to_export)} pages (from {len(pages_data)} total)")
        
        # Create output PDF
        from pdf_exporter import PDFExporter
        exporter = PDFExporter(pdf_handler)
        output_path = exporter.export(
            pages_to_export,
            annotations,
            text_boxes,
            flatten=flatten,
        )
        
        print(f"✓ Export successful: {output_path}")
        
        # Clean up the uploaded file
        uploaded_filepath = current_session.get('filepath')
        if uploaded_filepath and os.path.isfile(uploaded_filepath):
            try:
                os.remove(uploaded_filepath)
                print(f"✓ Cleaned up uploaded file: {uploaded_filepath}")
            except Exception as cleanup_error:
                print(f"⚠ Warning: Failed to delete uploaded file: {cleanup_error}")
        
        print(f"{'='*60}\n")
        
        return send_file(
            output_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"edited_{current_session.get('originalFilename', 'document.pdf')}",
        ), 200
        
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
    app.run(debug=True, host='127.0.0.1', port=5000)
