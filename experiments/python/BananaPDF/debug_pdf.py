import fitz

doc = fitz.open(r'c:\code\MS_other\experiments\python\BananaPDF\uploads\20260525_151817_1.pdf')
page = doc[0]

print(f'Page mediabox: {page.mediabox}')

# Get all text on the page
text_dict = page.get_text('dict')
blocks = text_dict.get('blocks', [])

print(f'Total text blocks: {len(blocks)}')

# Look for recently added text
for i, block in enumerate(blocks):
    if block.get('type') == 1:  # text block
        lines = block.get('lines', [])
        for line in lines:
            spans = line.get('spans', [])
            for span in spans:
                text = span.get('text', '')
                if 'TOPLEFT' in text or 'CENTER' in text or 'TOP-LEFT' in text:
                    print(f'Found text: {text}')
                    print(f'  Block {i}: {block.get("bbox")}')
                    print(f'  Span: {span}')
