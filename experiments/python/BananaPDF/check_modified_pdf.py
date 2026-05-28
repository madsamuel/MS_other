import fitz
import os

# Check the uploaded file that was modified
pdf_path = r'c:\code\MS_other\experiments\python\BananaPDF\uploads\20260527_212641_fresh_test.pdf'

if os.path.exists(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    # Get all text blocks
    blocks = page.get_text('dict')['blocks']
    
    print(f"PDF: {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path)} bytes")
    print(f"Total blocks: {len(blocks)}\n")
    
    for i, block in enumerate(blocks):
        print(f"Block {i}:")
        if 'lines' in block:  # Text blocks
            for line in block['lines']:
                for span in line['spans']:
                    print(f"  Text: {span['text']}")
        else:
            print(f"  Type: {block.get('type', 'unknown')}")
else:
    print(f"File not found: {pdf_path}")
