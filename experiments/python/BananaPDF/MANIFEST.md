# BananaPDF - File Structure & Purpose

## Project Files

### Core Application Files

#### app.py
- **Purpose**: Flask web server and REST API
- **Size**: ~400 lines
- **Key Classes**: None (module functions)
- **Key Functions**:
  - `upload_pdf()` - PDF upload handling
  - `render_page()` - Page rendering endpoint
  - `add_annotation()` - Annotation creation
  - `add_textbox()` - Text box creation
  - `rotate_page()` - Page rotation
  - `delete_page()` - Page deletion
  - `reorder_pages()` - Page reordering
  - `export_pdf()` - PDF export endpoint
- **Dependencies**: Flask, CORS, werkzeug, pdf_handler, annotation_manager, pdf_exporter

#### pdf_handler.py
- **Purpose**: PDF rendering and page operations
- **Size**: ~150 lines
- **Key Classes**:
  - `PDFHandler` - Main PDF manipulation class
- **Key Methods**:
  - `__init__()` - Initialize with PDF file
  - `get_page_count()` - Return page count
  - `render_page()` - Render page to PNG
  - `get_page_dimensions()` - Get page size
  - `extract_text()` - Extract text from page
  - `get_page_as_image()` - Get PIL Image
- **Dependencies**: pypdf, PyMuPDF, Pillow

#### annotation_manager.py
- **Purpose**: Manage annotations in memory
- **Size**: ~100 lines
- **Key Classes**:
  - `AnnotationManager` - Annotation storage
- **Key Methods**:
  - `add_annotation()` - Create annotation
  - `update_annotation()` - Modify annotation
  - `delete_annotation()` - Remove annotation
  - `get_annotations_for_page()` - Query by page
  - `get_all_annotations()` - Get all annotations
- **Dependencies**: uuid, datetime

#### pdf_exporter.py
- **Purpose**: Generate output PDF with annotations
- **Size**: ~200 lines
- **Key Classes**:
  - `PDFExporter` - PDF generation
- **Key Methods**:
  - `export()` - Generate final PDF
  - `_add_annotation_to_page()` - Draw annotation
  - `_add_textbox_to_page()` - Add text box
  - `_hex_to_rgb()` - Color conversion
- **Dependencies**: PyMuPDF, os, datetime

### Configuration Files

#### requirements.txt
- Lists all Python dependencies
- Flask, Flask-CORS, pypdf, PyMuPDF, Pillow, python-multipart
- Used by: `pip install -r requirements.txt`

#### README.md
- Comprehensive project documentation
- Features list
- Installation instructions
- Usage guide
- API endpoints
- Known limitations
- Future enhancements

#### QUICKSTART.md
- 5-minute quick start guide
- Common tasks
- Tips and tricks
- Troubleshooting

#### IMPLEMENTATION.md
- Architecture overview
- Component breakdown
- Data flow diagrams
- API reference
- Extension guide
- Performance optimization tips
- Deployment options
- Testing strategies

#### MANIFEST.md (optional)
- Project overview and status
- Key features completed
- Known issues
- File manifest

### Frontend Files

#### templates/index.html
- **Purpose**: Main application interface
- **Size**: ~300 lines
- **Key Sections**:
  - Toolbar (file, view, annotate, edit, pages, security, tools)
  - Left Panel (thumbnails)
  - Center Panel (PDF viewer)
  - Right Panel (document info, annotations)
  - Status Bar
  - Modals (text input, comment input)
- **Libraries**: PDF.js (CDN)

#### static/css/style.css
- **Purpose**: Application styling
- **Size**: ~500 lines
- **Key Sections**:
  - Root variables (colors, typography)
  - Toolbar styles
  - Button styles
  - Layout styles
  - Modal styles
  - Responsive design
  - Accessibility styles
  - Print styles

#### static/js/main.js
- **Purpose**: Client-side application logic
- **Size**: ~600 lines
- **Key Classes**:
  - `PDFEditor` - Main application class
- **Key Methods**:
  - `loadPDF()` - Load PDF with PDF.js
  - `renderPage()` - Render page to canvas
  - `generateThumbnails()` - Create thumbnails
  - `selectTool()` - Activate tool
  - `handleCanvasClick()` - Tool interactions
  - `addAnnotation()` - Call API to add annotation
  - `addTextBox()` - Call API to add text
  - `exportPDF()` - Download edited PDF
- **Dependencies**: PDF.js (client-side)

### Startup Scripts

#### START.bat
- **Purpose**: Windows startup script
- **Features**:
  - Check Python installation
  - Create virtual environment
  - Install dependencies
  - Start Flask server
- **Usage**: Double-click to run

#### start.sh
- **Purpose**: macOS/Linux startup script
- **Features**: Same as START.bat but for Unix systems
- **Usage**: `chmod +x start.sh && ./start.sh`

### Runtime Directories (Created at Runtime)

#### uploads/
- **Purpose**: Temporary PDF storage
- **Contents**: Uploaded PDF files
- **Cleanup**: Can be cleared periodically

#### exports/
- **Purpose**: Generated PDF storage
- **Contents**: Exported PDFs with annotations
- **Cleanup**: Can be cleared periodically

#### venv/ (after running START.bat/start.sh)
- **Purpose**: Python virtual environment
- **Contents**: Installed dependencies

## File Statistics

### Code Files
- Python: ~850 lines (4 main files)
- JavaScript: ~600 lines (1 file)
- HTML: ~300 lines (1 file)
- CSS: ~500 lines (1 file)
- **Total: ~2,250 lines of code**

### Documentation Files
- README.md: ~400 lines
- QUICKSTART.md: ~100 lines
- IMPLEMENTATION.md: ~400 lines
- MANIFEST.md: ~50 lines (optional)
- **Total: ~950 lines of documentation**

### Configuration Files
- requirements.txt: 6 lines
- START.bat: 40 lines
- start.sh: 35 lines
- **Total: ~80 lines**

## File Dependencies

```
app.py
├── pdf_handler.py
├── annotation_manager.py
├── pdf_exporter.py
├── Flask
├── Flask-CORS
├── werkzeug
└── templates/index.html

pdf_handler.py
├── pypdf
├── PyMuPDF
└── Pillow

pdf_exporter.py
├── PyMuPDF
├── os
└── datetime

annotation_manager.py
├── uuid
└── datetime

templates/index.html
└── static/
    ├── css/style.css
    ├── js/main.js
    └── PDF.js (CDN)

static/js/main.js
├── PDF.js (CDN)
└── Flask API (app.py)
```

## Deployment Files

For production deployment, you may need to add:

- `wsgi.py` - WSGI entry point for Gunicorn
- `Dockerfile` - Docker containerization
- `.gitignore` - Git ignore rules
- `config.py` - Configuration management
- `nginx.conf` - Nginx reverse proxy config
- `supervisord.conf` - Process management

## Testing Files (Not Yet Implemented)

Future additions for comprehensive testing:

- `tests/test_pdf_handler.py` - Unit tests for PDF handling
- `tests/test_annotation_manager.py` - Annotation tests
- `tests/test_pdf_exporter.py` - Export tests
- `tests/test_api.py` - API endpoint tests
- `tests/conftest.py` - Test configuration
- `tests/fixtures/sample.pdf` - Test PDF file

## Development Checklist

- [x] Core API implementation
- [x] PDF rendering backend
- [x] Annotation management
- [x] PDF export with annotations
- [x] Frontend HTML structure
- [x] Frontend CSS styling
- [x] Frontend JavaScript logic
- [x] File upload handling
- [x] Page navigation
- [x] Zoom controls
- [x] Annotation tools (highlight, text, comment)
- [x] Page rotation
- [x] Page deletion
- [x] PDF export
- [x] Documentation (README, QUICKSTART, IMPLEMENTATION)
- [x] Startup scripts
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests
- [ ] Error handling improvements
- [ ] Performance optimization
- [ ] Drawing tool
- [ ] Signature tool
- [ ] OCR integration
- [ ] Search functionality
- [ ] Form field detection
- [ ] Redaction tool
- [ ] Cloud storage integration

## Notes

### Important Observations

1. **Temporary Files**: The `uploads/` and `exports/` directories should be periodically cleaned up in production
2. **Session Management**: Currently uses global variables; consider persistent sessions for multi-user
3. **File Security**: Input validation is basic; add more robust checks for production
4. **Error Handling**: Generic error messages shown to users; expand error handling
5. **Logging**: No logging implemented; add logging for debugging
6. **Testing**: No test suite yet; create comprehensive tests before production

### Performance Notes

1. Thumbnail generation is synchronous - consider async generation
2. Large PDFs may cause memory issues - implement streaming
3. Annotation rendering is immediate - consider debouncing
4. No caching of rendered pages - implement caching strategy

### Security Notes

1. File uploads are not thoroughly validated - add file integrity checks
2. No authentication/authorization - add user management for production
3. No rate limiting - add to prevent abuse
4. PDF content is not sanitized - handle malicious PDFs gracefully
5. Session data stored in memory - implement persistent storage

---

**Generated**: May 2026
**Status**: MVP Complete, Ready for Testing
