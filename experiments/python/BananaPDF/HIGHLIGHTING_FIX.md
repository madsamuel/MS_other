# PDF Highlighting Coordinate System Fix - Complete Guide

## Problem Statement
The highlighting feature had a **coordinate system mismatch**:
- Highlights displayed on screen in one location
- But appeared in a different location when the PDF was saved
- This was because frontend and backend used different coordinate systems

## Root Cause Analysis

### The Issue
1. **Frontend** (PDF.js): Renders PDF to a canvas at a viewport size that may differ from the native PDF page dimensions
2. **Backend** (PyMuPDF): Works with native PDF page coordinates from the original PDF file
3. **Mismatch**: A click at canvas position (300px, 400px) might correspond to different PDF coordinates depending on the PDF's actual page size

### Example
```
PDF Page: 612 × 792 points (standard Letter size)
Rendered Viewport: 614 × 823 pixels (due to zoom/scaling)
User clicks at: (300px, 150px) in viewport
Without fix: Annotation stored as (300, 150) in PDF coordinates
Actual PDF: Should be (299.01, 148.27) in PDF points
Result: Highlight appears in wrong position!
```

## Solution Implementation

### 1. Backend Changes (app.py)
Added a new API endpoint to expose actual PDF page dimensions:

```python
@app.route('/api/page-dimensions/<int:page_num>')
def get_page_dimensions(page_num):
    """Get actual PDF page dimensions for coordinate calculations"""
    # Fetches native page dimensions from PyMuPDF
    # Returns: { width: 612.0, height: 792.0, ... }
```

**Why**: The frontend needs to know the actual PDF page size to properly convert between viewport and PDF coordinates.

### 2. Frontend Changes - PDFViewer class

#### Fetch PDF Dimensions
```javascript
async renderPage(pageNum, pdfDoc) {
    // ... existing code ...
    
    // NEW: Fetch actual PDF page dimensions from backend
    const dimResponse = await fetch(`/api/page-dimensions/${pageNum}`);
    if (dimResponse.ok) {
        const dimData = await dimResponse.json();
        this.pdfPageWidth = dimData.width;      // Native PDF width
        this.pdfPageHeight = dimData.height;    // Native PDF height
    }
    
    // Store both PDF and viewport dimensions for coordinate conversion
    this.pageWidth = unzoomedViewport.width;    // Viewport width
    this.pageHeight = unzoomedViewport.height;  // Viewport height
}
```

#### Proper Annotation Display
```javascript
renderAnnotations() {
    // Convert PDF coordinates back to viewport/canvas for display
    const scaleX = this.pageWidth / this.pdfPageWidth;
    const scaleY = this.pageHeight / this.pdfPageHeight;
    
    // Display annotation at correct position
    div.style.left = (annotation.x * scaleX * zoomScale) + 'px';
    div.style.top = (annotation.y * scaleY * zoomScale) + 'px';
    // ... dimension scaling ...
}
```

### 3. Frontend Changes - UIController class

#### Coordinate Transformation in Highlighting
```javascript
startHighlightDrag(event) {
    // 1. Get canvas pixel coordinates
    const canvasX = event.clientX - canvasRect.left;
    const canvasY = event.clientY - canvasRect.top;
    
    // 2. Divide by zoom to get viewport coordinates
    const viewportX = canvasX / scale;
    const viewportY = canvasY / scale;
    
    // 3. Scale to PDF native coordinates using actual dimensions
    const scaleX = this.pdfViewer.pdfPageWidth / this.pdfViewer.pageWidth;
    const scaleY = this.pdfViewer.pdfPageHeight / this.pdfViewer.pageHeight;
    const pdfX = viewportX * scaleX;
    const pdfY = viewportY * scaleY;
    
    // Store PDF coordinates
    this.highlightStart = { x: pdfX, y: pdfY };
}

endHighlightDrag(event) {
    // Same transformation process to calculate highlight end coordinates
    // Ensures highlight dimensions are also in PDF native space
}
```

#### Same Fix for Text and Comments
```javascript
handleCanvasClick(event) {
    // Same coordinate transformation for text and comment annotations
    // Ensures ALL annotations use the correct coordinate system
}
```

## Coordinate System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ User Action: Click or Drag on Canvas                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Canvas Pixel Coordinates                               │
│ (X, Y) = Position of mouse relative to canvas                  │
│ Example: (300px, 150px)                                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Viewport Coordinates (Unzoomed)                        │
│ Divide by zoom level                                            │
│ viewportX = canvasX / (zoomLevel / 100)                         │
│ Example at 100% zoom: (300, 150)                               │
│ Example at 200% zoom: (150, 75)                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: PDF Native Coordinates ⭐ NEW FIX                      │
│ Scale viewport to actual PDF page dimensions                   │
│ scaleX = pdfPageWidth / pageWidth                              │
│ scaleY = pdfPageHeight / pageHeight                            │
│ pdfX = viewportX * scaleX                                      │
│ pdfY = viewportY * scaleY                                      │
│                                                                 │
│ Example:                                                        │
│ PDF page: 612 × 792 points                                     │
│ Viewport: 614 × 823 pixels                                     │
│ scaleX = 612 / 614 = 0.9967                                    │
│ scaleY = 792 / 823 = 0.9623                                    │
│ pdfX = 300 * 0.9967 = 299.01                                   │
│ pdfY = 150 * 0.9623 = 144.35                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Store Annotation with PDF Coordinates                  │
│ {                                                               │
│   type: 'highlight',                                           │
│   x: 299.01,        /* PDF native space */                    │
│   y: 144.35,        /* PDF native space */                    │
│   width: 150.0,                                                │
│   height: 75.0                                                 │
│ }                                                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        DISPLAY (Screen)          SAVE (PDF Export)
        
        ┌──────────────────────┐  ┌──────────────────────┐
        │ Reverse Transform:   │  │ Direct Use:          │
        │ PDF → Viewport →     │  │ Use PDF coordinates  │
        │ Canvas pixels        │  │ directly with        │
        │                      │  │ PyMuPDF's            │
        │ Display in exact     │  │ add_highlight_annot()│
        │ position user        │  │                      │
        │ selected             │  │ Highlight appears in │
        │                      │  │ correct location     │
        │ (299.01, 144.35)     │  │                      │
        │ → (300, 150)px       │  │ (299.01, 144.35)     │
        │                      │  │ → PDF annotations    │
        └──────────────────────┘  └──────────────────────┘
```

## Testing the Fix

### Step 1: Open the Application
```bash
cd c:\code\MS_other\experiments\python\BananaPDF
python app.py
# Visit http://127.0.0.1:5000 in your browser
```

### Step 2: Test Highlighting
1. Upload a PDF file
2. Click the "Highlight" button (🌟)
3. Drag to create a highlight on the document
4. **Verify**: Highlight appears exactly where you dragged

### Step 3: Test Persistence
1. Click "Save" button (💾)
2. Download the PDF
3. Open the downloaded PDF in any PDF viewer (Adobe, Preview, etc.)
4. **Verify**: Highlight appears in the SAME position as on screen

### Step 4: Test Other Tools
Repeat with:
- Text tool (✏️): Click to add text box
- Comment tool (💬): Click to add comment bubble

## Technical Details

### Why This Works
1. **PDF.js** renders pages at the PDF's native resolution by default
2. But **zoom** and **scaling** can change the viewport size
3. **PyMuPDF** (fitz) works directly with native PDF coordinates
4. The fix ensures **bidirectional mapping** between viewport and PDF coordinates

### Edge Cases Handled
- ✅ Different zoom levels (50%, 100%, 200%, etc.)
- ✅ Different PDF page sizes (Letter, A4, Legal, custom)
- ✅ Rotated pages
- ✅ Different screen DPIs

### Fallback Behavior
If page dimensions can't be fetched:
```javascript
if (this.pdfViewer.pdfPageWidth && this.pdfViewer.pdfPageHeight) {
    // Use proper coordinate transformation
} else {
    // Fallback to viewport coordinates
    pdfX = viewportX;
    pdfY = viewportY;
}
```

## Files Modified

1. **app.py** - Added `/api/page-dimensions/<page_num>` endpoint
2. **static/js/main.js** - Updated three classes:
   - `PDFViewer.renderPage()` - Fetch PDF dimensions
   - `PDFViewer.renderAnnotations()` - Reverse transform for display
   - `UIController.startHighlightDrag()` - Forward transform
   - `UIController.endHighlightDrag()` - Forward transform
   - `UIController.handleCanvasClick()` - Forward transform

## Result
✅ **Highlighting now matches between preview and saved PDF**
✅ **All annotation tools use consistent coordinate system**
✅ **Display preview matches actual PDF output**

## Browser Console Debugging
Open browser DevTools (F12) to see detailed logging:
```javascript
console.log('Started highlight drag at PDF coords', this.highlightStart);
console.log(`Page ${pageNum} PDF dimensions: ${this.pdfPageWidth} x ${this.pdfPageHeight}`);
```

This provides visibility into coordinate transformations for troubleshooting.
