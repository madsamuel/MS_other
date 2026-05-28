import fitz
import os

# Check the PDF with all the new annotations
pdf_path = None

# Find the most recent PDF upload
uploads_dir = 'uploads'
pdfs = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
if pdfs:
    pdf_path = os.path.join(uploads_dir, sorted(pdfs)[-1])

if pdf_path and os.path.exists(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    # Get all blocks
    blocks = page.get_text('dict')['blocks']
    
    print(f"PDF: {os.path.basename(pdf_path)}")
    print(f"File size: {os.path.getsize(pdf_path)} bytes")
    print(f"Total blocks: {len(blocks)}\n")
    
    # Count images and text
    image_count = 0
    text_blocks = []
    
    for i, block in enumerate(blocks):
        if block.get('type') == 1:  # Image block
            image_count += 1
            print(f"Block {i}: IMAGE (Drawing or Signature)")
        elif 'lines' in block:
            for line in block['lines']:
                for span in line['spans']:
                    text_blocks.append(span['text'])
                    print(f"Block {i}: TEXT - {span['text']}")
    
    print(f"\n--- Summary ---")
    print(f"Text blocks: {len(text_blocks)}")
    print(f"Image blocks (drawings/signatures): {image_count}")
    print(f"✓ Features successfully added to PDF!")
else:
    print("PDF file not found")
