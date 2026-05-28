#!/usr/bin/env python
"""Test if PDF save is working"""

import os
import sys
import fitz
import tempfile
import shutil
from datetime import datetime

# Test file path
test_pdf_path = os.path.join('uploads', 'fresh_test.pdf')

print(f"Testing PDF save functionality...")
print(f"PDF path: {test_pdf_path}")
print(f"File exists: {os.path.exists(test_pdf_path)}")

if not os.path.exists(test_pdf_path):
    print(f"ERROR: PDF file not found!")
    sys.exit(1)

# Get file size before
size_before = os.path.getsize(test_pdf_path)
print(f"File size before: {size_before} bytes")

# Open PDF
print("\nOpening PDF...")
doc = fitz.open(test_pdf_path)
print(f"✓ PDF opened successfully")
print(f"Pages: {doc.page_count}")

# Get page 0
page = doc[0]
print(f"✓ Page 0 accessed")

# Create a rect for text
rect = fitz.Rect(100, 100, 250, 130)
print(f"✓ Created rect: {rect}")

# Insert text
text = f"TEST at {datetime.now().strftime('%H:%M:%S')}"
print(f"Inserting text: '{text}'")
page.insert_textbox(rect, text, fontsize=12, color=(0, 0, 0))
print(f"✓ Text inserted into page")

# Save the PDF to a temporary file, then replace the original
print(f"\nSaving PDF...")
temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
os.close(temp_fd)

try:
    doc.save(temp_path)
    print(f"✓ PDF saved to temp file: {temp_path}")
    
    # Replace original with temp file
    shutil.move(temp_path, test_pdf_path)
    print(f"✓ Replaced original file with updated version")
except Exception as e:
    print(f"ERROR: {e}")
    if os.path.exists(temp_path):
        os.remove(temp_path)
    sys.exit(1)

# Get file size after
size_after = os.path.getsize(test_pdf_path)
print(f"File size after: {size_after} bytes")
print(f"Size changed: {size_after != size_before} (before: {size_before}, after: {size_after})")

# Close document
doc.close()
print(f"✓ PDF closed")

# Verify by reading the file back
print(f"\n--- Verifying saved PDF ---")
doc2 = fitz.open(test_pdf_path)
page2 = doc2[0]
text_dict = page2.get_text('dict')

print(f"Number of blocks: {len(text_dict['blocks'])}")
for i, block in enumerate(text_dict['blocks']):
    if block.get('type') == 1:  # Text
        print(f"Block {i}: {block.get('bbox')} - Text found")
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                print(f"  Text: {span.get('text')}")

doc2.close()
print("\n✓ Test complete!")
