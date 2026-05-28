import fitz

doc = fitz.open(r'c:\code\MS_other\experiments\python\BananaPDF\uploads\fresh_test.pdf')
page = doc[0]

print(f'Page mediabox: {page.mediabox}')

text_dict = page.get_text('dict')
blocks = text_dict.get('blocks', [])

print(f'Total blocks: {len(blocks)}')
print('\nBlock types:')

for i, block in enumerate(blocks):
    print(f'Block {i}: type={block.get("type")} (type 1=text, type 3=image, etc)')
    if block.get('type') == 1:  # text block
        lines = block.get('lines', [])
        print(f'  {len(lines)} lines')
        for line in lines:
            for span in line.get('spans', []):
                text = span.get('text', '')
                if text.strip():
                    print(f'    Text: "{text}" at {span.get("bbox")}')

print('\n--- Checking for added textboxes ---')
print('All blocks:')
for i, block in enumerate(blocks):
    print(f'Block {i}: {block}')
