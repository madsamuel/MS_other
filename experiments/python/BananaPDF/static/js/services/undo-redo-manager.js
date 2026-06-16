/**
 * Undo/Redo Manager - Single Responsibility: Manage undo/redo history
 * Stores snapshots of state and provides undo/redo functionality
 */
class UndoRedoManager {
    constructor(maxHistorySize = 50) {
        this.undoStack = [];
        this.redoStack = [];
        this.maxHistorySize = maxHistorySize;
    }

    saveState(description, pageManager, annotationManager) {
        // Clear redo stack when new action is taken
        this.redoStack = [];
        
        // Save state snapshot
        const snapshot = {
            description,
            pageState: pageManager.getState(),
            annotationState: annotationManager.getState(),
            timestamp: Date.now(),
        };
        
        this.undoStack.push(snapshot);
        
        // Limit history size
        if (this.undoStack.length > this.maxHistorySize) {
            this.undoStack.shift();
        }
    }

    undo() {
        if (!this.canUndo()) return null;
        
        const current = this.undoStack.pop();
        this.redoStack.push(current);
        
        // Return previous state
        return this.undoStack.length > 0 ? this.undoStack[this.undoStack.length - 1] : null;
    }

    redo() {
        if (!this.canRedo()) return null;
        
        const snapshot = this.redoStack.pop();
        this.undoStack.push(snapshot);
        
        return snapshot;
    }

    canUndo() {
        return this.undoStack.length > 1;
    }

    canRedo() {
        return this.redoStack.length > 0;
    }

    clear() {
        this.undoStack = [];
        this.redoStack = [];
    }

    getHistory() {
        return {
            undo: this.undoStack.map(s => s.description),
            redo: this.redoStack.map(s => s.description),
        };
    }
}
