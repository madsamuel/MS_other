/**
 * State Manager - Single Responsibility: Manage application state
 * Stores all UI state and provides methods to update it
 */
class StateManager {
    constructor() {
        this.state = {
            currentPage: 1,
            pageCount: 0,
            isModified: false,
            selectedTool: null,
            zoomLevel: 1.0,
            pdfs: {},  // Cached page images
            originalFilename: '',
            pages: [],
            annotations: {},
            textBoxes: {},
        };
        
        this.listeners = [];
    }

    getState() {
        return { ...this.state };
    }

    setState(updates) {
        this.state = { ...this.state, ...updates };
        this.notifyListeners();
    }

    updatePage(updates) {
        this.state.pages = this.state.pages.map(p =>
            p.index === this.state.currentPage - 1 ? { ...p, ...updates } : p
        );
        this.notifyListeners();
    }

    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }

    notifyListeners() {
        this.listeners.forEach(listener => listener(this.state));
    }

    reset() {
        this.state = {
            currentPage: 1,
            pageCount: 0,
            isModified: false,
            selectedTool: null,
            zoomLevel: 1.0,
            pdfs: {},
            originalFilename: '',
            pages: [],
            annotations: {},
            textBoxes: {},
        };
        this.notifyListeners();
    }
}
