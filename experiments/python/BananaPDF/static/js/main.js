/**
 * BananaPDF - Main Application Logic
 */

// Set up PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

class PDFEditor {
    constructor() {
        this.pdfDoc = null;
        this.currentPage = 1;
        this.zoomLevel = 100;
        this.activeToolId = null;
        this.annotations = {};
        this.textBoxes = {};
        this.pages = [];
        this.isModified = false;
        this.currentTool = null;
        this.pendingInput = null;
        
        this.initializeElements();
        this.attachEventListeners();
        this.setStatus('Ready');
    }
    
    initializeElements() {
        // Main elements
        this.canvas = document.getElementById('pdfCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.fileInput = document.getElementById('fileInput');
        this.thumbnailsContainer = document.getElementById('thumbnailsContainer');
        this.annotationLayer = document.getElementById('annotationLayer');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.emptyState = document.getElementById('emptyState');
        this.errorMessage = document.getElementById('errorMessage');
        this.statusText = document.getElementById('statusText');
        
        // Buttons
        this.openBtn = document.getElementById('openBtn');
        this.exportBtn = document.getElementById('exportBtn');
        this.printBtn = document.getElementById('printBtn');
        this.zoomInBtn = document.getElementById('zoomInBtn');
        this.zoomOutBtn = document.getElementById('zoomOutBtn');
        this.zoomLevelSelect = document.getElementById('zoomLevel');
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
        
        // Modals
        this.textInputModal = document.getElementById('textInputModal');
        this.textInput = document.getElementById('textInput');
        this.textConfirm = document.getElementById('textConfirm');
        this.textCancel = document.getElementById('textCancel');
        
        this.commentInputModal = document.getElementById('commentInputModal');
        this.commentInput = document.getElementById('commentInput');
        this.commentConfirm = document.getElementById('commentConfirm');
        this.commentCancel = document.getElementById('commentCancel');
    }
    
    attachEventListeners() {
        // File operations
        this.openBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        this.exportBtn.addEventListener('click', () => this.exportPDF());
        this.printBtn.addEventListener('click', () => window.print());
        
        // Zoom controls
        this.zoomInBtn.addEventListener('click', () => this.setZoom(this.zoomLevel + 25));
        this.zoomOutBtn.addEventListener('click', () => this.setZoom(this.zoomLevel - 25));
        this.zoomLevelSelect.addEventListener('change', (e) => this.setZoom(parseInt(e.target.value)));
        
        // Tools
        this.highlightBtn.addEventListener('click', () => this.selectTool('highlight'));
        this.textBtn.addEventListener('click', () => this.selectTool('text'));
        this.commentBtn.addEventListener('click', () => this.selectTool('comment'));
        this.drawBtn.addEventListener('click', () => this.selectTool('draw'));
        this.signBtn.addEventListener('click', () => this.selectTool('signature'));
        
        // Page operations
        this.rotateBtn.addEventListener('click', () => this.rotatePage());
        this.deletePageBtn.addEventListener('click', () => this.deletePage());
        this.pageSelector.addEventListener('change', (e) => this.goToPage(parseInt(e.target.value)));
        
        // Canvas interactions
        this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleCanvasMouseMove(e));
        
        // Drag and drop
        document.addEventListener('dragover', (e) => e.preventDefault());
        document.addEventListener('drop', (e) => this.handleDrop(e));
        
        // Modals
        this.textConfirm.addEventListener('click', () => this.confirmTextInput());
        this.textCancel.addEventListener('click', () => this.closeModal('text'));
        this.commentConfirm.addEventListener('click', () => this.confirmCommentInput());
        this.commentCancel.addEventListener('click', () => this.closeModal('comment'));
    }
    
    async handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        try {
            this.showLoading(true);
            await this.loadPDF(file);
            this.setStatus('PDF loaded successfully');
        } catch (error) {
            this.showError(`Failed to load PDF: ${error.message}`);
            this.setStatus('Error loading PDF');
        } finally {
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
    
    async loadPDF(file) {
        const arrayBuffer = await file.arrayBuffer();
        this.pdfDoc = await pdfjsLib.getDocument(arrayBuffer).promise;
        
        this.fileName.textContent = file.name;
        this.pageInfo.textContent = `${this.pdfDoc.numPages} pages`;
        
        // Initialize pages
        this.pages = Array(this.pdfDoc.numPages).fill(null).map((_, i) => ({
            index: i,
            rotation: 0,
            deleted: false
        }));
        
        this.annotations = {};
        this.textBoxes = {};
        this.isModified = false;
        
        // Update UI
        this.enableControls();
        this.emptyState.style.display = 'none';
        this.updatePageSelector();
        await this.generateThumbnails();
        await this.renderPage(1);
    }
    
    async generateThumbnails() {
        this.thumbnailsContainer.innerHTML = '';
        
        for (let i = 1; i <= this.pdfDoc.numPages; i++) {
            const thumbnail = document.createElement('div');
            thumbnail.className = 'thumbnail';
            thumbnail.setAttribute('data-page', i);
            
            if (i === this.currentPage) {
                thumbnail.classList.add('active');
            }
            
            thumbnail.addEventListener('click', () => this.goToPage(i));
            
            // Render thumbnail
            const page = await this.pdfDoc.getPage(i);
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
            this.thumbnailsContainer.appendChild(thumbnail);
        }
    }
    
    async renderPage(pageNum) {
        if (!this.pdfDoc || pageNum < 1 || pageNum > this.pdfDoc.numPages) {
            return;
        }
        
        this.currentPage = pageNum;
        
        // Update thumbnail selection
        document.querySelectorAll('.thumbnail').forEach(thumb => {
            thumb.classList.remove('active');
        });
        document.querySelector(`[data-page="${pageNum}"]`)?.classList.add('active');
        
        // Update page selector
        this.pageSelector.value = pageNum;
        
        // Get page
        const page = await this.pdfDoc.getPage(pageNum);
        const rotation = this.pages[pageNum - 1]?.rotation || 0;
        const scale = this.zoomLevel / 100;
        
        const viewport = page.getViewport({
            scale: scale,
            rotation: rotation
        });
        
        this.canvas.width = viewport.width;
        this.canvas.height = viewport.height;
        
        const renderContext = {
            canvasContext: this.ctx,
            viewport: viewport
        };
        
        await page.render(renderContext).promise;
        
        // Render annotations
        this.renderAnnotations();
    }
    
    async rotatePage() {
        if (this.currentPage < 1 || this.currentPage > this.pages.length) return;
        
        const page = this.pages[this.currentPage - 1];
        page.rotation = (page.rotation + 90) % 360;
        this.isModified = true;
        
        await this.renderPage(this.currentPage);
        this.setStatus(`Page rotated to ${page.rotation}°`);
    }
    
    deletePage() {
        if (this.pdfDoc.numPages === 1) {
            this.showError('Cannot delete the last page');
            return;
        }
        
        if (!confirm('Delete this page? This action cannot be undone.')) {
            return;
        }
        
        const page = this.pages[this.currentPage - 1];
        page.deleted = true;
        this.isModified = true;
        
        // Hide the thumbnail for deleted page
        const thumbnail = document.querySelector(`[data-page="${this.currentPage}"]`);
        if (thumbnail) {
            thumbnail.style.display = 'none';
        }
        
        this.goToPage(Math.min(this.currentPage + 1, this.pdfDoc.numPages));
        this.setStatus('Page marked for deletion');
    }
    
    goToPage(pageNum) {
        if (pageNum < 1 || pageNum > this.pdfDoc.numPages) return;
        this.renderPage(pageNum);
    }
    
    selectTool(toolId) {
        // Deselect previous tool
        if (this.currentTool) {
            document.getElementById(`${this.currentTool}Btn`).classList.remove('active');
        }
        
        // Select new tool
        this.currentTool = toolId;
        document.getElementById(`${toolId}Btn`).classList.add('active');
        this.setStatus(`Selected: ${toolId}`);
    }
    
    async handleCanvasClick(event) {
        if (!this.currentTool) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        // Convert to canvas coordinates accounting for zoom
        const scale = this.zoomLevel / 100;
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
                await this.addAnnotation({
                    pageNum: this.currentPage - 1,
                    type: 'highlight',
                    x: canvasX,
                    y: canvasY,
                    width: 100,
                    height: 30,
                    color: '#FFFF00'
                });
                break;
        }
    }
    
    handleCanvasMouseMove(event) {
        // This can be extended for drawing or other mouse interactions
    }
    
    async addAnnotation(data) {
        try {
            const response = await fetch('/api/add-annotation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) throw new Error('Failed to add annotation');
            
            const result = await response.json();
            const annotation = result.annotation;
            
            if (!(annotation.pageNum in this.annotations)) {
                this.annotations[annotation.pageNum] = [];
            }
            this.annotations[annotation.pageNum].push(annotation);
            
            this.isModified = true;
            await this.renderPage(this.currentPage);
            this.updateAnnotationsList();
            this.setStatus('Annotation added');
            
        } catch (error) {
            this.showError(`Failed to add annotation: ${error.message}`);
        }
    }
    
    confirmTextInput() {
        if (!this.pendingInput || !this.textInput.value) return;
        
        this.addTextBox(this.pendingInput, this.textInput.value);
        this.closeModal('text');
        this.textInput.value = '';
        this.pendingInput = null;
    }
    
    confirmCommentInput() {
        if (!this.pendingInput || !this.commentInput.value) return;
        
        this.addAnnotation({
            pageNum: this.currentPage - 1,
            type: 'comment',
            x: this.pendingInput.x,
            y: this.pendingInput.y,
            width: 24,
            height: 24,
            color: '#FF0000',
            text: this.commentInput.value
        });
        
        this.closeModal('comment');
        this.commentInput.value = '';
        this.pendingInput = null;
    }
    
    async addTextBox(position, text) {
        try {
            const response = await fetch('/api/add-textbox', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    pageNum: this.currentPage - 1,
                    x: position.x,
                    y: position.y,
                    text: text,
                    fontSize: 12,
                    color: '#000000'
                })
            });
            
            if (!response.ok) throw new Error('Failed to add text box');
            
            const result = await response.json();
            this.textBoxes[result.textbox.id] = result.textbox;
            
            this.isModified = true;
            await this.renderPage(this.currentPage);
            this.setStatus('Text added');
            
        } catch (error) {
            this.showError(`Failed to add text: ${error.message}`);
        }
    }
    
    renderAnnotations() {
        this.annotationLayer.innerHTML = '';
        
        const pageAnnotations = this.annotations[this.currentPage - 1] || [];
        const scale = this.zoomLevel / 100;
        
        pageAnnotations.forEach(annotation => {
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
    
    updatePageSelector() {
        this.pageSelector.innerHTML = '';
        for (let i = 1; i <= this.pdfDoc.numPages; i++) {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = `Page ${i}`;
            this.pageSelector.appendChild(option);
        }
        this.pageSelector.value = this.currentPage;
    }
    
    updateAnnotationsList() {
        const pageAnnotations = this.annotations[this.currentPage - 1] || [];
        this.annotationsList.innerHTML = pageAnnotations
            .map(ann => `<li>${ann.type}: ${ann.text || 'annotation'}</li>`)
            .join('');
    }
    
    setZoom(level) {
        level = Math.max(25, Math.min(300, level));
        this.zoomLevel = level;
        this.zoomLevelSelect.value = level;
        this.renderPage(this.currentPage);
    }
    
    async exportPDF() {
        try {
            this.setStatus('Exporting PDF...');
            this.showLoading(true);
            
            const response = await fetch('/api/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    flatten: false
                })
            });
            
            if (!response.ok) throw new Error('Export failed');
            
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = 'edited_document.pdf';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.isModified = false;
            this.setStatus('PDF exported successfully');
            
        } catch (error) {
            this.showError(`Failed to export: ${error.message}`);
        } finally {
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
        }
    }
    
    closeModal(type) {
        if (type === 'text') {
            this.textInputModal.style.display = 'none';
        } else if (type === 'comment') {
            this.commentInputModal.style.display = 'none';
        }
    }
    
    enableControls() {
        this.exportBtn.disabled = false;
        this.printBtn.disabled = false;
        this.zoomInBtn.disabled = false;
        this.zoomOutBtn.disabled = false;
        this.zoomLevelSelect.disabled = false;
        this.rotateBtn.disabled = false;
        this.deletePageBtn.disabled = false;
        this.pageSelector.disabled = false;
        this.highlightBtn.disabled = false;
        this.textBtn.disabled = false;
        this.commentBtn.disabled = false;
        this.drawBtn.disabled = false;
        this.signBtn.disabled = false;
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

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.pdfEditor = new PDFEditor();
});
