from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

# Create uploads folder if it doesn't exist
os.makedirs('uploads', exist_ok=True)

# Create a simple PDF with some text
c = canvas.Canvas('uploads/fresh_test.pdf', pagesize=letter)
c.setFont("Helvetica", 12)
c.drawString(100, 750, "Original Test PDF - Page 1")
c.drawString(100, 700, "This is a test PDF for BananaPDF text insertion testing")
c.save()

print("✓ Created fresh_test.pdf")
print(f"File size: {os.path.getsize('uploads/fresh_test.pdf')} bytes")
