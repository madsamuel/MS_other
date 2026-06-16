# BananaPDF Refactored - Developer Quick Reference

## 🚀 Quick Start

### Run the Application

```bash
# Backend setup
pip install flask flask-cors PyMuPDF pillow werkzeug

# Run the server
python app_refactored.py

# Open browser to http://127.0.0.1:5001
```

### Key Difference: Old vs New

| Task | Old Way | New Way |
|------|---------|---------|
| Add text | POST `/api/add-textbox` → modifies PDF | Client stores → save all at once |
| Undo/Redo | Modified PDF backend | Pure client-side state snapshots |
| File handling | Global variables | `FileService` dependency injection |
| Annotations | Generic dicts | Type-safe `Annotation` classes |

---

## 🔧 Backend Quick Reference

### Using Services

```python
from services import PDFService, AnnotationService, FileService, ExportService

# Initialize services
pdf_service = PDFService()
annotation_service = AnnotationService()
file_service = FileService('uploads')
export_service = ExportService('exports')

# Load PDF
page_count = pdf_service.load_pdf('/path/to/file.pdf')

# Add annotation
annotation = annotation_service.add_annotation({
    'type': 'text',
    'pageNum': 0,
    'x': 100,
    'y': 100,
    'text': 'Hello'
})

# Export PDF
output_path = export_service.export_pdf(
    pdf_service.get_handler(),
    pages_to_export,
    annotations_service.get_all_annotations(),
    textboxes_dict
)

# Download file
file_data = file_service.read_file(output_path)
```

### Adding New Annotation Type

```python
# 1. Create model
from models import Annotation
from dataclasses import dataclass

@dataclass
class RectangleAnnotation(Annotation):
    color: str = "#FF0000"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'pageNum': self.page_num,
            'type': 'rectangle',
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'color': self.color,
        }
    
    def validate(self) -> bool:
        return self.width > 0 and self.height > 0

# 2. Register in factory
# In models/annotation.py annotation_factory():
elif ann_type == 'rectangle':
    return RectangleAnnotation(...)

# Done! Service automatically supports new type
```

### Testing Services

```python
import pytest
from services import AnnotationService

def test_add_annotation():
    service = AnnotationService()
    ann = service.add_annotation({
        'type': 'text',
        'pageNum': 0,
        'x': 0, 'y': 0,
        'width': 100, 'height': 30,
        'text': 'Test'
    })
    assert ann.id is not None
    assert ann.text == 'Test'

def test_annotation_validation():
    service = AnnotationService()
    with pytest.raises(ValueError):
        service.add_annotation({
            'type': 'text',
            'pageNum': 0,
            'x': 0, 'y': 0,
            'width': 100, 'height': 30,
            'text': ''  # Empty text - invalid
        })
```

---

## 🎨 Frontend Quick Reference

### Using Services

```javascript
// Services are injected
const app = new PDFEditorApp({
    apiService: new APIService(),
    stateManager: new StateManager(),
    annotationManager: new ClientAnnotationManager(),
    undoRedoManager: new UndoRedoManager(),
    pdfViewer: new PDFViewer('pdfContainer', apiService),
    drawingTool: new DrawingTool('drawingOverlay'),
});

await app.initialize();
```

### Adding New Tool

```javascript
class HighlightTool {
    constructor(containerElement) {
        this.container = containerElement;
        this.isActive = false;
    }

    enable() {
        this.isActive = true;
        this.container.addEventListener('mousedown', this.handleClick.bind(this));
    }

    disable() {
        this.isActive = false;
        this.container.removeEventListener('mousedown', this.handleClick.bind(this));
    }

    handleClick(e) {
        // Implement highlight logic
    }
}

// Register in PDFEditorApp.selectTool()
if (toolId === 'highlightTool') {
    this.highlightTool = new HighlightTool(annotationLayer);
    this.highlightTool.enable();
}
```

### Testing Services

```javascript
describe('StateManager', () => {
    it('should update state immutably', () => {
        const sm = new StateManager();
        sm.setState({ currentPage: 2 });
        const state = sm.getState();
        expect(state.currentPage).toBe(2);
    });

    it('should notify listeners on state change', (done) => {
        const sm = new StateManager();
        sm.subscribe(state => {
            expect(state.currentPage).toBe(3);
            done();
        });
        sm.setState({ currentPage: 3 });
    });
});
```

### Working with Annotations

```javascript
// Add text annotation
const textBox = {
    id: `text_${Date.now()}`,
    pageNum: 0,
    type: 'text',
    x: 100,
    y: 100,
    width: 150,
    height: 30,
    text: 'Hello World',
    fontSize: 12,
    color: '#000000'
};

annotationManager.addTextBox(textBox);

// Save undo state
undoRedoManager.saveState('Add text', pageManager, annotationManager);

// Get all annotations
const allAnnotations = annotationManager.getAllAnnotations();
// { '0': [...], '1': [...] }

// Render annotations
pdfViewer.renderAnnotations(
    annotationManager.getAnnotationsForPage(0),
    annotationManager.getTextBoxesForPage(0)
);
```

---

## 📝 API Endpoint Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/upload` | POST | Upload PDF file |
| `/api/get-pdf` | GET | Get rendered PDF page |
| `/api/page-dimensions/{page_num}` | GET | Get page dimensions |
| `/api/add-annotation` | POST | Add single annotation |
| `/api/save` | POST | Save all annotations to PDF |
| `/api/reset-session` | POST | Clear session |

### Upload Request
```json
{
  "file": File  // multipart form data
}
```

### Add Annotation Request
```json
{
  "type": "text",
  "pageNum": 0,
  "x": 100,
  "y": 100,
  "width": 150,
  "height": 30,
  "text": "Hello",
  "fontSize": 12,
  "color": "#000000"
}
```

### Save Request
```json
{
  "originalFilename": "document.pdf",
  "pages": [
    {"index": 0, "rotation": 0, "deleted": false},
    {"index": 1, "rotation": 0, "deleted": false}
  ],
  "annotations": {
    "0": [
      {
        "id": "text_1234",
        "pageNum": 0,
        "type": "text",
        "x": 100,
        "y": 100,
        "width": 150,
        "height": 30,
        "text": "Hello"
      }
    ]
  },
  "textBoxes": {
    "text_1234": { ... }
  }
}
```

---

## 🐛 Common Issues & Solutions

### Backend

**Issue**: `ModuleNotFoundError: No module named 'services'`
**Solution**: Make sure you're running from BananaPDF directory and models/services packages have `__init__.py`

**Issue**: `FileNotFoundError` when saving
**Solution**: `ExportService` creates exports folder automatically. Check folder permissions.

**Issue**: Drawing appears distorted
**Solution**: Drawing uses full-page coordinates (0, 0, page_width, page_height)

### Frontend

**Issue**: Services not found in browser console
**Solution**: Make sure script tags load in correct order in HTML:
1. api-service.js
2. state-manager.js
3. annotation-manager.js
4. undo-redo-manager.js
5. pdf-viewer.js
6. drawing-tool.js
7. app.js

**Issue**: Drawing not showing
**Solution**: Check that `drawingOverlay` canvas exists and is enabled in the right tool

**Issue**: Undo/Redo not working
**Solution**: Make sure `saveState()` is called after each operation

---

## 📊 Service Dependencies

```
PDFEditorApp (Orchestrator)
├─ APIService (HTTP)
├─ StateManager (State)
├─ ClientAnnotationManager (Storage)
│  └─ Depends on: Annotation models
├─ UndoRedoManager (History)
│  └─ Depends on: PageManager, AnnotationManager
├─ PDFViewer (Rendering)
│  └─ Depends on: APIService
└─ DrawingTool (Drawing)

Backend:
app_refactored.py (Routes)
├─ PDFService
│  └─ Depends on: PDFHandler
├─ AnnotationService
│  └─ Depends on: Annotation models
├─ FileService
│  └─ Depends on: OS file operations
└─ ExportService
   ├─ Depends on: PDFExporter
   ├─ Depends on: FileService
   └─ Depends on: PDFHandler
```

---

## 🔄 Data Flow: Upload → Edit → Save

```
1. USER UPLOADS FILE
   User clicks Upload → fileInput.change event
   ↓
   PDFEditorApp.handleFileUpload()
   ↓
   apiService.upload(file)
   ↓
   POST /api/upload → FileService.save_uploaded_file()
   ↓
   PDFService.load_pdf() → app.py creates session
   ↓
   Response: { pageCount, originalFilename }
   ↓
   App renders first page via PDFViewer

2. USER ADDS ANNOTATION
   User clicks Text Tool → selectTool('textTool')
   ↓
   User enters text → addTextAnnotation()
   ↓
   Create TextAnnotation object
   ↓
   annotationManager.addTextBox(textBox)
   ↓
   pdfViewer.renderAnnotations() → updates DOM
   ↓
   undoRedoManager.saveState() → save undo point

3. USER PRESSES CTRL+Z (UNDO)
   Keyboard event → app.undo()
   ↓
   undoRedoManager.undo() → get previous snapshot
   ↓
   annotationManager.setState(previousState)
   ↓
   pdfViewer.renderAnnotations() → re-render DOM

4. USER CLICKS SAVE
   User clicks Save → app.savePDF()
   ↓
   Prepare saveData: { pages, annotations, textBoxes }
   ↓
   apiService.savePDF(saveData)
   ↓
   POST /api/save → Backend processes
   ↓
   Backend: annotation_service.get_all_annotations()
   ↓
   Backend: export_service.export_pdf()
   ↓
   Backend: Returns PDF blob
   ↓
   Frontend: Download file to user's computer
```

---

## 🎯 Architecture Principles Checklist

Use this when adding new features:

- [ ] Does my new class have **one clear responsibility**?
- [ ] Can I **add new types** without modifying existing code?
- [ ] Can **subtypes substitute** for their base type?
- [ ] Does my service expose **only what clients need**?
- [ ] Are dependencies **injected**, not global?

If yes to all: ✅ Your code follows SOLID principles!

---

## 📚 Key Files to Know

```
Backend:
- app_refactored.py          ← Main entry point
- services/pdf_service.py    ← PDF operations  
- services/annotation_service.py ← Annotation management
- models/annotation.py       ← Annotation classes

Frontend:
- app.js                     ← Main controller
- services/api-service.js    ← HTTP communication
- services/state-manager.js  ← UI state
- services/pdf-viewer.js     ← PDF rendering
```

---

## 🎓 Learning Resources

- [Backend Architecture](SOLID_REFACTORING.md)
- [Frontend Architecture](FRONTEND_REFACTORING.md)
- [Complete Summary](REFACTORING_SUMMARY.md)
- Individual service files (well-documented code)

---

## ✅ Ready to Go!

You now have:
✅ Clean, maintainable code
✅ Professional architecture
✅ Easy to test
✅ Easy to extend
✅ No global state
✅ Clear separation of concerns

**Happy coding! 🚀**
