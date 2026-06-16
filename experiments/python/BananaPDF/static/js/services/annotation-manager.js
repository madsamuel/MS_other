/**
 * Annotation Manager - Single Responsibility: Client-side annotation storage
 * Stores all annotations and text boxes locally until save
 */
class ClientAnnotationManager {
    constructor() {
        this.annotations = {};  // {pageNum: [annotations]}
        this.textBoxes = {};    // {id: textbox}
    }

    addAnnotation(annotation) {
        const pageKey = String(annotation.pageNum);
        if (!this.annotations[pageKey]) {
            this.annotations[pageKey] = [];
        }
        this.annotations[pageKey].push(annotation);
        return annotation;
    }

    getAnnotationsForPage(pageNum) {
        return this.annotations[String(pageNum)] || [];
    }

    getAllAnnotations() {
        return { ...this.annotations };
    }

    removeAnnotation(annotationId) {
        for (const pageKey in this.annotations) {
            const idx = this.annotations[pageKey].findIndex(a => a.id === annotationId);
            if (idx !== -1) {
                this.annotations[pageKey].splice(idx, 1);
                return true;
            }
        }
        return false;
    }

    addTextBox(textBox) {
        this.textBoxes[textBox.id] = textBox;
        
        // Also add to annotations for consistency
        const pageKey = String(textBox.pageNum);
        if (!this.annotations[pageKey]) {
            this.annotations[pageKey] = [];
        }
        this.annotations[pageKey].push({
            ...textBox,
            type: 'text',
        });
    }

    getTextBoxesForPage(pageNum) {
        const boxes = [];
        for (const id in this.textBoxes) {
            if (this.textBoxes[id].pageNum === pageNum) {
                boxes.push(this.textBoxes[id]);
            }
        }
        return boxes;
    }

    getState() {
        return {
            annotations: this.getAllAnnotations(),
            textBoxes: this.textBoxes,
        };
    }

    setState(state) {
        this.annotations = state.annotations || {};
        this.textBoxes = state.textBoxes || {};
    }

    clear() {
        this.annotations = {};
        this.textBoxes = {};
    }
}
