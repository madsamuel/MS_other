/**
 * Drawing Tool - Single Responsibility: Handle drawing operations
 * Manages canvas drawing state and exports drawing as image
 */
class DrawingTool {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.isDrawing = false;
        this.startX = 0;
        this.startY = 0;
    }

    setup(pageContainer) {
        if (!this.canvas || !pageContainer) return;
        
        // Set canvas size to match page
        const pageImg = pageContainer.querySelector('img');
        if (pageImg) {
            this.canvas.width = pageImg.offsetWidth;
            this.canvas.height = pageImg.offsetHeight;
        }
    }

    enable() {
        if (!this.canvas) return;
        this.canvas.style.display = 'block';
        this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
        this.canvas.addEventListener('mouseleave', this.handleMouseLeave.bind(this));
    }

    disable() {
        if (!this.canvas) return;
        this.canvas.style.display = 'none';
        this.canvas.removeEventListener('mousedown', this.handleMouseDown.bind(this));
        this.canvas.removeEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.removeEventListener('mouseup', this.handleMouseUp.bind(this));
        this.canvas.removeEventListener('mouseleave', this.handleMouseLeave.bind(this));
    }

    handleMouseDown(e) {
        this.isDrawing = true;
        const rect = this.canvas.getBoundingClientRect();
        this.startX = e.clientX - rect.left;
        this.startY = e.clientY - rect.top;
    }

    handleMouseMove(e) {
        if (!this.isDrawing) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Draw line
        this.ctx.strokeStyle = '#000000';
        this.ctx.lineWidth = 2;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        
        this.ctx.beginPath();
        this.ctx.moveTo(this.startX, this.startY);
        this.ctx.lineTo(x, y);
        this.ctx.stroke();
        
        this.startX = x;
        this.startY = y;
    }

    handleMouseUp() {
        this.isDrawing = false;
    }

    handleMouseLeave() {
        this.isDrawing = false;
    }

    hasContent() {
        if (!this.canvas) return false;
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        return imageData.data.some(pixel => pixel !== 0);
    }

    getImageData() {
        if (!this.hasContent()) return null;
        return this.canvas.toDataURL('image/png');
    }

    clear() {
        if (this.ctx) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
    }
}
