# BananaPDF - SOLID Refactoring

## Overview
The BananaPDF application has been refactored to follow SOLID principles, resulting in a more maintainable, testable, and extensible architecture.

## SOLID Principles Applied

### 1. Single Responsibility Principle (SRP)

**Before**: `app.py` was a 1000+ line monolith handling uploads, rendering, saving, and state management.

**After**: Each class has a single responsibility:
- `PDFService`: PDF loading and page management
- `AnnotationService`: Annotation storage and retrieval
- `FileService`: File I/O operations
- `ExportService`: PDF export orchestration
- `Flask routes`: Request handling only

**Benefits**:
- Each class is easy to understand and modify
- Changes to PDF handling don't affect annotation handling
- File operations are isolated for easier testing

### 2. Open/Closed Principle (OCP)

**Before**: Adding new annotation types required modifying `AnnotationManager` class.

**After**: 
- Created `Annotation` base class with specific implementations
- Used `annotation_factory()` to create instances
- New annotation types can be added by creating a subclass without modifying existing code

**Example**: To add a new "Rectangle" annotation type:
```python
class RectangleAnnotation(Annotation):
    color: str = "#FF0000"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'pageNum': self.page_num,
            'type': 'rectangle',
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'color': self.color,
        }
    
    def validate(self) -> bool:
        return self.width > 0 and self.height > 0
```

Then update `annotation_factory()` to handle the new type. **No existing code changes needed**.

### 3. Liskov Substitution Principle (LSP)

**Before**: Different annotation types were stored as generic dictionaries.

**After**: All annotation types inherit from `Annotation` base class:
```python
# Can use any Annotation subclass interchangeably
annotations: List[Annotation] = [
    TextAnnotation(...),
    DrawingAnnotation(...),
    SignatureAnnotation(...),
]

for ann in annotations:
    print(ann.to_dict())  # Works for all types
```

**Benefits**:
- Polymorphism reduces if/else type checking
- Type hints provide better IDE support
- Subclasses are guaranteed to have required methods

### 4. Interface Segregation Principle (ISP)

**Before**: `AnnotationManager` had many unrelated methods crammed together.

**After**: Clients depend only on what they need:
- `AnnotationService` provides annotation-specific methods
- `PDFService` provides PDF-specific methods
- `FileService` provides file-specific methods

Each service exposes only the methods relevant to its domain.

### 5. Dependency Inversion Principle (DIP)

**Before**: Global variables (`pdf_handler`, `annotation_manager`, `current_session`) created tight coupling.

**After**: Dependency Injection:
```python
# Initialize services at app startup
file_service = FileService(UPLOAD_FOLDER)
annotation_service = AnnotationService()
pdf_service = PDFService()
export_service = ExportService('exports')

# Routes receive injected services
@app.route('/api/add-annotation', methods=['POST'])
def add_annotation():
    # Uses injected annotation_service
    annotation = annotation_service.add_annotation(data)
```

**Benefits**:
- Easier to test (inject mock services)
- Can swap implementations without changing code
- Services are decoupled from Flask routes

## File Structure

```
BananaPDF/
├── app.py                          # Original app (for comparison)
├── app_refactored.py              # Refactored Flask app (thin layer)
├── models/
│   ├── __init__.py
│   └── annotation.py              # Annotation base class + subclasses
├── services/
│   ├── __init__.py
│   ├── annotation_service.py      # Annotation management
│   ├── pdf_service.py             # PDF operations
│   ├── file_service.py            # File I/O
│   └── export_service.py          # PDF export
├── pdf_handler.py                  # Existing (unchanged)
├── pdf_exporter.py                 # Existing (minimally modified)
└── (other files...)
```

## How to Use the Refactored Code

### Option 1: Run the refactored version:
```bash
python app_refactored.py
```

### Option 2: Gradually migrate from old to new:
1. Copy services and models to your project
2. Update routes one at a time to use new services
3. Run both `app.py` and `app_refactored.py` in parallel for comparison

## Testing Benefits

With SOLID architecture, testing is much easier:

```python
# Test annotation validation without Flask
def test_text_annotation_validation():
    ann = TextAnnotation(
        id='test',
        page_num=0,
        x=0, y=0,
        width=100, height=30,
        text='Hello'
    )
    assert ann.validate() == True
    
    ann.text = ''  # Invalid
    assert ann.validate() == False

# Test service independently
def test_annotation_service():
    service = AnnotationService()
    service.add_annotation({'type': 'text', 'text': 'Hello', ...})
    assert len(service.get_all_annotations()['0']) == 1

# Test with mock PDFService
def test_save_with_mock_pdf():
    mock_pdf_service = MockPDFService()
    export_service = ExportService()
    # export_service works with mock without real PDF
```

## Migration Checklist

- [ ] Copy `models/` folder to your project
- [ ] Copy `services/` folder to your project
- [ ] Test services independently
- [ ] Create integration tests with `app_refactored.py`
- [ ] Update frontend if needed (should be compatible)
- [ ] Gradually replace routes in `app.py` with `app_refactored.py` routes
- [ ] Remove global variables from `app.py`
- [ ] Update `pdf_exporter.py` if needed

## Future Improvements

1. **Repository Pattern**: Move session management to `SessionRepository`
2. **Event Bus**: For loose coupling between services
3. **Async Operations**: Use async/await for long-running operations
4. **Logging Configuration**: Extract to separate config file
5. **Error Handling**: Create custom exception types for different errors
6. **Validation**: Move validation logic to separate validators
7. **Caching**: Add caching layer for page dimensions, etc.

## Comparison: Old vs New

| Aspect | Old | New |
|--------|-----|-----|
| Global Variables | 3 globals | 0 globals |
| Service Coupling | Tight | Loose |
| Testing | Hard | Easy |
| Adding Features | Modify existing code | Extend with new classes |
| Code Reusability | Low | High |
| Type Safety | Weak | Strong |
| Line Count | 1000+ | Split across modules |

## Summary

The refactored code follows SOLID principles to create:
- **Maintainable**: Clear separation of concerns
- **Testable**: Each service can be tested independently
- **Extensible**: New features added without modifying existing code
- **Readable**: Each class has a single, clear purpose
- **Scalable**: Easier to add new annotation types, services, or features
