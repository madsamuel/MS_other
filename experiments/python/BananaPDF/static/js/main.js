/**
 * BananaPDF - Refactored with SOLID Principles
 * 
 * Architecture:
 * - EventBus: Central event dispatcher (Dependency Inversion)
 * - PDFLoader: Handles file loading (Single Responsibility)
 * - PDFViewer: Handles rendering (Single Responsibility)
 * - PageManager: Manages page state (Single Responsibility)
 * - AnnotationManager: Manages annotations (Single Responsibility)
 * - UIController: Manages UI interactions (Single Responsibility)
 * - UndoRedoManager: Manages undo/redo (Single Responsibility)
 */

// Set up PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

// ============================================================================
// EVENT BUS - Central event dispatcher (Dependency Inversion Principle)
// ============================================================================

class EventBus {
    constructor() {
        this.listeners = {};
    }
    
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }
    
    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }
    
    off(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }
}

// ============================================================================
// PDF LOADER - Handles PDF file loading and validation
// ============================================================================

class PDFLoader {
    constructor(eventBus) {
        this.eventBus = eventBus;
    }
    
    async load(file) {
        try {
            console.log('Loading PDF:', file.name);
            const arrayBuffer = await file.arrayBuffer();
            console.log('File read, size:', arrayBuffer.byteLength);
            
            const pdfDoc = await pdfjsLib.getDocument(arrayBuffer).promise;
            console.log('PDF loaded, pages:', pdfDoc.numPages);
            
            this.eventBus.emit('pdfLoaded', {
                pdfDoc,
                filename: file.name,
                pageCount: pdfDoc.numPages
            });
            
            return pdfDoc;
        } catch (error) {
            console.error('Failed to load PDF:', error);
            this.eventBus.emit('error', {
                message: `Failed to load PDF: ${error.message}`
            });
            throw error;
        }
    }
}

// ============================================================================
// PAGE MANAGER - Manages page state (rotation, deletion, etc.)
// ============================================================================

class PageManager {
    constructor(eventBus) {
        this.eventBus = eventBus;
        this.pages = [];
    }
    
    initialize(pageCount) {
        this.pages = Array(pageCount).fill(null).map((_, i) => ({
            index: i,
            rotation: 0,
            deleted: false
        }));
        this.eventBus.emit('pagesInitialized', { pages: this.pages });
    }
    
    rotatePage(pageNum) {
        if (this.isValidPage(pageNum)) {
            this.pages[pageNum - 1].rotation = (this.pages[pageNum - 1].rotation + 90) % 360;
            this.eventBus.emit('pageRotated', { pageNum, rotation: this.pages[pageNum - 1].rotation });
        }
    }
    
    deletePage(pageNum) {
        if (this.isValidPage(pageNum) && this.pages.length > 1) {
            this.pages[pageNum - 1].deleted = true;
            this.eventBus.emit('pageDeleted', { pageNum });
        }
    }
    
    reorderPages(newOrder) {
        const original = this.pages.slice();
        for (let i = 0; i < newOrder.length; i++) {
            this.pages[i] = original[newOrder[i]];
        }
        this.eventBus.emit('pagesReordered', { pages: this.pages });
    }
    
    getActivePage(pageNum) {
        return this.isValidPage(pageNum) && !this.pages[pageNum - 1].deleted;
    }
    
    isValidPage(pageNum) {
        return pageNum > 0 && pageNum <= this.pages.length;
    }
    
    getPages() {
        return this.pages.filter(p => !p.deleted);
    }
    
    getState() {
        return JSON.parse(JSON.stringify(this.pages));
    }
    
    setState(pages) {
        this.pages = JSON.parse(JSON.stringify(pages));
    }
    
    reset() {
        this.pages = [];
    }
}

// ============================================================================
// ANNOTATION STORAGE - Client-side annotation management
// ============================================================================

class ClientAnnotationManager {
    constructor(eventBus) {
        this.eventBus = eventBus;
        this.annotations = {};
        this.textBoxes = {};
    }
    
    addAnnotation(annotation) {
        const { pageNum } = annotation;
        if (!this.annotations[pageNum]) {
            this.annotations[pageNum] = [];
        }
        this.annotations[pageNum].push(annotation);
        this.eventBus.emit('annotationAdded', annotation);
        return annotation;
    }
    
    updateAnnotation(annotationId, updates) {
        // Find and update annotation in any page
        for (const pageNum in this.annotations) {
            const annotation = this.annotations[pageNum].find(a => a.id === annotationId);
            if (annotation) {
                Object.assign(annotation, updates);
                this.eventBus.emit('annotationUpdated', annotation);
                return annotation;
            }
        }
        console.warn('Annotation not found:', annotationId);
        return null;
    }
    
    addTextBox(textBox) {
        this.textBoxes[textBox.id] = textBox;
        this.eventBus.emit('textBoxAdded', textBox);
        return textBox;
    }
    
    getAnnotationsForPage(pageNum) {
        return this.annotations[pageNum] || [];
    }
    
    getTextBoxesForPage(pageNum) {
        return Object.values(this.textBoxes).filter(tb => tb.pageNum === pageNum);
    }
    
    getState() {
        return {
            annotations: JSON.parse(JSON.stringify(this.annotations)),
            textBoxes: JSON.parse(JSON.stringify(this.textBoxes))
        };
    }
    
    setState(state) {
        this.annotations = JSON.parse(JSON.stringify(state.annotations || {}));
        this.textBoxes = JSON.parse(JSON.stringify(state.textBoxes || {}));
    }
}

// ============================================================================
// PDF VIEWER - Handles PDF rendering and display
// ============================================================================

class PDFViewer {
    constructor(eventBus, pageManager, annotationManager) {
        this.eventBus = eventBus;
        this.pageManager = pageManager;
        this.annotationManager = annotationManager;
        this.pdfDoc = null;
        this.currentPage = 1;
        this.zoomLevel = 100;
        
        this.canvas = document.getElementById('pdfCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.annotationLayer = document.getElementById('annotationLayer');
        this.thumbnailsContainer = document.getElementById('thumbnailsContainer');
    }
    
    async renderPage(pageNum, pdfDoc) {
        if (!pdfDoc || pageNum < 1 || pageNum > pdfDoc.numPages) return;
        
        this.currentPage = pageNum;
        const page = await pdfDoc.getPage(pageNum);
        const rotation = this.pageManager.pages[pageNum - 1]?.rotation || 0;
        const scale = this.zoomLevel / 100;
        
        const viewport = page.getViewport({ scale, rotation });
        this.canvas.width = viewport.width;
        this.canvas.height = viewport.height;
        
        // Store page dimensions for coordinate conversion (needed for proper annotation positioning)
        const unzoomedViewport = page.getViewport({ scale: 1, rotation });
        this.pageWidth = unzoomedViewport.width;
        this.pageHeight = unzoomedViewport.height;
        
        // Fetch actual PDF page dimensions from backend for accurate coordinate mapping
        try {
            const timestamp = Date.now();
            const dimResponse = await fetch(`/api/page-dimensions/${pageNum}?t=${timestamp}`);
            if (dimResponse.ok) {
                const dimData = await dimResponse.json();
                this.pdfPageWidth = dimData.width;
                this.pdfPageHeight = dimData.height;
                console.log(`✓ Page ${pageNum} PDF native dimensions: ${this.pdfPageWidth} x ${this.pdfPageHeight} (points)`);
                console.log(`  Viewport dimensions: ${this.pageWidth} x ${this.pageHeight} (pixels)`);
                console.log(`  Scale factors: X=${(this.pageWidth / this.pdfPageWidth).toFixed(4)}, Y=${(this.pageHeight / this.pdfPageHeight).toFixed(4)}`);
            } else {
                console.error(`✗ Failed to fetch page dimensions: HTTP ${dimResponse.status}`);
                this.pdfPageWidth = null;
                this.pdfPageHeight = null;
            }
        } catch (error) {
            console.error('✗ Failed to fetch page dimensions - network error:', error);
            this.pdfPageWidth = null;
            this.pdfPageHeight = null;
        }
        
        // Explicitly clear the canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        const renderContext = {
            canvasContext: this.ctx,
            viewport: viewport
        };
        
        await page.render(renderContext).promise;
        this.renderAnnotations();
        this.eventBus.emit('pageRendered', { pageNum });
    }
    
    async generateThumbnails(pdfDoc) {
        // Preserve scroll position
        const scrollTop = this.thumbnailsContainer.scrollTop;
        
        this.thumbnailsContainer.innerHTML = '';
        
        for (let i = 1; i <= pdfDoc.numPages; i++) {
            if (this.pageManager.pages[i - 1]?.deleted) continue;
            
            const thumbnail = document.createElement('div');
            thumbnail.className = 'thumbnail';
            thumbnail.setAttribute('data-page', i);
            
            if (i === this.currentPage) {
                thumbnail.classList.add('active');
            }
            
            thumbnail.addEventListener('click', () => {
                this.eventBus.emit('pageSelected', { pageNum: i });
            });
            
            try {
                const page = await pdfDoc.getPage(i);
                const scale = 0.15;
                const viewport = page.getViewport({ scale });
                
                const canvas = document.createElement('canvas');
                canvas.width = viewport.width;
                canvas.height = viewport.height;
                
                const ctx = canvas.getContext('2d');
                const renderContext = {
                    canvasContext: ctx,
                    viewport: viewport
                };
                
                await page.render(renderContext).promise;
                
                // Convert canvas to image for better CSS sizing
                const img = document.createElement('img');
                img.src = canvas.toDataURL('image/png');
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.objectFit = 'cover';
                thumbnail.appendChild(img);
            } catch (error) {
                console.error('Error rendering thumbnail:', error);
            }
            
            this.thumbnailsContainer.appendChild(thumbnail);
        }
        
        // Restore scroll position without animation
        this.thumbnailsContainer.scrollTop = scrollTop;
        
        // Ensure active thumbnail is visible (without smooth animation)
        const activeThumbnail = document.querySelector('[data-page="' + this.currentPage + '"]');
        if (activeThumbnail) {
            activeThumbnail.scrollIntoView({ block: 'nearest' });
        }
    }
    
    renderAnnotations() {
        this.annotationLayer.innerHTML = '';
        
        // Position the annotation layer to overlay the canvas exactly
        const canvasRect = this.canvas.getBoundingClientRect();
        const containerRect = this.annotationLayer.parentElement.getBoundingClientRect();
        
        this.annotationLayer.style.width = this.canvas.width + 'px';
        this.annotationLayer.style.height = this.canvas.height + 'px';
        this.annotationLayer.style.top = (canvasRect.top - containerRect.top) + 'px';
        this.annotationLayer.style.left = (canvasRect.left - containerRect.left) + 'px';
        
        const annotations = this.annotationManager.getAnnotationsForPage(this.currentPage - 1);
        const textBoxes = this.annotationManager.getTextBoxesForPage(this.currentPage - 1);
        const scale = this.zoomLevel / 100;
        
        // Render annotations (highlights, comments, etc.) - skip drawing/signature, they're rendered as images
        annotations.forEach(annotation => {
            // Skip drawing and signature annotations - they're rendered as images later
            if (annotation.type === 'drawing' || annotation.type === 'signature') {
                return;
            }
            
            const div = document.createElement('div');
            div.className = 'annotation ' + annotation.type;
            
            // Convert PDF coordinates back to viewport/canvas coordinates for display
            let displayX = annotation.x;
            let displayY = annotation.y;
            let displayWidth = annotation.width;
            let displayHeight = annotation.height;
            
            if (this.pdfPageWidth && this.pdfPageHeight && this.pageWidth && this.pageHeight) {
                // Convert from PDF space to viewport space
                const scaleX = this.pageWidth / this.pdfPageWidth;
                const scaleY = this.pageHeight / this.pdfPageHeight;
                displayX = annotation.x * scaleX;
                displayY = annotation.y * scaleY;
                displayWidth = annotation.width * scaleX;
                displayHeight = annotation.height * scaleY;
            }
            
            // Apply zoom to get canvas-space coordinates
            div.style.left = (displayX * scale) + 'px';
            div.style.top = (displayY * scale) + 'px';
            div.style.width = (displayWidth * scale) + 'px';
            div.style.height = (displayHeight * scale) + 'px';
            
            if (annotation.type === 'highlight') {
                div.style.backgroundColor = 'rgba(255, 255, 0, 0.3)';
            } else if (annotation.type === 'comment') {
                // Keep existing comment display style, just add hover/click handlers
                div.style.cursor = 'pointer';
                div.style.pointerEvents = 'auto';
                
                // Hover to show tooltip
                div.addEventListener('mouseenter', (e) => {
                    if (annotation.text) {
                        const tooltip = document.createElement('div');
                        tooltip.className = 'comment-tooltip';
                        tooltip.textContent = annotation.text;
                        tooltip.style.position = 'fixed';
                        tooltip.style.backgroundColor = '#FFE4B5';
                        tooltip.style.border = '1px solid #FF8C00';
                        tooltip.style.borderRadius = '4px';
                        tooltip.style.padding = '8px 12px';
                        tooltip.style.maxWidth = '250px';
                        tooltip.style.wordWrap = 'break-word';
                        tooltip.style.zIndex = '1001';
                        tooltip.style.fontSize = '12px';
                        tooltip.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
                        
                        const rect = div.getBoundingClientRect();
                        tooltip.style.top = (rect.bottom + 5) + 'px';
                        tooltip.style.left = rect.left + 'px';
                        
                        document.body.appendChild(tooltip);
                        div.tooltip = tooltip;
                    }
                });
                
                div.addEventListener('mouseleave', () => {
                    if (div.tooltip) {
                        div.tooltip.remove();
                        div.tooltip = null;
                    }
                });
                
                // Click to edit comment
                div.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.editComment(annotation);
                });
            }
            
            this.annotationLayer.appendChild(div);
        });
        
        // Render text boxes from annotation manager
        // Text boxes are stored for undo/redo and will be embedded in PDF when saved
        // Render as plain text with NO box/border/styling
        textBoxes.forEach(textBox => {
            const div = document.createElement('div');
            div.className = 'annotation text-box';
            
            // Convert PDF coordinates to viewport/canvas coordinates
            let displayX = textBox.x;
            let displayY = textBox.y;
            
            if (this.pdfPageWidth && this.pdfPageHeight && this.pageWidth && this.pageHeight) {
                const scaleX = this.pageWidth / this.pdfPageWidth;
                const scaleY = this.pageHeight / this.pdfPageHeight;
                displayX = textBox.x * scaleX;
                displayY = textBox.y * scaleY;
            }
            
            // Apply zoom - position only, no sizing or styling
            div.style.position = 'absolute';
            div.style.left = (displayX * scale) + 'px';
            div.style.top = (displayY * scale) + 'px';
            div.style.fontSize = textBox.fontSize + 'px';
            div.style.color = textBox.color;
            div.style.fontFamily = textBox.fontFamily;
            div.style.pointerEvents = 'none';
            div.style.whiteSpace = 'nowrap';
            div.style.border = 'none';
            div.style.borderWidth = '0';
            div.style.outline = 'none';
            div.style.padding = '0';
            div.style.margin = '0';
            div.style.background = 'none';
            div.style.backgroundColor = 'transparent';
            div.style.boxShadow = 'none';
            div.textContent = textBox.text;
            
            this.annotationLayer.appendChild(div);
        });
        
        // Render drawing and signature annotations
        annotations.forEach(annotation => {
            if (annotation.type === 'drawing' || annotation.type === 'signature') {
                if (!annotation.imageData) return;
                
                const img = document.createElement('img');
                img.src = annotation.imageData;
                img.style.position = 'absolute';
                
                let displayX = annotation.x;
                let displayY = annotation.y;
                let displayWidth = annotation.width;
                let displayHeight = annotation.height;
                
                if (this.pdfPageWidth && this.pdfPageHeight && this.pageWidth && this.pageHeight) {
                    const scaleX = this.pageWidth / this.pdfPageWidth;
                    const scaleY = this.pageHeight / this.pdfPageHeight;
                    displayX = annotation.x * scaleX;
                    displayY = annotation.y * scaleY;
                    displayWidth = annotation.width * scaleX;
                    displayHeight = annotation.height * scaleY;
                }
                
                img.style.left = (displayX * scale) + 'px';
                img.style.top = (displayY * scale) + 'px';
                img.style.width = (displayWidth * scale) + 'px';
                img.style.height = (displayHeight * scale) + 'px';
                img.style.pointerEvents = 'none';
                
                this.annotationLayer.appendChild(img);
            }
        });
    }
    
    setZoom(level) {
        this.zoomLevel = Math.max(25, Math.min(300, level));
        this.eventBus.emit('zoomChanged', { zoomLevel: this.zoomLevel });
    }
    
    updateThumbnailSelection(pageNum) {
        document.querySelectorAll('.thumbnail').forEach(thumb => {
            thumb.classList.remove('active');
        });
        document.querySelector(`[data-page="${pageNum}"]`)?.classList.add('active');
    }
}

// ============================================================================
// UNDO/REDO MANAGER - Manages undo/redo stack
// ============================================================================

class UndoRedoManager {
    constructor(eventBus) {
        this.eventBus = eventBus;
        this.undoStack = [];
        this.redoStack = [];
    }
    
    saveState(actionType, pageManager, annotationManager) {
        const state = {
            action: actionType,
            pages: pageManager.getState(),
            annotations: annotationManager.getState(),
            timestamp: Date.now()
        };
        this.undoStack.push(state);
        this.redoStack = [];
        this.eventBus.emit('stateChanged', { canUndo: this.canUndo(), canRedo: this.canRedo() });
    }
    
    undo(pageManager, annotationManager) {
        if (!this.canUndo()) return;
        
        const currentState = {
            action: 'current',
            pages: pageManager.getState(),
            annotations: annotationManager.getState()
        };
        this.redoStack.push(currentState);
        
        const previousState = this.undoStack.pop();
        pageManager.setState(previousState.pages);
        annotationManager.setState(previousState.annotations);
        
        this.eventBus.emit('stateRestored', { 
            action: previousState.action,
            canUndo: this.canUndo(),
            canRedo: this.canRedo()
        });
    }
    
    redo(pageManager, annotationManager) {
        if (!this.canRedo()) return;
        
        const currentState = {
            action: 'current',
            pages: pageManager.getState(),
            annotations: annotationManager.getState()
        };
        this.undoStack.push(currentState);
        
        const nextState = this.redoStack.pop();
        pageManager.setState(nextState.pages);
        annotationManager.setState(nextState.annotations);
        
        this.eventBus.emit('stateRestored', { 
            action: nextState.action,
            canUndo: this.canUndo(),
            canRedo: this.canRedo()
        });
    }
    
    canUndo() {
        return this.undoStack.length > 0;
    }
    
    canRedo() {
        return this.redoStack.length > 0;
    }
    
    reset() {
        this.undoStack = [];
        this.redoStack = [];
        this.eventBus.emit('stateChanged', { canUndo: false, canRedo: false });
    }
}

// ============================================================================
// UI CONTROLLER - Manages UI interactions and state
// ============================================================================

class UIController {
    constructor(eventBus, pdfLoader, pdfViewer, pageManager, annotationManager, undoRedoManager) {
        this.eventBus = eventBus;
        this.pdfLoader = pdfLoader;
        this.pdfViewer = pdfViewer;
        this.pageManager = pageManager;
        this.annotationManager = annotationManager;
        this.undoRedoManager = undoRedoManager;
        
        this.pdfDoc = null;
        this.currentFilename = 'document.pdf';  // Default filename for save operations
        this.currentTool = null;
        this.pendingInput = null;
        this.editingCommentId = null;  // Track which comment is being edited
        this.highlightStart = null;
        this.isHighlighting = false;
        
        this.initializeElements();
        this.attachEventListeners();
        this.attachEventBusListeners();
    }
    
    initializeElements() {
        // Buttons
        this.openBtn = document.getElementById('openBtn');
        this.saveBtn = document.getElementById('saveBtn');
        this.printBtn = document.getElementById('printBtn');
        this.zoomInBtn = document.getElementById('zoomInBtn');
        this.zoomOutBtn = document.getElementById('zoomOutBtn');
        this.zoomLevelSelect = document.getElementById('zoomLevel');
        this.undoBtn = document.getElementById('undoBtn');
        this.redoBtn = document.getElementById('redoBtn');
        this.highlightBtn = document.getElementById('highlightBtn');
        this.textBtn = document.getElementById('textBtn');
        this.commentBtn = document.getElementById('commentBtn');
        this.drawBtn = document.getElementById('drawBtn');
        this.signBtn = document.getElementById('signBtn');
        this.rotateBtn = document.getElementById('rotateBtn');
        this.deletePageBtn = document.getElementById('deletePageBtn');
        
        // Right panel
        this.pageSelector = document.getElementById('pageSelector');
        this.pageInfo = document.getElementById('pageInfo');
        this.fileName = document.getElementById('fileName');
        this.annotationsList = document.getElementById('annotationsList');
        
        // File input
        this.fileInput = document.getElementById('fileInput');
        
        // Modals
        this.textInputModal = document.getElementById('textInputModal');
        this.textInput = document.getElementById('textInput');
        this.textConfirm = document.getElementById('textConfirm');
        this.textCancel = document.getElementById('textCancel');
        
        this.commentInputModal = document.getElementById('commentInputModal');
        this.commentInput = document.getElementById('commentInput');
        this.commentConfirm = document.getElementById('commentConfirm');
        this.commentCancel = document.getElementById('commentCancel');
        
        // Signature modal
        this.signatureModal = document.getElementById('signatureModal');
        this.signatureCanvas = document.getElementById('signatureCanvas');
        this.signatureClear = document.getElementById('signatureClear');
        this.signatureConfirm = document.getElementById('signatureConfirm');
        this.signatureCancel = document.getElementById('signatureCancel');
        
        // Drawing overlay (for direct PDF drawing)
        this.drawingOverlay = document.getElementById('drawingOverlay');
        this.drawingOverlayContext = null;
        
        // Drawing tools panel
        this.drawingToolsPanel = document.getElementById('drawingToolsPanel');
        this.brushColor = document.getElementById('brushColor');
        this.brushType = document.getElementById('brushType');
        this.clearDrawingBtn = document.getElementById('clearDrawingBtn');
        
        // Current brush settings
        this.currentBrushColor = '#000000';
        this.currentBrushWidth = 2;
        
        // Drawing state
        this.isDrawing = false;
        this.drawingContext = null;
        this.isSignature = false;
        this.drawingStartX = 0;
        this.drawingStartY = 0;
        
        // Store bound functions for event listeners so we can remove them later
        this.drawingStartHandler = null;
        this.drawingMoveHandler = null;
        this.drawingEndHandler = null;
        this.signatureStartHandler = null;
        this.signatureMoveHandler = null;
        this.signatureEndHandler = null;
        this.overlayMouseDownHandler = null;
        this.overlayMouseMoveHandler = null;
        this.overlayMouseUpHandler = null;
        this.overlayKeyDownHandler = null;
        
        // Status
        this.statusText = document.getElementById('statusText');
        this.emptyState = document.getElementById('emptyState');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.errorMessage = document.getElementById('errorMessage');
        this.isUpdatingUI = false; // Lock to prevent race conditions
    }
    
    attachEventListeners() {
        // File operations
        if (this.openBtn) this.openBtn.addEventListener('click', () => this.fileInput.click());
        if (this.fileInput) this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        if (this.saveBtn) this.saveBtn.addEventListener('click', () => this.eventBus.emit('saveRequested'));
        if (this.printBtn) this.printBtn.addEventListener('click', () => window.print());
        
        // Zoom controls
        if (this.zoomInBtn) this.zoomInBtn.addEventListener('click', () => this.pdfViewer.setZoom(this.pdfViewer.zoomLevel + 25));
        if (this.zoomOutBtn) this.zoomOutBtn.addEventListener('click', () => this.pdfViewer.setZoom(this.pdfViewer.zoomLevel - 25));
        if (this.zoomLevelSelect) this.zoomLevelSelect.addEventListener('change', (e) => this.pdfViewer.setZoom(parseInt(e.target.value)));
        
        // Undo/Redo
        if (this.undoBtn) this.undoBtn.addEventListener('click', () => this.eventBus.emit('undoRequested'));
        if (this.redoBtn) this.redoBtn.addEventListener('click', () => this.eventBus.emit('redoRequested'));
        
        // Keyboard shortcuts for undo/redo
        document.addEventListener('keydown', (e) => {
            // Ctrl+Z or Cmd+Z for undo
            if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
                e.preventDefault();
                this.eventBus.emit('undoRequested');
            }
            // Ctrl+Shift+Z or Cmd+Shift+Z for redo (also support Ctrl+Y)
            if ((e.ctrlKey || e.metaKey) && (e.key === 'z' || e.key === 'y') && e.shiftKey) {
                e.preventDefault();
                this.eventBus.emit('redoRequested');
            }
            // Also support Ctrl+Y for redo (without shift)
            if ((e.ctrlKey || e.metaKey) && e.key === 'y' && !e.shiftKey) {
                e.preventDefault();
                this.eventBus.emit('redoRequested');
            }
        });
        
        // Tools
        if (this.highlightBtn) this.highlightBtn.addEventListener('click', () => this.selectTool('highlight'));
        if (this.textBtn) this.textBtn.addEventListener('click', () => this.selectTool('text'));
        if (this.commentBtn) this.commentBtn.addEventListener('click', () => this.selectTool('comment'));
        if (this.drawBtn) this.drawBtn.addEventListener('click', () => this.selectTool('draw'));
        if (this.signBtn) this.signBtn.addEventListener('click', () => this.selectTool('signature'));
        
        // Page operations
        if (this.rotateBtn) this.rotateBtn.addEventListener('click', () => this.eventBus.emit('rotatePageRequested'));
        if (this.deletePageBtn) this.deletePageBtn.addEventListener('click', () => this.eventBus.emit('deletePageRequested'));
        if (this.pageSelector) this.pageSelector.addEventListener('change', (e) => this.eventBus.emit('pageSelected', { pageNum: parseInt(e.target.value) }));
        
        // Canvas
        if (this.pdfViewer.canvas) {
            this.pdfViewer.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
            this.pdfViewer.canvas.addEventListener('mousedown', (e) => this.startHighlightDrag(e));
            this.pdfViewer.canvas.addEventListener('mouseup', (e) => this.endHighlightDrag(e));
        }
        
        // Drag and drop
        document.addEventListener('dragover', (e) => e.preventDefault());
        document.addEventListener('drop', (e) => this.handleDrop(e));
        
        // Modals
        if (this.textConfirm) this.textConfirm.addEventListener('click', () => this.confirmTextInput());
        if (this.textCancel) this.textCancel.addEventListener('click', () => this.closeModal('text'));
        if (this.commentConfirm) this.commentConfirm.addEventListener('click', () => this.confirmCommentInput());
        if (this.commentCancel) this.commentCancel.addEventListener('click', () => this.closeModal('comment'));
        
        // Signature controls
        if (this.signatureClear) this.signatureClear.addEventListener('click', () => this.clearSignatureCanvas());
        if (this.signatureConfirm) this.signatureConfirm.addEventListener('click', () => this.confirmSignature());
        if (this.signatureCancel) this.signatureCancel.addEventListener('click', () => this.closeModal('signature'));
        
        // Drawing tools controls
        if (this.brushColor) this.brushColor.addEventListener('change', (e) => {
            this.currentBrushColor = e.target.value;
        });
        
        if (this.brushType) this.brushType.addEventListener('change', (e) => {
            const widthMap = {
                'thin': 1,
                'normal': 2,
                'thick': 4,
                'extra': 6
            };
            this.currentBrushWidth = widthMap[e.target.value] || 2;
        });
        
        if (this.clearDrawingBtn) this.clearDrawingBtn.addEventListener('click', () => {
            if (this.drawingOverlay && this.drawingOverlay.style.display === 'block') {
                const ctx = this.drawingOverlay.getContext('2d');
                ctx.clearRect(0, 0, this.drawingOverlay.width, this.drawingOverlay.height);
                this.setStatus('Drawing cleared');
            }
        });
    }
    
    attachEventBusListeners() {
        this.eventBus.on('pdfLoaded', (data) => this.onPDFLoaded(data));
        this.eventBus.on('pageSelected', (data) => this.onPageSelected(data));
        this.eventBus.on('pageRotated', () => this.onPageModified());
        this.eventBus.on('pageDeleted', () => this.onPageModified());
        this.eventBus.on('rotatePageRequested', () => this.rotateCurrentPage());
        this.eventBus.on('deletePageRequested', () => this.deleteCurrentPage());
        this.eventBus.on('undoRequested', () => this.performUndo());
        this.eventBus.on('redoRequested', () => this.performRedo());
        this.eventBus.on('stateRestored', (data) => this.onStateRestored(data));
        this.eventBus.on('zoomChanged', (data) => this.updateZoomUI(data.zoomLevel));
        this.eventBus.on('error', (data) => this.showError(data.message));
        this.eventBus.on('saveRequested', () => this.handleSave());
        
        // Show empty state initially
        this.emptyState.style.display = 'flex';
    }
    
    async handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // Check for unsaved changes
        if (this.hasUnsavedChanges()) {
            const confirmed = confirm(
                `You have unsaved changes to "${this.currentFilename}".\n\n` +
                `Do you want to discard them and open "${file.name}"?`
            );
            if (!confirmed) {
                // Reset file input
                this.fileInput.value = '';
                return;
            }
        }
        
        this.showLoading(true);
        try {
            // Clear previous document state before loading new PDF
            this.clearDocumentState();
            
            // 1. Load PDF client-side for display (using PDF.js)
            this.pdfDoc = await this.pdfLoader.load(file);
            
            // 2. Upload file to backend for storage and processing
            const formData = new FormData();
            formData.append('file', file);
            
            console.log(`Uploading file to backend: ${file.name}`);
            const uploadResponse = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!uploadResponse.ok) {
                const errorData = await uploadResponse.json();
                throw new Error(errorData.error || 'Upload failed');
            }
            
            const uploadData = await uploadResponse.json();
            console.log(`File uploaded successfully. Session:`, uploadData.session);
            
            // Backend upload succeeded - pdfDoc is already loaded client-side
        } catch (error) {
            console.error('Error in handleFileSelect:', error);
            this.showLoading(false);
            this.showError(`Failed to upload file: ${error.message}`);
        }
    }
    
    hasUnsavedChanges() {
        // Check if there are any annotations or unsaved modifications
        const hasAnnotations = Object.keys(this.annotationManager.annotations).length > 0 ||
                               Object.keys(this.annotationManager.textBoxes).length > 0;
        return hasAnnotations;
    }
    
    clearDocumentState() {
        // Clear all annotations, text boxes, and undo/redo history
        console.log('Clearing document state...');
        this.annotationManager.annotations = {};
        this.annotationManager.textBoxes = {};
        this.undoRedoManager.reset();
        this.pageManager.reset();
        this.pdfDoc = null;
        
        // Clear the active tool button styling
        if (this.currentTool) {
            const toolBtn = document.getElementById(`${this.currentTool}Btn`);
            if (toolBtn) toolBtn.classList.remove('active');
        }
        this.currentTool = null;
        this.pendingInput = null;
        
        if (this.saveBtn) this.saveBtn.disabled = true;
        this.updateUndoRedoButtons();
        console.log('✓ Document state cleared');
    }
    
    handleDrop(event) {
        event.preventDefault();
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.fileInput.files = files;
            this.handleFileSelect({ target: this.fileInput });
        }
    }
    
    async onPDFLoaded(data) {
        this.pdfDoc = data.pdfDoc;
        this.currentFilename = data.filename;  // Store filename for save operations
        this.fileName.textContent = data.filename;
        this.pageInfo.textContent = `${data.pageCount} pages`;
        
        this.pageManager.initialize(data.pageCount);
        this.enableControls();
        this.emptyState.style.display = 'none';
        
        this.updatePageSelector();
        await this.pdfViewer.generateThumbnails(this.pdfDoc);
        await this.pdfViewer.renderPage(1, this.pdfDoc);
        
        this.showLoading(false);
        this.setStatus('PDF loaded successfully');
    }
    
    async reloadPDFDocument() {
        // Reload the PDF document from server to show updates (e.g., after adding text)
        try {
            console.log('Reloading PDF document from server...');
            // Add cache-busting parameter to ensure fresh PDF is fetched
            const timestamp = Date.now();
            const url = `/api/get-pdf?t=${timestamp}`;
            this.pdfDoc = await pdfjsLib.getDocument(url).promise;
            console.log('✓ PDF document reloaded');
            return this.pdfDoc;
        } catch (error) {
            console.error('✗ Failed to reload PDF:', error);
            throw error;
        }
    }
    
    async onPageSelected(data) {
        try {
            // Update current page state
            this.pdfViewer.currentPage = data.pageNum;
            
            // Render the page
            await this.pdfViewer.renderPage(data.pageNum, this.pdfDoc);
            
            // Sync UI elements
            this.pageSelector.value = data.pageNum;
            this.pdfViewer.updateThumbnailSelection(data.pageNum);
            
            this.setStatus(`Page ${data.pageNum} loaded`);
        } catch (error) {
            console.error('Error selecting page:', error);
            this.showError('Failed to load page. Please try again.');
        }
    }
    
    async onPageModified() {
        if (this.isUpdatingUI) return; // Prevent race conditions
        this.isUpdatingUI = true;
        
        try {
            // Track the current page before validation
            const pageBeforeValidation = this.pdfViewer.currentPage;
            
            // Validate and fix current page if it was deleted
            this.ensureValidCurrentPage();
            
            const pageChanged = pageBeforeValidation !== this.pdfViewer.currentPage;
            
            // Update thumbnails and selector together for consistency
            await this.pdfViewer.generateThumbnails(this.pdfDoc);
            this.updatePageSelector();
            
            // Only re-render if the page actually changed
            if (pageChanged) {
                await this.pdfViewer.renderPage(this.pdfViewer.currentPage, this.pdfDoc);
            }
        } catch (error) {
            console.error('Error updating page display:', error);
            this.showError('Failed to update page display. Please try again.');
        } finally {
            this.isUpdatingUI = false;
        }
    }
    
    ensureValidCurrentPage() {
        const currentPageDeleted = this.pageManager.pages[this.pdfViewer.currentPage - 1]?.deleted;
        if (!currentPageDeleted) return; // Current page is valid
        
        // Find next valid page: prefer next, then previous
        for (let i = this.pdfViewer.currentPage + 1; i <= this.pdfDoc.numPages; i++) {
            if (!this.pageManager.pages[i - 1]?.deleted) {
                this.pdfViewer.currentPage = i;
                return;
            }
        }
        
        for (let i = this.pdfViewer.currentPage - 1; i >= 1; i--) {
            if (!this.pageManager.pages[i - 1]?.deleted) {
                this.pdfViewer.currentPage = i;
                return;
            }
        }
        
        // No valid pages remain
        this.showError('No valid pages remaining in document.');
    }
    
    async onStateRestored(data) {
        await this.onPageModified();
        this.updateUndoRedoButtons();
        this.setStatus(`${data.action}`);
    }
    
    selectTool(toolId) {
        // Toggle: if already selected, deselect; otherwise select
        if (this.currentTool === toolId) {
            // Deselect
            document.getElementById(`${toolId}Btn`).classList.remove('active');
            this.currentTool = null;
            
            // Handle deselection of draw tool
            if (toolId === 'draw') {
                this.disableDrawingOverlay();
            }
            
            this.setStatus('Tool deselected');
        } else {
            // Select new tool
            if (this.currentTool) {
                document.getElementById(`${this.currentTool}Btn`).classList.remove('active');
                
                // Clean up previous tool
                if (this.currentTool === 'draw') {
                    this.disableDrawingOverlay();
                }
            }
            
            this.currentTool = toolId;
            document.getElementById(`${toolId}Btn`).classList.add('active');
            
            // Handle selection of draw tool
            if (toolId === 'draw') {
                this.enableDrawingOverlay();
                this.setStatus('Drawing mode - Draw on the PDF. Press ESC or click another tool to finish.');
            } else {
                this.setStatus(`Selected: ${toolId}`);
            }
        }
    }
    
    enableDrawingOverlay() {
        if (!this.drawingOverlay) return;
        
        // Show drawing tools panel
        if (this.drawingToolsPanel) {
            this.drawingToolsPanel.style.display = 'flex';
        }
        
        // Match canvas size to PDF canvas
        const pdfCanvas = this.pdfViewer.canvas;
        if (!pdfCanvas) return;
        
        // Set canvas pixel size (not CSS size)
        this.drawingOverlay.width = pdfCanvas.width;
        this.drawingOverlay.height = pdfCanvas.height;
        
        // Set CSS size to match
        this.drawingOverlay.style.width = pdfCanvas.width + 'px';
        this.drawingOverlay.style.height = pdfCanvas.height + 'px';
        
        // Position overlay to match PDF canvas position
        const rect = pdfCanvas.getBoundingClientRect();
        const containerRect = pdfCanvas.parentElement.getBoundingClientRect();
        
        this.drawingOverlay.style.position = 'absolute';
        this.drawingOverlay.style.top = (rect.top - containerRect.top) + 'px';
        this.drawingOverlay.style.left = (rect.left - containerRect.left) + 'px';
        this.drawingOverlay.style.zIndex = '100';
        this.drawingOverlay.style.display = 'block';
        this.drawingOverlay.style.cursor = 'crosshair';
        
        // Get drawing context
        this.drawingOverlayContext = this.drawingOverlay.getContext('2d');
        
        // Clear the overlay completely - canvas will be transparent via CSS
        this.drawingOverlayContext.clearRect(0, 0, this.drawingOverlay.width, this.drawingOverlay.height);
        
        // Reset canvas context to default state
        this.drawingOverlayContext.strokeStyle = '#000000';
        this.drawingOverlayContext.lineWidth = 2;
        this.drawingOverlayContext.lineCap = 'round';
        this.drawingOverlayContext.lineJoin = 'round';
        
        // Create and store event handlers
        this.overlayMouseDownHandler = (e) => this.startOverlayDrawing(e);
        this.overlayMouseMoveHandler = (e) => this.continueOverlayDrawing(e);
        this.overlayMouseUpHandler = (e) => this.stopOverlayDrawing(e);
        this.overlayKeyDownHandler = (e) => this.handleDrawingKeyDown(e);
        
        // Add event listeners
        this.drawingOverlay.addEventListener('mousedown', this.overlayMouseDownHandler);
        this.drawingOverlay.addEventListener('mousemove', this.overlayMouseMoveHandler);
        this.drawingOverlay.addEventListener('mouseup', this.overlayMouseUpHandler);
        this.drawingOverlay.addEventListener('mouseout', this.overlayMouseUpHandler);
        document.addEventListener('keydown', this.overlayKeyDownHandler);
    }
    
    disableDrawingOverlay() {
        if (!this.drawingOverlay) return;
        
        // Only save if overlay is visible and there's actual drawing content
        if (this.drawingOverlay.style.display === 'block') {
            // Check if there's actual drawing content before saving
            const imageData = this.drawingOverlay.getContext('2d').getImageData(0, 0, this.drawingOverlay.width, this.drawingOverlay.height);
            const hasDrawing = imageData.data.some((pixel, index) => {
                return index % 4 === 3 && pixel > 0;
            });
            
            if (hasDrawing) {
                this.saveDrawingFromOverlay();
                return;  // Exit after saving to avoid double cleanup
            }
        }
        
        // Remove event listeners
        if (this.overlayMouseDownHandler) {
            this.drawingOverlay.removeEventListener('mousedown', this.overlayMouseDownHandler);
            this.drawingOverlay.removeEventListener('mousemove', this.overlayMouseMoveHandler);
            this.drawingOverlay.removeEventListener('mouseup', this.overlayMouseUpHandler);
            this.drawingOverlay.removeEventListener('mouseout', this.overlayMouseUpHandler);
            document.removeEventListener('keydown', this.overlayKeyDownHandler);
        }
        
        // Hide overlay and clear completely
        this.drawingOverlay.style.display = 'none';
        
        if (this.drawingOverlayContext) {
            this.drawingOverlayContext.clearRect(0, 0, this.drawingOverlay.width, this.drawingOverlay.height);
        }
        
        // Hide drawing tools panel
        if (this.drawingToolsPanel) {
            this.drawingToolsPanel.style.display = 'none';
        }
        
        this.isDrawing = false;
    }
    
    startOverlayDrawing(e) {
        if (!this.drawingOverlay) return;
        
        this.isDrawing = true;
        const rect = this.drawingOverlay.getBoundingClientRect();
        this.drawingStartX = (e.clientX - rect.left) * (this.drawingOverlay.width / rect.width);
        this.drawingStartY = (e.clientY - rect.top) * (this.drawingOverlay.height / rect.height);
        
        const ctx = this.drawingOverlay.getContext('2d');
        ctx.beginPath();
        ctx.moveTo(this.drawingStartX, this.drawingStartY);
    }
    
    continueOverlayDrawing(e) {
        if (!this.isDrawing || !this.drawingOverlay) return;
        
        const rect = this.drawingOverlay.getBoundingClientRect();
        const x = (e.clientX - rect.left) * (this.drawingOverlay.width / rect.width);
        const y = (e.clientY - rect.top) * (this.drawingOverlay.height / rect.height);
        
        const ctx = this.drawingOverlay.getContext('2d');
        ctx.lineWidth = this.currentBrushWidth;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.strokeStyle = this.currentBrushColor;
        ctx.lineTo(x, y);
        ctx.stroke();
    }
    
    stopOverlayDrawing(e) {
        if (!this.drawingOverlay) return;
        this.isDrawing = false;
        const ctx = this.drawingOverlay.getContext('2d');
        ctx.closePath();
    }
    
    handleDrawingKeyDown(e) {
        // ESC key to finish drawing
        if (e.key === 'Escape' && this.currentTool === 'draw') {
            this.saveDrawingFromOverlay();
            this.selectTool('draw'); // Deselect the tool
        }
    }
    
    saveDrawingFromOverlay() {
        if (!this.drawingOverlay || !this.drawingOverlay.toDataURL) return;
        
        // Check if anything was drawn
        const imageData = this.drawingOverlay.getContext('2d').getImageData(0, 0, this.drawingOverlay.width, this.drawingOverlay.height);
        const hasDrawing = imageData.data.some((pixel, index) => {
            // Check if any non-white pixels exist (alpha > 0)
            return index % 4 === 3 && pixel > 0; // Check alpha channel
        });
        
        if (!hasDrawing) {
            this.setStatus('No drawing to save');
            return;
        }
        
        // Get the drawing as base64
        const imageData64 = this.drawingOverlay.toDataURL('image/png');
        
        // Save undo/redo state BEFORE making changes
        this.undoRedoManager.saveState('Add Drawing', this.pageManager, this.annotationManager);
        
        // The drawing overlay is full size of the canvas view
        // Map it to PDF space based on current zoom and page dimensions
        const overlayWidth = this.drawingOverlay.width;
        const overlayHeight = this.drawingOverlay.height;
        
        // Calculate scale from overlay coordinates to PDF coordinates
        const canvasScale = this.pdfViewer.pageWidth / overlayWidth;  // How much of PDF is shown in overlay
        const pdfScale = this.pdfViewer.pdfPageWidth / this.pdfViewer.pageWidth;  // Canvas to PDF coords
        
        // Drawing covers the entire visible page area
        // Map overlay space directly to visible PDF space
        const pdfX = 0;  // Drawing starts at page origin
        const pdfY = 0;
        const pdfWidth = this.pdfViewer.pdfPageWidth;
        const pdfHeight = this.pdfViewer.pdfPageHeight;
        
        // Add drawing to client-side annotation manager ONLY (not to PDF backend yet)
        // Drawing will be embedded in PDF only when user clicks Save
        const drawingAnnotation = {
            id: `draw_${Date.now()}`,
            pageNum: this.pdfViewer.currentPage - 1,
            type: 'drawing',
            x: pdfX,
            y: pdfY,
            width: pdfWidth,
            height: pdfHeight,
            imageData: imageData64
        };
        
        this.annotationManager.addAnnotation(drawingAnnotation);
        
        this.setStatus('✓ Drawing added (click Save to embed in PDF)');
        
        // Render drawing immediately on canvas
        this.pdfViewer.renderAnnotations();
        
        // Clear overlay completely
        if (this.drawingOverlayContext) {
            this.drawingOverlayContext.clearRect(0, 0, this.drawingOverlay.width, this.drawingOverlay.height);
        }
        
        // Hide drawing overlay completely
        this.drawingOverlay.style.display = 'none';
        
        // Note: Tool will be deselected naturally when user selects another tool
        // Do NOT call selectTool() here as it creates a recursive loop
        
        this.enableSaveButton();
        this.updateUndoRedoButtons();
    }

    drawingOverlayHasContent() {
        if (!this.drawingOverlay) return false;

        const ctx = this.drawingOverlay.getContext('2d');
        if (!ctx) return false;

        const imageData = ctx.getImageData(0, 0, this.drawingOverlay.width, this.drawingOverlay.height);
        return imageData.data.some((pixel, index) => index % 4 === 3 && pixel > 0);
    }
    
    handleCanvasClick(event) {
        console.log('Canvas clicked, current tool:', this.currentTool);
        if (!this.currentTool || this.currentTool === 'highlight') return; // Highlight uses drag
        
        const rect = this.pdfViewer.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const scale = this.pdfViewer.zoomLevel / 100;
        const viewportX = x / scale;
        const viewportY = y / scale;
        
        // Convert canvas coordinates to PDF native coordinates
        let pdfX, pdfY;
        console.log('=== COORDINATE DEBUG ===' );
        console.log('Click position on canvas (pixels):', x, y);
        console.log('Zoom level:', this.pdfViewer.zoomLevel, '(scale factor:', scale + ')');
        console.log('Viewport coords (at 100% zoom):', viewportX.toFixed(2), viewportY.toFixed(2));
        console.log('PDF page dimensions: ', this.pdfViewer.pdfPageWidth, 'x', this.pdfViewer.pdfPageHeight, '(points)');
        console.log('Viewport dimensions:', this.pdfViewer.pageWidth, 'x', this.pdfViewer.pageHeight, '(pixels)');
        
        if (this.pdfViewer.pdfPageWidth && this.pdfViewer.pdfPageHeight && 
            this.pdfViewer.pageWidth && this.pdfViewer.pageHeight) {
            // Direct scaling: viewport pixels to PDF points
            // pageWidth is already at 100% zoom with PDF.js 96 DPI built-in
            const scaleX = this.pdfViewer.pdfPageWidth / this.pdfViewer.pageWidth;
            const scaleY = this.pdfViewer.pdfPageHeight / this.pdfViewer.pageHeight;
            pdfX = viewportX * scaleX;
            // PDF.js pageHeight already has coordinates with origin at top-left
            // No Y-axis inversion needed - just scale directly
            pdfY = viewportY * scaleY;
            console.log('Scale factors (viewport to PDF):', 'X=' + scaleX.toFixed(4), 'Y=' + scaleY.toFixed(4));
            console.log('Flipped Y coordinate: viewportY=' + viewportY.toFixed(2) + ' -> pdfY=' + pdfY.toFixed(2));
            console.log('Final PDF coordinates:', pdfX.toFixed(2), pdfY.toFixed(2));
        } else {
            // Fallback to viewport coordinates
            pdfX = viewportX;
            pdfY = viewportY;
            console.warn('⚠️  PDF dimensions not available!');
            console.warn('  pdfPageWidth:', this.pdfViewer.pdfPageWidth);
            console.warn('  pdfPageHeight:', this.pdfViewer.pdfPageHeight);
            console.warn('  pageWidth:', this.pdfViewer.pageWidth);
            console.warn('  pageHeight:', this.pdfViewer.pageHeight);
            console.warn('Falling back to viewport coordinates:', pdfX.toFixed(2), pdfY.toFixed(2));
        }
        console.log('======================');
        
        switch (this.currentTool) {
            case 'text':
                this.pendingInput = { x: pdfX, y: pdfY, type: 'text' };
                this.openModal('text');
                break;
            case 'comment':
                this.pendingInput = { x: pdfX, y: pdfY, type: 'comment' };
                this.openModal('comment');
                break;
            case 'draw':
                // Draw tool is now handled by overlay, not modal
                break;
            case 'signature':
                this.pendingInput = { x: pdfX, y: pdfY, type: 'signature' };
                this.openModal('signature');
                break;
        }
    }
    
    startHighlightDrag(event) {
        if (this.currentTool !== 'highlight') return;
        
        const canvasRect = this.pdfViewer.canvas.getBoundingClientRect();
        const scale = this.pdfViewer.zoomLevel / 100;
        
        // Calculate position relative to the canvas
        const canvasX = event.clientX - canvasRect.left;
        const canvasY = event.clientY - canvasRect.top;
        
        // Convert canvas coordinates to PDF native coordinates
        const viewportX = canvasX / scale;
        const viewportY = canvasY / scale;
        
        // If we have actual PDF page dimensions, map viewport coords to PDF coords
        if (this.pdfViewer.pdfPageWidth && this.pdfViewer.pdfPageHeight && 
            this.pdfViewer.pageWidth && this.pdfViewer.pageHeight) {
            const scaleX = this.pdfViewer.pdfPageWidth / this.pdfViewer.pageWidth;
            const scaleY = this.pdfViewer.pdfPageHeight / this.pdfViewer.pageHeight;
            const pdfX = viewportX * scaleX;
            // PDF.js pageHeight already has coordinates with origin at top-left
            // No Y-axis inversion needed - just scale directly
            const pdfY = viewportY * scaleY;
            this.highlightStart = { x: pdfX, y: pdfY };
            console.log('Started highlight drag at PDF coords', this.highlightStart, 
                       `(viewport: ${viewportX}, ${viewportY})`);
        } else {
            // Fallback to viewport coordinates if PDF dimensions not available
            this.highlightStart = { x: viewportX, y: viewportY };
            console.log('Started highlight drag at viewport coords (fallback)', this.highlightStart);
        }
        
        this.isHighlighting = true;
    }
    
    endHighlightDrag(event) {
        if (!this.isHighlighting || !this.highlightStart) return;
        
        const canvasRect = this.pdfViewer.canvas.getBoundingClientRect();
        const scale = this.pdfViewer.zoomLevel / 100;
        
        const canvasX = event.clientX - canvasRect.left;
        const canvasY = event.clientY - canvasRect.top;
        
        // Convert canvas coordinates to PDF native coordinates (same as startHighlightDrag)
        const viewportX = canvasX / scale;
        const viewportY = canvasY / scale;
        
        let pdfEndX, pdfEndY;
        
        if (this.pdfViewer.pdfPageWidth && this.pdfViewer.pdfPageHeight && 
            this.pdfViewer.pageWidth && this.pdfViewer.pageHeight) {
            const scaleX = this.pdfViewer.pdfPageWidth / this.pdfViewer.pageWidth;
            const scaleY = this.pdfViewer.pdfPageHeight / this.pdfViewer.pageHeight;
            pdfEndX = viewportX * scaleX;
            // PDF.js pageHeight already has coordinates with origin at top-left
            // No Y-axis inversion needed - just scale directly
            pdfEndY = viewportY * scaleY;
        } else {
            // Fallback to viewport coordinates
            pdfEndX = viewportX;
            pdfEndY = viewportY;
        }
        
        // Ensure start is top-left and end is bottom-right
        // Both coordinates use the same system (top-left origin), so min/max works correctly
        const highlightX = Math.min(this.highlightStart.x, pdfEndX);
        const highlightY = Math.min(this.highlightStart.y, pdfEndY);
        const width = Math.abs(pdfEndX - this.highlightStart.x);
        const height = Math.abs(pdfEndY - this.highlightStart.y);
        
        // Only create highlight if user dragged a meaningful distance (in PDF coordinates)
        if (width > 5 && height > 5) {
            this.addHighlight(highlightX, highlightY, width, height);
            console.log('Highlight created: x=', highlightX, 'y=', highlightY, 
                       'width=', width, 'height=', height);
        }
        
        this.isHighlighting = false;
        this.highlightStart = null;
        console.log('Ended highlight drag');
    }
    
    addHighlight(x, y, width, height) {
        console.log('Adding highlight at', x, y, 'size', width, 'x', height);
        this.undoRedoManager.saveState('Add Highlight', this.pageManager, this.annotationManager);
        
        const annotation = {
            id: `ann_${Date.now()}`,
            pageNum: this.pdfViewer.currentPage - 1,
            type: 'highlight',
            x,
            y,
            width: width || 100,
            height: height || 30,
            color: '#FFFF00'
        };
        
        console.log('Annotation created:', annotation);
        this.annotationManager.addAnnotation(annotation);
        console.log('Annotations on page:', this.annotationManager.getAnnotationsForPage(this.pdfViewer.currentPage - 1));
        this.pdfViewer.renderAnnotations();
        this.enableSaveButton();
        this.updateUndoRedoButtons();
    }
    
    confirmTextInput() {
        // Validate input
        if (!this.pendingInput) {
            console.warn('⚠️ No pending input location');
            return;
        }
        
        const textContent = this.textInput.value.trim();
        if (!textContent) {
            alert('Please enter some text before adding.');
            return;
        }
        
        const textBoxData = {
            pageNum: this.pdfViewer.currentPage - 1,
            x: this.pendingInput.x,
            y: this.pendingInput.y,
            width: 150,
            height: 30,
            text: textContent,
            fontSize: 12,
            color: '#000000',
            fontFamily: 'Arial'
        };
        
        // Save undo/redo state before making changes
        // This must be done AFTER creating textBoxData but BEFORE sending to backend
        this.undoRedoManager.saveState('Add Text', this.pageManager, this.annotationManager);
        
        console.log('✓ Adding text box to PDF:');
        console.log('  Page:', textBoxData.pageNum);
        console.log('  Position (PDF coords):', textBoxData.x, ',', textBoxData.y);
        console.log('  Width:', textBoxData.width, ', Height:', textBoxData.height);
        console.log('  Text:', textBoxData.text);
        
        // Detailed validation logging
        if (isNaN(textBoxData.x) || isNaN(textBoxData.y)) {
            console.error('⚠️ INVALID COORDINATES - x or y is NaN!');
            console.error('  pendingInput:', this.pendingInput);
            console.error('  x is NaN?', isNaN(textBoxData.x), ', y is NaN?', isNaN(textBoxData.y));
            this.setStatus('⚠️ Invalid click coordinates');
            return;
        }
        
        // Add text box to client-side annotation manager (NOT to PDF backend yet)
        // Text will be embedded in PDF only when user clicks Save
        // This allows undo/redo to work properly
        const textBoxAnnotation = {
            id: `txt_${Date.now()}`,
            pageNum: textBoxData.pageNum,
            type: 'text',
            x: textBoxData.x,
            y: textBoxData.y,
            width: textBoxData.width,
            height: textBoxData.height,
            text: textBoxData.text,
            fontSize: textBoxData.fontSize,
            color: textBoxData.color,
            fontFamily: textBoxData.fontFamily
        };
        
        this.annotationManager.addTextBox(textBoxAnnotation);
        
        this.setStatus('✓ Text "' + textBoxData.text + '" added (click Save to embed in PDF)');
        
        // Clear form and close modal
        this.textInput.value = '';
        this.pendingInput = null;
        this.closeModal('text');
        
        // Render text box immediately on canvas with blue border for visual feedback
        this.pdfViewer.renderAnnotations();
        
        // Enable save button and update undo/redo
        this.enableSaveButton();
        this.updateUndoRedoButtons();
    }
    
    confirmCommentInput() {
        // Validate input
        if (!this.pendingInput && !this.editingCommentId) {
            console.warn('⚠️ No pending input location');
            return;
        }
        
        const commentContent = this.commentInput.value.trim();
        if (!commentContent) {
            alert('Please enter a comment before adding.');
            return;
        }
        
        // Save undo/redo state BEFORE making changes
        if (this.editingCommentId) {
            // Update existing comment
            this.undoRedoManager.saveState('Edit Comment', this.pageManager, this.annotationManager);
            this.annotationManager.updateAnnotation(this.editingCommentId, { text: commentContent });
            this.editingCommentId = null;
        } else {
            // Add new comment
            this.undoRedoManager.saveState('Add Comment', this.pageManager, this.annotationManager);
            
            const annotation = {
                id: `cmt_${Date.now()}`,
                pageNum: this.pdfViewer.currentPage - 1,
                type: 'comment',
                x: this.pendingInput.x,
                y: this.pendingInput.y,
                width: 24,
                height: 24,
                color: '#FF0000',
                text: commentContent
            };
            
            this.annotationManager.addAnnotation(annotation);
        }
        
        this.commentInput.value = '';
        this.pendingInput = null;
        this.closeModal('comment');
        this.pdfViewer.renderAnnotations();
        this.enableSaveButton();
        this.updateUndoRedoButtons();
    }
    
    editComment(annotation) {
        // Open comment modal with existing comment text for editing
        this.editingCommentId = annotation.id;
        this.commentInput.value = annotation.text;
        this.openModal('comment');
        this.commentInput.focus();
        this.commentInput.select();  // Select all text for easy editing
    }
    
    initializeSignatureCanvas() {
        if (!this.signatureCanvas) return;
        
        // Remove old listeners first if they exist
        if (this.signatureStartHandler) {
            this.signatureCanvas.removeEventListener('mousedown', this.signatureStartHandler);
            this.signatureCanvas.removeEventListener('mousemove', this.signatureMoveHandler);
            this.signatureCanvas.removeEventListener('mouseup', this.signatureEndHandler);
            this.signatureCanvas.removeEventListener('mouseout', this.signatureEndHandler);
        }
        
        // Set canvas size
        this.signatureCanvas.width = this.signatureCanvas.offsetWidth;
        this.signatureCanvas.height = this.signatureCanvas.offsetHeight;
        
        const ctx = this.signatureCanvas.getContext('2d');
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, this.signatureCanvas.width, this.signatureCanvas.height);
        
        this.drawingContext = ctx;
        this.isSignature = true;
        
        // Create and store bound functions for signature
        this.signatureStartHandler = (e) => this.startDrawing(e, true);
        this.signatureMoveHandler = (e) => this.continueDrawing(e, true);
        this.signatureEndHandler = () => this.stopDrawing(true);
        
        // Add event listeners for drawing
        this.signatureCanvas.addEventListener('mousedown', this.signatureStartHandler);
        this.signatureCanvas.addEventListener('mousemove', this.signatureMoveHandler);
        this.signatureCanvas.addEventListener('mouseup', this.signatureEndHandler);
        this.signatureCanvas.addEventListener('mouseout', this.signatureEndHandler);
    }
    
    startDrawing(e, isSignature) {
        this.isDrawing = true;
        const canvas = isSignature ? this.signatureCanvas : this.drawingCanvas;
        const rect = canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) * (canvas.width / rect.width);
        const y = (e.clientY - rect.top) * (canvas.height / rect.height);
        
        const ctx = canvas.getContext('2d');
        ctx.beginPath();
        ctx.moveTo(x, y);
    }
    
    continueDrawing(e, isSignature) {
        if (!this.isDrawing) return;
        
        const canvas = isSignature ? this.signatureCanvas : this.drawingCanvas;
        const rect = canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) * (canvas.width / rect.width);
        const y = (e.clientY - rect.top) * (canvas.height / rect.height);
        
        const ctx = canvas.getContext('2d');
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.strokeStyle = '#000000';
        ctx.lineTo(x, y);
        ctx.stroke();
    }
    
    stopDrawing(isSignature) {
        this.isDrawing = false;
        const canvas = isSignature ? this.signatureCanvas : this.drawingCanvas;
        const ctx = canvas.getContext('2d');
        ctx.closePath();
    }
    
    clearSignatureCanvas() {
        if (!this.signatureCanvas) return;
        const ctx = this.signatureCanvas.getContext('2d');
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, this.signatureCanvas.width, this.signatureCanvas.height);
    }
    
    confirmSignature() {
        if (!this.pendingInput) {
            alert('Please select a location on the PDF first.');
            return;
        }
        
        // Get signature data as image
        const imageData = this.signatureCanvas.toDataURL('image/png');
        
        // Save undo/redo state BEFORE making changes
        this.undoRedoManager.saveState('Add Signature', this.pageManager, this.annotationManager);
        
        // Add signature to client-side annotation manager ONLY (not to PDF backend yet)
        // Signature will be embedded in PDF only when user clicks Save
        const signatureAnnotation = {
            id: `sig_${Date.now()}`,
            pageNum: this.pdfViewer.currentPage - 1,
            type: 'signature',
            x: this.pendingInput.x,
            y: this.pendingInput.y,
            width: 150,
            height: 100,
            imageData: imageData
        };
        
        this.annotationManager.addAnnotation(signatureAnnotation);
        
        this.setStatus('✓ Signature added (click Save to embed in PDF)');
        
        // Render signature immediately
        this.pdfViewer.renderAnnotations();
        
        this.pendingInput = null;
        this.closeModal('signature');
        
        this.enableSaveButton();
        this.updateUndoRedoButtons();
    }
    
    async rotateCurrentPage() {
        if (confirm('Rotate this page?')) {
            try {
                this.undoRedoManager.saveState('Rotate Page', this.pageManager, this.annotationManager);
                this.pageManager.rotatePage(this.pdfViewer.currentPage);
                await this.pdfViewer.renderPage(this.pdfViewer.currentPage, this.pdfDoc);
                this.enableSaveButton();
                this.updateUndoRedoButtons();
                this.setStatus('Page rotated');
            } catch (error) {
                console.error('Error rotating page:', error);
                this.showError('Failed to rotate page. Please try again.');
            }
        }
    }
    
    deleteCurrentPage() {
        if (confirm('Delete this page?')) {
            try {
                this.undoRedoManager.saveState('Delete Page', this.pageManager, this.annotationManager);
                const pageToDelete = this.pdfViewer.currentPage;
                this.pageManager.deletePage(pageToDelete);
                
                // Note: ensureValidCurrentPage() will be called by onPageModified()
                this.onPageModified();
                this.enableSaveButton();
                this.updateUndoRedoButtons();
                this.setStatus(`Page ${pageToDelete} deleted`);
            } catch (error) {
                console.error('Error deleting page:', error);
                this.showError('Failed to delete page. Please try again.');
            }
        }
    }
    
    setStatus(message) {
        this.statusText.textContent = message;
        this.statusText.style.display = 'block';
        setTimeout(() => {
            this.statusText.style.display = 'none';
        }, 3000);
    }
    
    showError(message) {
        this.errorMessage.textContent = message;
        this.errorMessage.style.display = 'block';
        setTimeout(() => {
            this.errorMessage.style.display = 'none';
        }, 5000);
    }

    performUndo() {
        this.undoRedoManager.undo(this.pageManager, this.annotationManager);
        // Re-render current page with full update for page-level changes (rotation, deletion, etc.)
        this.onPageModified();
        this.pdfViewer.renderAnnotations();  // Re-render all annotations
        this.updateUndoRedoButtons();        // Update button states
        this.enableSaveButton();
    }
    
    performRedo() {
        this.undoRedoManager.redo(this.pageManager, this.annotationManager);
        // Re-render current page with full update for page-level changes (rotation, deletion, etc.)
        this.onPageModified();
        this.pdfViewer.renderAnnotations();  // Re-render all annotations
        this.updateUndoRedoButtons();        // Update button states
        this.enableSaveButton();
    }
    
    updatePageSelector() {
        try {
            this.pageSelector.innerHTML = '';
            
            for (let i = 1; i <= this.pdfDoc.numPages; i++) {
                // Skip deleted pages
                if (this.pageManager.pages[i - 1]?.deleted) continue;
                
                const option = document.createElement('option');
                option.value = i;
                option.textContent = `Page ${i}`;
                
                // Mark current page as selected
                if (i === this.pdfViewer.currentPage) {
                    option.selected = true;
                }
                
                this.pageSelector.appendChild(option);
            }
            
            // Update aria-label for accessibility
            const totalPages = Array.from(this.pageSelector.options).length;
            this.pageSelector.setAttribute('aria-label', `Page selector: ${totalPages} pages available`);
        } catch (error) {
            console.error('Error updating page selector:', error);
        }
    }
    
    updateZoomUI(zoomLevel) {
        this.zoomLevelSelect.value = zoomLevel;
        this.pdfViewer.renderPage(this.pdfViewer.currentPage, this.pdfDoc);
    }
    
    updateUndoRedoButtons() {
        if (this.undoBtn) this.undoBtn.disabled = !this.undoRedoManager.canUndo();
        if (this.redoBtn) this.redoBtn.disabled = !this.undoRedoManager.canRedo();
    }
    
    enableControls() {
        const controls = [
            this.printBtn, this.zoomInBtn, this.zoomOutBtn, 
            this.zoomLevelSelect, this.highlightBtn, this.textBtn, this.commentBtn,
            this.drawBtn, this.signBtn, this.rotateBtn, this.deletePageBtn, this.pageSelector
        ];
        controls.forEach(control => { if (control) control.disabled = false; });
        this.updateUndoRedoButtons();
    }
    
    enableSaveButton() {
        if (this.saveBtn) this.saveBtn.disabled = false;
    }
    
    async handleSave() {
        if (!this.pdfDoc) {
            this.showError('No PDF loaded. Please open a PDF file first.');
            console.error('Save attempted with no PDF loaded');
            return;
        }
        
        if (this.isUpdatingUI) {
            this.showError('A save operation is already in progress. Please wait.');
            return;
        }
        
        try {
            this.showLoading(true);
            this.setStatus('Saving PDF...');

            // If the user clicks Save while still in draw mode, persist the current
            // overlay into annotationManager so it is included in the save payload.
            if (this.currentTool === 'draw' && this.drawingOverlayHasContent()) {
                this.saveDrawingFromOverlay();
            }
            
            // Build page state array including deletion info
            const pages = [];
            for (let i = 0; i < this.pdfDoc.numPages; i++) {
                pages.push({
                    pageNum: i + 1,
                    deleted: this.pageManager.pages[i]?.deleted || false,
                    rotation: this.pageManager.pages[i]?.rotation || 0
                });
            }
            
            // Verify we have at least one non-deleted page
            const activePages = pages.filter(p => !p.deleted);
            if (activePages.length === 0) {
                this.showError('Cannot save: all pages have been deleted.');
                this.showLoading(false);
                return;
            }
            
            // Prepare save data - IMPORTANT: include filename so backend can find the PDF
            const saveData = {
                flatten: false,  // Use false for proper PDF annotations (like Adobe)
                originalFilename: this.currentFilename,  // Send filename to backend for recovery
                pages: pages,
                annotations: this.annotationManager.annotations || {},
                textBoxes: this.annotationManager.textBoxes || {}
            };
            
            console.log(`Saving PDF "${this.currentFilename}" with ${activePages.length} active pages...`);
            console.log('TextBoxes being sent:', this.annotationManager.textBoxes);
            console.log('Full save data:', saveData);
            
            // Debug: Show all text box details
            Object.entries(this.annotationManager.textBoxes).forEach(([id, tb]) => {
                console.log(`  TextBox "${id}":`, {
                    page: tb.pageNum,
                    x: tb.x,
                    y: tb.y,
                    width: tb.width,
                    height: tb.height,
                    text: tb.text,
                    fontSize: tb.fontSize
                });
            });
            
            // Send to backend
            const response = await fetch('/api/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(saveData)
            });
            
            if (!response.ok) {
                let errorMsg = 'Unknown error';
                try {
                    const error = await response.json();
                    errorMsg = error.error || error.message || errorMsg;
                } catch (e) {
                    errorMsg = `HTTP ${response.status}: ${response.statusText}`;
                }
                throw new Error(errorMsg);
            }
            
            // Download the file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `edited_${this.currentFilename || 'document.pdf'}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.setStatus(`✅ PDF saved successfully! (${activePages.length} pages)`);
            this.showLoading(false);
            console.log('Save completed successfully');
        } catch (error) {
            console.error('Error saving PDF:', error);
            this.showError(`Failed to save PDF: ${error.message}`);
            this.showLoading(false);
        }
    }
    
    openModal(type) {
        if (type === 'text') {
            this.textInputModal.style.display = 'flex';
            this.textInput.focus();
        } else if (type === 'comment') {
            this.commentInputModal.style.display = 'flex';
            this.commentInput.focus();
        } else if (type === 'signature') {
            this.signatureModal.style.display = 'flex';
            setTimeout(() => this.initializeSignatureCanvas(), 100);
        }
    }
    
    closeModal(type) {
        if (type === 'text') {
            this.textInputModal.style.display = 'none';
        } else if (type === 'comment') {
            this.commentInputModal.style.display = 'none';
            this.editingCommentId = null;  // Clear edit mode
        } else if (type === 'signature') {
            this.signatureModal.style.display = 'none';
            this.isDrawing = false;
            // Remove event listeners properly using stored handlers
            if (this.signatureCanvas && this.signatureStartHandler) {
                this.signatureCanvas.removeEventListener('mousedown', this.signatureStartHandler);
                this.signatureCanvas.removeEventListener('mousemove', this.signatureMoveHandler);
                this.signatureCanvas.removeEventListener('mouseup', this.signatureEndHandler);
                this.signatureCanvas.removeEventListener('mouseout', this.signatureEndHandler);
            }
        }
    }
    
    showLoading(show) {
        this.loadingIndicator.style.display = show ? 'flex' : 'none';
    }
    
    showError(message) {
        this.errorMessage.style.display = 'block';
        document.getElementById('errorText').textContent = message;
        setTimeout(() => {
            this.errorMessage.style.display = 'none';
        }, 5000);
    }
    
    setStatus(message) {
        if (this.statusText) {
            this.statusText.textContent = message;
            this.statusText.style.display = 'block';
        }
    }
}

// ============================================================================
// APPLICATION INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing BananaPDF with SOLID principles...');
    
    try {
        // Create event bus (dependency injection point)
        const eventBus = new EventBus();
        
        // Create service instances
        const pdfLoader = new PDFLoader(eventBus);
        const pageManager = new PageManager(eventBus);
        const annotationManager = new ClientAnnotationManager(eventBus);
        const pdfViewer = new PDFViewer(eventBus, pageManager, annotationManager);
        const undoRedoManager = new UndoRedoManager(eventBus);
        
        // Create UI controller (orchestrator)
        const uiController = new UIController(
            eventBus,
            pdfLoader,
            pdfViewer,
            pageManager,
            annotationManager,
            undoRedoManager
        );
        
        // Make available globally for debugging
        window.bananaPDF = {
            eventBus,
            pdfLoader,
            pageManager,
            annotationManager,
            pdfViewer,
            undoRedoManager,
            uiController
        };
        
        console.log('BananaPDF initialized successfully with SOLID architecture');
        
        // Auto-load PDF if one is available in the backend session
        setTimeout(async () => {
            try {
                const response = await fetch('/api/get-pdf-data');
                if (response.ok) {
                    const data = await response.json();
                    console.log('PDF available in session:', data.fileName);
                    
                    // Load the PDF from the server
                    const pdfResponse = await fetch('/api/get-pdf');
                    if (pdfResponse.ok) {
                        const blob = await pdfResponse.blob();
                        const file = new File([blob], data.fileName || 'document.pdf', { type: 'application/pdf' });
                        
                        // Trigger the file select handler
                        const fileInput = document.getElementById('fileInput');
                        if (fileInput) {
                            const dataTransfer = new DataTransfer();
                            dataTransfer.items.add(file);
                            fileInput.files = dataTransfer.files;
                            uiController.handleFileSelect({ target: fileInput });
                            console.log('Auto-loaded PDF from server session');
                        }
                    }
                }
            } catch (error) {
                console.log('No PDF in server session or auto-load disabled (this is normal)', error.message);
            }
        }, 100);
        
    } catch (error) {
        console.error('Failed to initialize BananaPDF:', error);
    }
});
