# BananaPDF Implementation Guide

## Architecture Overview

BananaPDF uses a three-tier architecture:

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (Browser)                 │
│  HTML5 + CSS3 + JavaScript (PDF.js for rendering)   │
└─────────────────┬───────────────────────────────────┘
                  │ HTTP/JSON API
┌─────────────────▼───────────────────────────────────┐
│               Backend (Flask Server)                 │
│  REST API endpoints for PDF operations              │
└─────────────────┬───────────────────────────────────┘
                  │ File I/O
┌─────────────────▼───────────────────────────────────┐
│               PDF Processing Layer                   │
│  PyMuPDF (fitz) + pypdf for PDF manipulation        │
└─────────────────────────────────────────────────────┘
```

## Component Breakdown

### Backend Components

#### 1. app.py (Flask Application)
**Responsibility**: REST API endpoints and request handling

**Key Functions**:
- `upload_pdf()` - Handle PDF uploads
- `render_page()` - Render PDF page as image
- `add_annotation()` - Add annotation to PDF
- `add_textbox()` - Add text box to PDF
- `rotate_page()` - Rotate page
- `delete_page()` - Mark page for deletion
- `export_pdf()` - Export edited PDF
- `get_session()` - Return current session state

**Session Management**:
```python
current_session = {
    'filename': str,           # Temp filename
    'filepath': str,           # Full path
    'originalFilename': str,   # Original name
    'pageCount': int,
    'isModified': bool,
    'pages': [                 # Page metadata
        {'index': int, 'rotation': int, 'deleted': bool}
    ],
    'annotations': {},         # {pageNum: [annotation]}
    'textBoxes': {},          # {id: textbox}
}
```

#### 2. pdf_handler.py (PDF Rendering)
**Responsibility**: Low-level PDF rendering and metadata

**Key Methods**:
- `__init__(filepath)` - Load PDF
- `get_page_count()` - Return number of pages
- `render_page(page_num, rotation, zoom)` - Render page to PNG
- `get_page_dimensions(page_num)` - Get page size
- `extract_text(page_num)` - Extract text content
- `get_page_as_image(page_num, dpi)` - Get PIL Image

**Libraries Used**:
- `PyMuPDF (fitz)`: High-quality PDF rendering
- `pypdf`: PDF reading and basic operations

#### 3. annotation_manager.py (Annotation Storage)
**Responsibility**: In-memory annotation management

**Key Methods**:
- `add_annotation(data)` - Create new annotation
- `update_annotation(id, data)` - Modify annotation
- `delete_annotation(id)` - Remove annotation
- `get_annotations_for_page(page_num)` - Query annotations
- `get_all_annotations()` - Return all annotations

**Annotation Types**:
- `highlight` - Yellow highlight over text
- `comment` - Comment bubble with text
- `rectangle` - Rectangle shape
- `circle` - Circle shape
- `line` - Line or arrow
- `freehand` - Free-drawn path
- `text` - Text overlay
- `signature` - Signature image

#### 4. pdf_exporter.py (PDF Generation)
**Responsibility**: Create final PDF with annotations

**Key Methods**:
- `export(pages, annotations, textboxes, flatten)` - Generate PDF
- `_add_annotation_to_page()` - Draw annotation on page
- `_add_textbox_to_page()` - Add text box to page

**Process Flow**:
1. Open original PDF with PyMuPDF
2. Create new empty document
3. For each page to export:
   - Copy page from original
   - Apply rotation
   - Add annotations
   - Add text boxes
4. Save to output file

### Frontend Components

#### 1. index.html (Main Interface)
**Structure**:
- Toolbar (file, view, annotate, edit, pages, security, tools)
- Left Panel (thumbnails)
- Center Panel (PDF viewer canvas + annotation layer)
- Right Panel (document info, annotations list)
- Status Bar (messages)
- Modals (text input, comment input)

#### 2. style.css (Styling)
**Key Styles**:
- Flexbox layout for responsive design
- Dark theme for PDF viewer background
- Tool buttons with active state
- Modal dialogs with overlay
- Thumbnail selection with active border

#### 3. main.js (Application Logic)
**PDFEditor Class**:
```javascript
class PDFEditor {
    // Core state
    pdfDoc              // PDF.js document
    currentPage         // Current page number (1-based)
    zoomLevel           // Zoom percentage
    currentTool         // Active tool ('highlight', 'text', etc.)
    annotations         // {pageNum: [annotation]}
    textBoxes          // {id: textbox}
    isModified         // Has user made changes?
    
    // Methods
    loadPDF()          // Load PDF from file
    renderPage()       // Render page to canvas
    handleCanvasClick()// Tool interaction
    addAnnotation()    // Add annotation via API
    addTextBox()       // Add text box via API
    exportPDF()        // Download edited PDF
    selectTool()       // Activate tool
}
```

**PDF.js Integration**:
- Uses PDF.js to render PDFs client-side
- Worker thread for background rendering
- Supports zoom and rotation

## Data Flow

### Opening a PDF

```
User Click "Open"
    ↓
File Input Dialog
    ↓
User Selects PDF
    ↓
handleFileSelect()
    ↓
FormData with file
    ↓
POST /api/upload
    ↓
app.py: Save file → Initialize handlers
    ↓
Return page count and metadata
    ↓
JavaScript: Load PDF with PDF.js
    ↓
Render first page
    ↓
Generate thumbnails
    ↓
Enable controls
```

### Adding Annotation

```
User Selects Tool (e.g., "Highlight")
    ↓
selectTool('highlight')
    ↓
User Clicks Canvas
    ↓
handleCanvasClick()
    ↓
Determine click position
    ↓
POST /api/add-annotation
    ↓
app.py: Create annotation
    ↓
annotation_manager.add_annotation()
    ↓
Return annotation data
    ↓
Store in current_session['annotations']
    ↓
JavaScript: renderAnnotations()
    ↓
Draw annotation overlay on page
    ↓
Update right panel list
```

### Exporting PDF

```
User Clicks "Export"
    ↓
POST /api/export
    ↓
app.py: Get session data
    ↓
pdf_exporter.export()
    ↓
For each active page:
    - Copy from original PDF
    - Apply rotation
    - Add annotations
    - Add text boxes
    ↓
Save to exports/ folder
    ↓
Return as attachment
    ↓
Browser downloads PDF
```

## API Reference

### POST /api/upload
Upload a PDF file

**Request**:
- Multipart form data with 'file' field (PDF file)

**Response**:
```json
{
    "success": true,
    "session": {...},
    "pageCount": 10
}
```

### POST /api/render-page/<page_num>
Render a page as PNG image

**Response**: PNG image file

### POST /api/add-annotation
Add annotation to page

**Request**:
```json
{
    "pageNum": 0,
    "type": "highlight",
    "x": 100,
    "y": 150,
    "width": 100,
    "height": 30,
    "color": "#FFFF00",
    "text": "Comment text"
}
```

**Response**:
```json
{
    "success": true,
    "annotation": {...}
}
```

### POST /api/add-textbox
Add text box to page

**Request**:
```json
{
    "pageNum": 0,
    "x": 100,
    "y": 150,
    "text": "Your text here",
    "fontSize": 12,
    "color": "#000000"
}
```

### POST /api/rotate-page
Rotate page 90 degrees clockwise

**Request**:
```json
{
    "pageNum": 0
}
```

### POST /api/delete-page
Mark page for deletion

**Request**:
```json
{
    "pageNum": 0
}
```

### POST /api/export
Export PDF with all modifications

**Request**:
```json
{
    "flatten": false
}
```

**Response**: PDF file attachment

## Extending BananaPDF

### Adding a New Annotation Type

1. **Update annotation_manager.py**:
```python
def add_drawing_annotation(self, data):
    annotation = {
        'id': str(uuid.uuid4()),
        'type': 'drawing',
        'pageNum': data['pageNum'],
        'points': data['points'],  # List of [x, y] coordinates
        'color': data.get('color', '#000000'),
        'strokeWidth': data.get('strokeWidth', 2),
        # ... other fields
    }
    self.annotations[annotation['id']] = annotation
    return annotation
```

2. **Update pdf_exporter.py**:
```python
def _add_annotation_to_page(self, page, annotation):
    # ... existing code ...
    elif annotation['type'] == 'drawing':
        points = annotation['points']
        for i in range(len(points) - 1):
            p1 = fitz.Point(points[i][0], points[i][1])
            p2 = fitz.Point(points[i+1][0], points[i+1][1])
            page.draw_line(p1, p2, color=color_normalized, width=width)
```

3. **Update app.py** - Add API endpoint if needed

4. **Update main.js** - Add tool selection and canvas interaction

### Adding OCR Support

1. Install Tesseract.js:
```bash
pip install pytesseract
# Install Tesseract binary
```

2. Create ocr_handler.py:
```python
class OCRHandler:
    def process_page(self, image):
        # Use pytesseract to extract text
        text = pytesseract.image_to_string(image)
        return text
```

3. Add API endpoint in app.py

4. Integrate into frontend

### Adding Drawing Tool

1. Create canvas-based drawing in main.js
2. Track mouse events on canvas
3. Store path points
4. Send to annotation API
5. Render in export

## Performance Optimization

### Current Bottlenecks
1. Large PDF thumbnail generation
2. Full page rendering on zoom
3. Annotation rendering with many items

### Optimization Strategies
1. **Lazy Loading**: Generate thumbnails in background
2. **Canvas Caching**: Cache rendered pages
3. **Virtual Scrolling**: Only render visible thumbnails
4. **Worker Threads**: Offload heavy computations
5. **Progressive Rendering**: Show low-quality first

### Recommended Improvements
```javascript
// Implement virtual scrolling for thumbnails
const thumbnailObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            renderThumbnail(entry.target);
        }
    });
});
```

## Security Considerations

1. **File Upload Validation**:
   - Check MIME type
   - Validate PDF header
   - Limit file size
   - Sanitize filenames

2. **Input Sanitization**:
   - Escape text in annotations
   - Validate coordinate values
   - Check page numbers

3. **Server Storage**:
   - Use temporary directories
   - Clean up after export
   - Don't store PDFs permanently

## Testing

### Unit Tests (Add to test_suite.py)
```python
def test_pdf_upload():
    # Test valid PDF upload
    
def test_annotation_creation():
    # Test annotation storage
    
def test_pdf_export():
    # Test PDF generation
```

### Integration Tests
```javascript
// Test PDF loading in browser
// Test annotation rendering
// Test export download
```

### Manual Testing
1. Upload various PDF types
2. Add annotations to different pages
3. Rotate and delete pages
4. Export and verify in Adobe Reader
5. Test with large PDFs (100+ pages)

## Deployment

### Development
```bash
python app.py
```

### Production (with Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Troubleshooting Guide

### Issue: PDF.js Worker Not Loading
**Solution**: Ensure CDN link in index.html is correct

### Issue: Annotations Not Saving
**Solution**: Check session management in app.py

### Issue: Export Fails
**Solution**: Check PyMuPDF version compatibility

## Future Roadmap

**Phase 2**:
- Form field detection and filling
- Redaction with proper safety checks
- Merge and extract pages UI

**Phase 3**:
- OCR integration
- Search functionality
- Undo/Redo history

**Phase 4**:
- Cloud storage integration
- Collaboration features
- Mobile app

---

For questions or contributions, refer to the main README.md file.
