"""Annotation models following SOLID principles"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Annotation(ABC):
    """Base annotation class (Interface Segregation + Liskov Substitution)"""
    id: str
    page_num: int
    x: float
    y: float
    width: float
    height: float
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert annotation to dictionary"""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate annotation data"""
        pass


@dataclass
class TextAnnotation(Annotation):
    """Text annotation"""
    text: str = ""
    font_size: int = 12
    font_family: str = "Arial"
    color: str = "#000000"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'pageNum': self.page_num,
            'type': 'text',
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'text': self.text,
            'fontSize': self.font_size,
            'fontFamily': self.font_family,
            'color': self.color,
        }
    
    def validate(self) -> bool:
        """Validate text annotation"""
        if not self.text or not self.text.strip():
            return False
        if self.font_size < 1 or self.font_size > 72:
            return False
        if len(self.text) > 1000:
            return False
        return True


@dataclass
class DrawingAnnotation(Annotation):
    """Drawing annotation (image-based)"""
    image_data: str = ""  # base64 PNG
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'pageNum': self.page_num,
            'type': 'drawing',
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'imageData': self.image_data,
        }
    
    def validate(self) -> bool:
        """Validate drawing annotation"""
        if not self.image_data:
            return False
        if not self.image_data.startswith(('data:image', 'iVBOR')):
            return False
        if self.width <= 0 or self.height <= 0:
            return False
        return True


@dataclass
class SignatureAnnotation(Annotation):
    """Signature annotation (image-based)"""
    image_data: str = ""  # base64 PNG
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'pageNum': self.page_num,
            'type': 'signature',
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'imageData': self.image_data,
        }
    
    def validate(self) -> bool:
        """Validate signature annotation"""
        if not self.image_data:
            return False
        if not self.image_data.startswith(('data:image', 'iVBOR')):
            return False
        if self.width <= 0 or self.height <= 0:
            return False
        return True


@dataclass
class HighlightAnnotation(Annotation):
    """Highlight annotation"""
    color: str = "#FFFF00"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'pageNum': self.page_num,
            'type': 'highlight',
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'color': self.color,
        }
    
    def validate(self) -> bool:
        """Validate highlight annotation"""
        if self.width <= 0 or self.height <= 0:
            return False
        return True


@dataclass
class CommentAnnotation(Annotation):
    """Comment annotation"""
    text: str = ""
    color: str = "#FF0000"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'pageNum': self.page_num,
            'type': 'comment',
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'text': self.text,
            'color': self.color,
        }
    
    def validate(self) -> bool:
        """Validate comment annotation"""
        if self.width <= 0 or self.height <= 0:
            return False
        return True


def annotation_factory(data: Dict[str, Any]) -> Annotation:
    """Factory to create appropriate annotation type (Dependency Inversion)"""
    ann_type = data.get('type', 'text').lower()
    
    if ann_type == 'text':
        return TextAnnotation(
            id=data.get('id', ''),
            page_num=data.get('pageNum', 0),
            x=data.get('x', 0),
            y=data.get('y', 0),
            width=data.get('width', 150),
            height=data.get('height', 30),
            text=data.get('text', ''),
            font_size=data.get('fontSize', 12),
            font_family=data.get('fontFamily', 'Arial'),
            color=data.get('color', '#000000'),
        )
    elif ann_type == 'drawing':
        return DrawingAnnotation(
            id=data.get('id', ''),
            page_num=data.get('pageNum', 0),
            x=data.get('x', 0),
            y=data.get('y', 0),
            width=data.get('width', 420),
            height=data.get('height', 595),
            image_data=data.get('imageData', ''),
        )
    elif ann_type == 'signature':
        return SignatureAnnotation(
            id=data.get('id', ''),
            page_num=data.get('pageNum', 0),
            x=data.get('x', 0),
            y=data.get('y', 0),
            width=data.get('width', 420),
            height=data.get('height', 200),
            image_data=data.get('imageData', ''),
        )
    elif ann_type == 'highlight':
        return HighlightAnnotation(
            id=data.get('id', ''),
            page_num=data.get('pageNum', 0),
            x=data.get('x', 0),
            y=data.get('y', 0),
            width=data.get('width', 100),
            height=data.get('height', 20),
            color=data.get('color', '#FFFF00'),
        )
    elif ann_type == 'comment':
        return CommentAnnotation(
            id=data.get('id', ''),
            page_num=data.get('pageNum', 0),
            x=data.get('x', 0),
            y=data.get('y', 0),
            width=data.get('width', 100),
            height=data.get('height', 50),
            text=data.get('text', ''),
            color=data.get('color', '#FF0000'),
        )
    else:
        raise ValueError(f"Unknown annotation type: {ann_type}")
