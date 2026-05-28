import fitz
import json

doc = fitz.open(r'c:\code\MS_other\experiments\python\BananaPDF\uploads\20260525_151817_1.pdf')
page = doc[0]

print(f'Page mediabox: {page.mediabox}')
print(f'Page rect: {page.rect}')

# Get all text blocks to find any added text
text_dict = page.get_text('dict')
blocks = text_dict.get('blocks', [])

print(f'\nTotal blocks: {len(blocks)}')
print('\nSearching for recent additions...')

found_test = False
for i, block in enumerate(blocks):
    if block.get('type') == 1:  # text block
        bbox = block.get('bbox')
        lines = block.get('lines', [])
        for line in lines:
            spans = line.get('spans', [])
            for span in spans:
                text = span.get('text', '')
                if 'TEST' in text or 'TOPLEFT' in text or 'DEBUG' in text or 'CENTER' in text or 'MIDDLE' in text:
                    print(f'\n✓ Found: "{text}"')
                    print(f'  Block bbox: {bbox}')
                    print(f'  Span: {span}')
                    found_test = True

if not found_test:
    print('\n⚠ No test text found on page')
    print('\nAll text blocks:')
    for i, block in enumerate(blocks):
        if block.get('type') == 1:
            lines = block.get('lines', [])
            for line_idx, line in enumerate(lines):
                spans = line.get('spans', [])
                for span_idx, span in enumerate(spans):
                    text = span.get('text', '')
                    print(f'Block {i}, Line {line_idx}, Span {span_idx}: "{text[:50]}"')

doc.close()
