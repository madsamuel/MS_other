#!/usr/bin/env python
"""Test if PyMuPDF can save to BytesIO"""
import fitz
import io

print("Testing PyMuPDF save to BytesIO...")

# Create a simple PDF
doc = fitz.open()
page = doc.new_page()
page.insert_text((100, 100), "Test PDF", fontsize=12)

print("Created PDF with one page")

# Try to save to BytesIO
try:
    print("Attempting to save to BytesIO buffer...")
    pdf_buffer = io.BytesIO()
    doc.save(pdf_buffer, filetype='pdf')
    print(f"✓ Success! Saved {pdf_buffer.tell()} bytes to BytesIO")
    
    # Check size
    pdf_buffer.seek(0, 2)
    size = pdf_buffer.tell()
    print(f"✓ Buffer size: {size} bytes")
    
    # Try to read back
    pdf_buffer.seek(0)
    data = pdf_buffer.read(100)
    print(f"✓ Read first 100 bytes: {data[:20]}...")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

doc.close()
