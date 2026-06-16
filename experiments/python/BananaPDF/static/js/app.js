/**
 * PDF Editor Application Controller
 * Orchestrates all services using dependency injection
 * Single Responsibility: Coordinate between services and UI
 */
class PDFEditorApp {
    constructor(config = {}) {
        // Dependency Injection
        this.apiService = config.apiService || new APIService();
        this.stateManager = config.stateManager || new StateManager();
        this.annotationManager = config.annotationManager || new ClientAnnotationManager();
        this.undoRedoManager = config.undoRedoManager || new UndoRedoManager();
        this.pdfViewer = config.pdfViewer || new PDFViewer('pdfContainer', this.apiService);
        this.drawingTool = config.drawingTool || new DrawingTool('drawingOverlay');
        
        this.currentPageNum = 1;
        this.pageCount = 0;
    }

    async initialize() {
        console.log('Initializing PDF Editor App...');
        
        // Set up event listeners
        this.setupFileUpload();
        this.setupPageNavigation();
        this.setupTools();
        this.setupKeyboardShortcuts();
        this.setupSave();
        
        console.log('✓ PDF Editor initialized');
    }

    setupFileUpload() {
        const fileInput = document.getElementById('fileInput');
        const uploadBtn = document.getElementById('uploadBtn');
        
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => fileInput.click());
        }
        
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        }
    }

    setupPageNavigation() {
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');
        const pageInput = document.getElementById('pageInput');
        
        if (prevBtn) prevBtn.addEventListener('click', () => this.goToPreviousPage());
        if (nextBtn) nextBtn.addEventListener('click', () => this.goToNextPage());
        if (pageInput) pageInput.addEventListener('change', (e) => this.goToPage(parseInt(e.target.value)));
    }

    setupTools() {
        const tools = ['selectTool', 'drawTool', 'textTool', 'signatureTool', 'eraserTool'];
        
        tools.forEach(toolId => {
            const btn = document.getElementById(toolId);
            if (btn) {
                btn.addEventListener('click', () => this.selectTool(toolId));
            }
        });
        
        // Undo/Redo buttons
        const undoBtn = document.getElementById('undoBtn');
        const redoBtn = document.getElementById('redoBtn');
        
        if (undoBtn) undoBtn.addEventListener('click', () => this.undo());
        if (redoBtn) redoBtn.addEventListener('click', () => this.redo());
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'z' && !e.shiftKey) {
                    e.preventDefault();
                    this.undo();
                } else if (e.key === 'z' && e.shiftKey || e.key === 'y') {
                    e.preventDefault();
                    this.redo();
                }
            }
        });
    }

    setupSave() {
        const saveBtn = document.getElementById('saveBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.savePDF());
        }
    }

    async handleFileUpload(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        try {
            console.log(`Uploading: ${file.name}`);
            
            const result = await this.apiService.upload(file);
            
            this.pageCount = result.pageCount;
            this.currentPageNum = 1;
            
            // Update state
            this.stateManager.setState({
                pageCount: result.pageCount,
                currentPage: 1,
                originalFilename: result.originalFilename,
                pages: Array.from({ length: result.pageCount }, (_, i) => ({
                    index: i,
                    rotation: 0,
                    deleted: false,
                })),
            });
            
            // Reset managers
            this.annotationManager.clear();
            this.undoRedoManager.clear();
            
            // Render first page
            await this.renderCurrentPage();
            
            console.log(`✓ Uploaded: ${result.pageCount} pages`);
        } catch (error) {
            console.error('Upload failed:', error);
            alert(`Upload failed: ${error.message}`);
        }
    }

    async renderCurrentPage() {
        try {
            // Render PDF page
            const pageInfo = await this.pdfViewer.renderPage(this.currentPageNum, this.pageCount);
            
            // Set up drawing tool
            this.drawingTool.setup(pageInfo.element);
            
            // Render annotations
            const annotations = this.annotationManager.getAnnotationsForPage(this.currentPageNum - 1);
            const textBoxes = this.annotationManager.getTextBoxesForPage(this.currentPageNum - 1);
            
            this.pdfViewer.renderAnnotations(annotations, textBoxes);
            
            // Update UI
            this.updatePageInfo();
        } catch (error) {
            console.error('Failed to render page:', error);
            alert(`Failed to render page: ${error.message}`);
        }
    }

    updatePageInfo() {
        const pageInfo = document.getElementById('pageInfo');
        if (pageInfo) {
            pageInfo.textContent = `Page ${this.currentPageNum} of ${this.pageCount}`;
        }
        
        const pageInput = document.getElementById('pageInput');
        if (pageInput) {
            pageInput.value = this.currentPageNum;
            pageInput.max = this.pageCount;
        }
    }

    async goToPage(pageNum) {
        if (pageNum < 1 || pageNum > this.pageCount) return;
        
        this.currentPageNum = pageNum;
        this.stateManager.setState({ currentPage: pageNum });
        
        // Save drawing if in draw mode
        if (this.stateManager.state.selectedTool === 'drawTool') {
            await this.saveDrawing();
        }
        
        await this.renderCurrentPage();
    }

    goToPreviousPage() {
        if (this.currentPageNum > 1) {
            this.goToPage(this.currentPageNum - 1);
        }
    }

    goToNextPage() {
        if (this.currentPageNum < this.pageCount) {
            this.goToPage(this.currentPageNum + 1);
        }
    }

    selectTool(toolId) {
        const previousTool = this.stateManager.state.selectedTool;
        
        // Clean up previous tool
        if (previousTool === 'drawTool') {
            this.saveDrawing();
            this.drawingTool.disable();
        }
        
        this.stateManager.setState({ selectedTool: toolId });
        
        // Setup new tool
        if (toolId === 'drawTool') {
            this.drawingTool.enable();
        } else if (toolId === 'textTool') {
            this.setupTextTool();
        } else if (toolId === 'signatureTool') {
            this.setupSignatureTool();
        }
    }

    setupTextTool() {
        const annotationLayer = this.pdfViewer.getAnnotationLayer();
        if (!annotationLayer) return;
        
        annotationLayer.addEventListener('click', (e) => {
            const text = prompt('Enter text:');
            if (text) {
                const rect = annotationLayer.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                this.addTextAnnotation(x, y, text);
            }
        });
    }

    setupSignatureTool() {
        console.log('Signature tool selected');
        // Implementation for signature tool
    }

    async saveDrawing() {
        const imageData = this.drawingTool.getImageData();
        if (!imageData) return;
        
        const annotation = {
            id: `draw_${Date.now()}`,
            pageNum: this.currentPageNum - 1,
            type: 'drawing',
            x: 0,
            y: 0,
            width: this.drawingTool.canvas.width,
            height: this.drawingTool.canvas.height,
            imageData: imageData,
        };
        
        this.annotationManager.addAnnotation(annotation);
        this.drawingTool.clear();
        
        // Save undo state
        this.undoRedoManager.saveState('Drawing', this, this.annotationManager);
    }

    addTextAnnotation(x, y, text) {
        const textBox = {
            id: `text_${Date.now()}`,
            pageNum: this.currentPageNum - 1,
            type: 'text',
            x: x,
            y: y,
            width: 150,
            height: 30,
            text: text,
            fontSize: 12,
            fontFamily: 'Arial',
            color: '#000000',
        };
        
        this.annotationManager.addTextBox(textBox);
        
        // Re-render annotations
        const annotations = this.annotationManager.getAnnotationsForPage(this.currentPageNum - 1);
        const textBoxes = this.annotationManager.getTextBoxesForPage(this.currentPageNum - 1);
        this.pdfViewer.renderAnnotations(annotations, textBoxes);
        
        // Save undo state
        this.undoRedoManager.saveState('Add text', this, this.annotationManager);
    }

    async undo() {
        const previousSnapshot = this.undoRedoManager.undo();
        if (!previousSnapshot) return;
        
        // Restore state
        this.annotationManager.setState(previousSnapshot.annotationState);
        
        // Re-render
        const annotations = this.annotationManager.getAnnotationsForPage(this.currentPageNum - 1);
        const textBoxes = this.annotationManager.getTextBoxesForPage(this.currentPageNum - 1);
        this.pdfViewer.renderAnnotations(annotations, textBoxes);
        
        console.log('✓ Undo:', previousSnapshot.description);
    }

    async redo() {
        const snapshot = this.undoRedoManager.redo();
        if (!snapshot) return;
        
        // Restore state
        this.annotationManager.setState(snapshot.annotationState);
        
        // Re-render
        const annotations = this.annotationManager.getAnnotationsForPage(this.currentPageNum - 1);
        const textBoxes = this.annotationManager.getTextBoxesForPage(this.currentPageNum - 1);
        this.pdfViewer.renderAnnotations(annotations, textBoxes);
        
        console.log('✓ Redo:', snapshot.description);
    }

    async savePDF() {
        try {
            if (!this.pageCount) {
                alert('No PDF loaded');
                return;
            }
            
            // Save any pending drawing
            if (this.stateManager.state.selectedTool === 'drawTool') {
                await this.saveDrawing();
            }
            
            const state = this.stateManager.getState();
            const saveData = {
                originalFilename: state.originalFilename,
                pages: state.pages,
                annotations: this.annotationManager.getAllAnnotations(),
                textBoxes: this.annotationManager.textBoxes,
            };
            
            console.log('Saving PDF...', saveData);
            
            const pdfBlob = await this.apiService.savePDF(saveData);
            
            // Download file
            const url = URL.createObjectURL(pdfBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `edited_${state.originalFilename}`;
            link.click();
            URL.revokeObjectURL(url);
            
            console.log('✓ PDF saved and downloaded');
        } catch (error) {
            console.error('Save failed:', error);
            alert(`Save failed: ${error.message}`);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new PDFEditorApp();
    app.initialize();
    
    // Expose globally for debugging
    window.pdfEditorApp = app;
});
