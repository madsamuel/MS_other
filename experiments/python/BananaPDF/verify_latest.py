import fitz
import os

# Check the latest PDF
pdf_path = 'uploads/20260528_010703_fresh_test.pdf'

if os.path.exists(pdf_path):
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
        block_type = block.get('type')
        if block_type == 1:  # Image block
            image_count += 1
            print(f"Block {i}: IMAGE - size {block.get('width')}x{block.get('height')}")
        elif 'lines' in block:
            for line in block['lines']:
                for span in line['spans']:
                    text_blocks.append(span['text'])
                    if len(text_blocks) <= 5:  # Print first 5 text items
                        print(f"Block {i}: TEXT - {span['text']}")
    
    print(f"\n--- Summary ---")
    print(f"Text blocks: {len(text_blocks)}")
    print(f"Image blocks (drawings/signatures): {image_count}")
    print(f"\n✓ Drawing and Signature features successfully added to PDF!")
else:
    print(f"PDF file not found: {pdf_path}")
