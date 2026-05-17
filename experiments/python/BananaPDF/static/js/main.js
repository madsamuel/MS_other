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
    
    addTextBox(textBox) {
        this.textBoxes[textBox.id] = textBox;
        this.eventBus.emit('textBoxAdded', textBox);
        return textBox;
    }
    
    getAnnotationsForPage(pageNum) {
        return this.annotations[pageNum] || [];
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
        
        const renderContext = {
            canvasContext: this.ctx,
            viewport: viewport
        };
        
        await page.render(renderContext).promise;
        this.renderAnnotations();
        this.eventBus.emit('pageRendered', { pageNum });
    }
    
    async generateThumbnails(pdfDoc) {
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
                thumbnail.appendChild(canvas);
            } catch (error) {
                console.error('Error rendering thumbnail:', error);
            }
            
            this.thumbnailsContainer.appendChild(thumbnail);
        }
    }
    
    renderAnnotations() {
        this.annotationLayer.innerHTML = '';
        const annotations = this.annotationManager.getAnnotationsForPage(this.currentPage - 1);
        const scale = this.zoomLevel / 100;
        
        annotations.forEach(annotation => {
            const div = document.createElement('div');
            div.className = 'annotation ' + annotation.type;
            div.style.left = (annotation.x * scale) + 'px';
            div.style.top = (annotation.y * scale) + 'px';
            div.style.width = (annotation.width * scale) + 'px';
            div.style.height = (annotation.height * scale) + 'px';
            
            if (annotation.type === 'highlight') {
                div.style.backgroundColor = 'rgba(255, 255, 0, 0.3)';
            }
            
            this.annotationLayer.appendChild(div);
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
        this.currentTool = null;
        this.pendingInput = null;
        
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
        
        // Status
        this.statusText = document.getElementById('statusText');
        this.emptyState = document.getElementById('emptyState');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.errorMessage = document.getElementById('errorMessage');
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
        if (this.pdfViewer.canvas) this.pdfViewer.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
        
        // Drag and drop
        document.addEventListener('dragover', (e) => e.preventDefault());
        document.addEventListener('drop', (e) => this.handleDrop(e));
        
        // Modals
        if (this.textConfirm) this.textConfirm.addEventListener('click', () => this.confirmTextInput());
        if (this.textCancel) this.textCancel.addEventListener('click', () => this.closeModal('text'));
        if (this.commentConfirm) this.commentConfirm.addEventListener('click', () => this.confirmCommentInput());
        if (this.commentCancel) this.commentCancel.addEventListener('click', () => this.closeModal('comment'));
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
        
        // Show empty state initially
        this.emptyState.style.display = 'flex';
    }
    
    async handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        this.showLoading(true);
        try {
            this.pdfDoc = await this.pdfLoader.load(file);
        } catch (error) {
            this.showLoading(false);
        }
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
    
    async onPageSelected(data) {
        await this.pdfViewer.renderPage(data.pageNum, this.pdfDoc);
        this.pageSelector.value = data.pageNum;
        this.pdfViewer.updateThumbnailSelection(data.pageNum);
    }
    
    async onPageModified() {
        // First, update page selector which will fix currentPage if it's deleted
        this.updatePageSelector();
        // Then regenerate thumbnails
        await this.pdfViewer.generateThumbnails(this.pdfDoc);
        // Finally render the (now valid) current page
        await this.pdfViewer.renderPage(this.pdfViewer.currentPage, this.pdfDoc);
    }
    
    async onStateRestored(data) {
        await this.onPageModified();
        this.updateUndoRedoButtons();
        this.setStatus(`${data.action}`);
    }
    
    selectTool(toolId) {
        if (this.currentTool) {
            document.getElementById(`${this.currentTool}Btn`).classList.remove('active');
        }
        this.currentTool = toolId;
        document.getElementById(`${toolId}Btn`).classList.add('active');
        this.setStatus(`Selected: ${toolId}`);
    }
    
    handleCanvasClick(event) {
        if (!this.currentTool) return;
        
        const rect = this.pdfViewer.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const scale = this.pdfViewer.zoomLevel / 100;
        const canvasX = x / scale;
        const canvasY = y / scale;
        
        switch (this.currentTool) {
            case 'text':
                this.pendingInput = { x: canvasX, y: canvasY, type: 'text' };
                this.openModal('text');
                break;
            case 'comment':
                this.pendingInput = { x: canvasX, y: canvasY, type: 'comment' };
                this.openModal('comment');
                break;
            case 'highlight':
                this.addHighlight(canvasX, canvasY);
                break;
        }
    }
    
    addHighlight(x, y) {
        this.undoRedoManager.saveState('Add Highlight', this.pageManager, this.annotationManager);
        
        const annotation = {
            id: `ann_${Date.now()}`,
            pageNum: this.pdfViewer.currentPage - 1,
            type: 'highlight',
            x,
            y,
            width: 100,
            height: 30,
            color: '#FFFF00'
        };
        
        this.annotationManager.addAnnotation(annotation);
        this.pdfViewer.renderAnnotations();
        this.enableSaveButton();
    }
    
    confirmTextInput() {
        if (!this.pendingInput || !this.textInput.value) return;
        
        this.undoRedoManager.saveState('Add Text Box', this.pageManager, this.annotationManager);
        
        const textBox = {
            id: `text_${Date.now()}`,
            pageNum: this.pdfViewer.currentPage - 1,
            x: this.pendingInput.x,
            y: this.pendingInput.y,
            text: this.textInput.value,
            fontSize: 12,
            color: '#000000'
        };
        
        this.annotationManager.addTextBox(textBox);
        this.closeModal('text');
        this.textInput.value = '';
        this.pendingInput = null;
        this.pdfViewer.renderAnnotations();
        this.enableSaveButton();
    }
    
    confirmCommentInput() {
        if (!this.pendingInput || !this.commentInput.value) return;
        
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
            text: this.commentInput.value
        };
        
        this.annotationManager.addAnnotation(annotation);
        this.closeModal('comment');
        this.commentInput.value = '';
        this.pendingInput = null;
        this.pdfViewer.renderAnnotations();
        this.enableSaveButton();
    }
    
    rotateCurrentPage() {
        if (confirm('Rotate this page?')) {
            this.undoRedoManager.saveState('Rotate Page', this.pageManager, this.annotationManager);
            this.pageManager.rotatePage(this.pdfViewer.currentPage);
            this.pdfViewer.renderPage(this.pdfViewer.currentPage, this.pdfDoc);
            this.enableSaveButton();
        }
    }
    
    deleteCurrentPage() {
        if (confirm('Delete this page? This action cannot be undone.')) {
            this.undoRedoManager.saveState('Delete Page', this.pageManager, this.annotationManager);
            const pageToDelete = this.pdfViewer.currentPage;
            this.pageManager.deletePage(pageToDelete);
            
            // Find next valid page to display
            for (let i = 1; i <= this.pdfDoc.numPages; i++) {
                if (!this.pageManager.pages[i - 1]?.deleted) {
                    this.pdfViewer.currentPage = i;
                    break;
                }
            }
            
            this.onPageModified();
            this.enableSaveButton();
        }
    }
    
    performUndo() {
        this.undoRedoManager.undo(this.pageManager, this.annotationManager);
        this.enableSaveButton();
    }
    
    performRedo() {
        this.undoRedoManager.redo(this.pageManager, this.annotationManager);
        this.enableSaveButton();
    }
    
    updatePageSelector() {
        this.pageSelector.innerHTML = '';
        for (let i = 1; i <= this.pdfDoc.numPages; i++) {
            // Skip deleted pages
            if (this.pageManager.pages[i - 1]?.deleted) continue;
            
            const option = document.createElement('option');
            option.value = i;
            option.textContent = `Page ${i}`;
            if (i === this.pdfViewer.currentPage) {
                option.selected = true;
            }
            this.pageSelector.appendChild(option);
        }
        
        // If current page was deleted, find first active page
        if (this.pageManager.pages[this.pdfViewer.currentPage - 1]?.deleted) {
            for (let i = 1; i <= this.pdfDoc.numPages; i++) {
                if (!this.pageManager.pages[i - 1]?.deleted) {
                    this.pdfViewer.currentPage = i;
                    break;
                }
            }
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
    
    openModal(type) {
        if (type === 'text') {
            this.textInputModal.style.display = 'flex';
            this.textInput.focus();
        } else if (type === 'comment') {
            this.commentInputModal.style.display = 'flex';
            this.commentInput.focus();
        }
    }
    
    closeModal(type) {
        if (type === 'text') {
            this.textInputModal.style.display = 'none';
        } else if (type === 'comment') {
            this.commentInputModal.style.display = 'none';
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
        this.statusText.textContent = message;
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
    } catch (error) {
        console.error('Failed to initialize BananaPDF:', error);
    }
});
