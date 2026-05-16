"""Annotation Manager - handles annotations"""
from datetime import datetime
import uuid


class AnnotationManager:
    """Manage PDF annotations"""
    
    def __init__(self):
        """Initialize annotation manager"""
        self.annotations = {}
    
    def add_annotation(self, data):
        """
        Add annotation
        
        Args:
            data: {
                'pageNum': int,
                'type': 'highlight'|'comment'|'rectangle'|'circle'|'line'|'freehand',
                'x': float,
                'y': float,
                'width': float,
                'height': float,
                'color': str (hex color),
                'text': str (for comments),
                'points': list (for freehand),
            }
        """
        try:
            annotation = {
                'id': str(uuid.uuid4()),
                'pageNum': data.get('pageNum'),
                'type': data.get('type'),
                'x': data.get('x'),
                'y': data.get('y'),
                'width': data.get('width'),
                'height': data.get('height'),
                'color': data.get('color', '#FFFF00'),
                'opacity': data.get('opacity', 0.3),
                'strokeWidth': data.get('strokeWidth', 2),
                'text': data.get('text', ''),
                'points': data.get('points', []),
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat(),
            }
            
            self.annotations[annotation['id']] = annotation
            return annotation
            
        except Exception as e:
            raise Exception(f"Failed to add annotation: {str(e)}")
    
    def update_annotation(self, annotation_id, data):
        """Update annotation"""
        try:
            if annotation_id not in self.annotations:
                raise ValueError(f"Annotation not found: {annotation_id}")
            
            annotation = self.annotations[annotation_id]
            
            # Update allowed fields
            for key in ['x', 'y', 'width', 'height', 'color', 'text', 'opacity', 'strokeWidth']:
                if key in data:
                    annotation[key] = data[key]
            
            annotation['updatedAt'] = datetime.now().isoformat()
            
            return annotation
            
        except Exception as e:
            raise Exception(f"Failed to update annotation: {str(e)}")
    
    def delete_annotation(self, annotation_id):
        """Delete annotation"""
        try:
            if annotation_id in self.annotations:
                del self.annotations[annotation_id]
                return True
            return False
            
        except Exception as e:
            raise Exception(f"Failed to delete annotation: {str(e)}")
    
    def get_annotations_for_page(self, page_num):
        """Get all annotations for a page"""
        return [
            ann for ann in self.annotations.values()
            if ann.get('pageNum') == page_num
        ]
    
    def get_all_annotations(self):
        """Get all annotations"""
        return list(self.annotations.values())
