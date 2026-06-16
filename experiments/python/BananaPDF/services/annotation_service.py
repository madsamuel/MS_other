"""Annotation service (Single Responsibility + Dependency Inversion)"""
from typing import Dict, List, Any
from models.annotation import Annotation, annotation_factory
import logging


logger = logging.getLogger(__name__)


class AnnotationService:
    """Service for managing annotations (Single Responsibility)"""
    
    def __init__(self):
        """Initialize annotation service"""
        # Store annotations by page number
        self._annotations: Dict[str, List[Annotation]] = {}
    
    def add_annotation(self, annotation_data: Dict[str, Any]) -> Annotation:
        """
        Add annotation to service
        
        Args:
            annotation_data: Dictionary with annotation data
            
        Returns:
            The added annotation
            
        Raises:
            ValueError: If annotation data is invalid
        """
        # Create annotation using factory (Dependency Inversion)
        annotation = annotation_factory(annotation_data)
        
        # Validate annotation
        if not annotation.validate():
            raise ValueError(f"Invalid {annotation.__class__.__name__}: {annotation}")
        
        # Store annotation by page number
        page_key = str(annotation.page_num)
        if page_key not in self._annotations:
            self._annotations[page_key] = []
        
        self._annotations[page_key].append(annotation)
        logger.info(f"Added {annotation.__class__.__name__} to page {annotation.page_num}")
        
        return annotation
    
    def get_annotations_for_page(self, page_num: int) -> List[Annotation]:
        """Get all annotations for a page"""
        page_key = str(page_num)
        return self._annotations.get(page_key, [])
    
    def get_all_annotations(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all annotations as dictionary"""
        result = {}
        for page_key, annotations in self._annotations.items():
            result[page_key] = [ann.to_dict() for ann in annotations]
        return result
    
    def clear_page_annotations(self, page_num: int) -> None:
        """Clear all annotations for a page"""
        page_key = str(page_num)
        if page_key in self._annotations:
            self._annotations[page_key] = []
    
    def remove_annotation(self, annotation_id: str) -> bool:
        """Remove annotation by ID"""
        for page_key, annotations in self._annotations.items():
            for i, ann in enumerate(annotations):
                if ann.id == annotation_id:
                    annotations.pop(i)
                    logger.info(f"Removed annotation {annotation_id}")
                    return True
        return False
    
    def get_state(self) -> Dict[str, Any]:
        """Get current service state (for undo/redo)"""
        return {
            'annotations': {
                page: [ann.to_dict() for ann in annlist]
                for page, annlist in self._annotations.items()
            }
        }
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """Set service state from saved state (for undo/redo)"""
        self._annotations = {}
        if 'annotations' in state:
            for page_key, ann_dicts in state['annotations'].items():
                self._annotations[page_key] = []
                for ann_dict in ann_dicts:
                    annotation = annotation_factory(ann_dict)
                    self._annotations[page_key].append(annotation)
