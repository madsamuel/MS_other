/**
 * API Service - Single Responsibility: API communication
 * Handles all HTTP requests to the backend
 */
class APIService {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }

    async upload(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.baseURL}/upload`, {
            method: 'POST',
            body: formData,
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }
        
        return response.json();
    }

    async getPDF(pageNum, t) {
        const response = await fetch(`${this.baseURL}/render-page/${pageNum}?t=${t}`);
        if (!response.ok) throw new Error('Failed to get PDF page');
        return response.blob();
    }

    async getPageDimensions(pageNum) {
        const response = await fetch(`${this.baseURL}/page-dimensions/${pageNum}?t=${Date.now()}`);
        if (!response.ok) throw new Error('Failed to get page dimensions');
        return response.json();
    }

    async addAnnotation(annotationData) {
        const response = await fetch(`${this.baseURL}/add-annotation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(annotationData),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to add annotation');
        }
        
        return response.json();
    }

    async savePDF(saveData) {
        const response = await fetch(`${this.baseURL}/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(saveData),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save PDF');
        }
        
        // Return blob for file download
        return response.blob();
    }

    async resetSession() {
        const response = await fetch(`${this.baseURL}/reset-session`, {
            method: 'POST',
        });
        
        if (!response.ok) throw new Error('Failed to reset session');
        return response.json();
    }
}
