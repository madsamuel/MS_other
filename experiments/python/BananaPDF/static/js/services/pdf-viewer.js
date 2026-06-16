/**
 * PDF Viewer - Single Responsibility: Render PDFs and annotations
 * Handles canvas rendering, image display, and annotation rendering
 */
class PDFViewer {
    constructor(containerId, apiService) {
        this.container = document.getElementById(containerId);
        this.apiService = apiService;
        this.currentPageNum = 1;
        this.zoomLevel = 1.0;
    }

    async renderPage(pageNum, pageCount) {
        try {
            this.currentPageNum = pageNum;
            
            // Clear container
            this.container.innerHTML = '';
            
            // Create page container
            const pageContainer = document.createElement('div');
            pageContainer.className = 'page-container';
            pageContainer.style.position = 'relative';
            
            // Render PDF image
            const pdfBlob = await this.apiService.getPDF(pageNum - 1, Date.now());
            const pdfUrl = URL.createObjectURL(pdfBlob);
            
            const pdfImg = document.createElement('img');
            pdfImg.src = pdfUrl;
            pdfImg.className = 'pdf-page';
            pdfImg.style.width = '100%';
            pdfImg.style.display = 'block';
            
            pageContainer.appendChild(pdfImg);
            
            // Create annotation layer
            const annotationLayer = document.createElement('div');
            annotationLayer.id = 'annotationLayer';
            annotationLayer.className = 'annotation-layer';
            annotationLayer.style.position = 'absolute';
            annotationLayer.style.top = '0';
            annotationLayer.style.left = '0';
            annotationLayer.style.width = '100%';
            annotationLayer.style.height = '100%';
            
            pageContainer.appendChild(annotationLayer);
            
            // Create drawing overlay
            const drawingOverlay = document.createElement('canvas');
            drawingOverlay.id = 'drawingOverlay';
            drawingOverlay.className = 'drawing-overlay';
            drawingOverlay.style.position = 'absolute';
            drawingOverlay.style.top = '0';
            drawingOverlay.style.left = '0';
            drawingOverlay.style.display = 'none';
            drawingOverlay.style.cursor = 'crosshair';
            drawingOverlay.style.zIndex = '100';
            drawingOverlay.style.backgroundColor = 'transparent';
            
            pageContainer.appendChild(drawingOverlay);
            
            this.container.appendChild(pageContainer);
            
            // Wait for image to load to get dimensions
            await new Promise(resolve => {
                pdfImg.onload = resolve;
                pdfImg.onerror = resolve;
            });
            
            return {
                width: pdfImg.offsetWidth,
                height: pdfImg.offsetHeight,
                element: pageContainer,
            };
            
        } catch (error) {
            console.error('Failed to render page:', error);
            throw error;
        }
    }

    renderAnnotations(annotations, textBoxes) {
        const annotationLayer = document.getElementById('annotationLayer');
        if (!annotationLayer) return;
        
        annotationLayer.innerHTML = '';
        
        // Render all annotations
        annotations.forEach(ann => {
            const el = this.createAnnotationElement(ann);
            if (el) annotationLayer.appendChild(el);
        });
        
        // Render all text boxes
        textBoxes.forEach(tb => {
            const el = this.createTextBoxElement(tb);
            if (el) annotationLayer.appendChild(el);
        });
    }

    createAnnotationElement(annotation) {
        if (!annotation || !annotation.type) return null;
        
        const el = document.createElement('div');
        el.id = annotation.id;
        el.className = `annotation ${annotation.type}`;
        el.style.position = 'absolute';
        el.style.left = `${annotation.x}px`;
        el.style.top = `${annotation.y}px`;
        el.style.width = `${annotation.width}px`;
        el.style.height = `${annotation.height}px`;
        
        switch (annotation.type) {
            case 'drawing':
            case 'signature':
                // Render as image
                if (annotation.imageData) {
                    el.style.backgroundImage = `url('${annotation.imageData}')`;
                    el.style.backgroundSize = 'contain';
                    el.style.backgroundRepeat = 'no-repeat';
                    el.style.backgroundColor = 'transparent';
                    el.style.border = 'none';
                }
                break;
            
            case 'text':
                el.textContent = annotation.text;
                el.style.fontSize = `${annotation.fontSize || 12}px`;
                el.style.color = annotation.color || '#000000';
                el.style.padding = '0';
                el.style.margin = '0';
                el.style.backgroundColor = 'transparent';
                el.style.border = 'none';
                break;
            
            case 'highlight':
                el.style.backgroundColor = annotation.color || 'rgba(255, 255, 0, 0.3)';
                el.style.border = 'none';
                break;
            
            case 'comment':
                el.textContent = annotation.text || 'Comment';
                el.style.backgroundColor = annotation.color || 'rgba(255, 0, 0, 0.1)';
                el.style.color = '#000000';
                el.style.padding = '5px';
                el.style.fontSize = '12px';
                break;
        }
        
        return el;
    }

    createTextBoxElement(textBox) {
        const el = document.createElement('div');
        el.id = textBox.id;
        el.className = 'textbox annotation';
        el.textContent = textBox.text;
        
        el.style.position = 'absolute';
        el.style.left = `${textBox.x}px`;
        el.style.top = `${textBox.y}px`;
        el.style.width = `${textBox.width}px`;
        el.style.height = `${textBox.height}px`;
        el.style.fontSize = `${textBox.fontSize || 12}px`;
        el.style.color = textBox.color || '#000000';
        el.style.padding = '0';
        el.style.margin = '0';
        el.style.backgroundColor = 'transparent';
        el.style.border = 'none';
        el.style.outline = 'none';
        el.style.boxShadow = 'none';
        el.style.fontFamily = textBox.fontFamily || 'Arial';
        
        return el;
    }

    getDrawingCanvas() {
        return document.getElementById('drawingOverlay');
    }

    getAnnotationLayer() {
        return document.getElementById('annotationLayer');
    }
}
