#!/usr/bin/env python
"""Inspect which pdf_exporter.py is being loaded and what it contains"""
import sys
sys.path.insert(0, '.')

from pdf_exporter import PDFExporter
import inspect

print("PDFExporter file location:", inspect.getfile(PDFExporter))
print("\nPDFExporter.export() source code location:", inspect.getfile(PDFExporter.export))

# Get the source code of the export method
source = inspect.getsource(PDFExporter.export)
print("\nFirst 500 characters of export() method:")
print(source[:500])
print("\n...")
print("\nLast 500 characters of export() method:")
print(source[-500:])

# Check if it mentions BytesIO
if "BytesIO" in source:
    print("\n✓ BytesIO found in source code")
else:
    print("\n✗ BytesIO NOT found in source code!")

# Check if it mentions exports folder  
if "exports" in source:
    print("✗ 'exports' folder reference found in source code!")
else:
    print("✓ 'exports' folder NOT found in source code")
