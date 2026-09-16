import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
from app.extractor import DocumentExtractor

ext = DocumentExtractor()
with open('scratch/ocr_text_2004.txt', encoding='utf-8') as f:
    text = f.read()

res = ext.extract(text, doc_type='sale_deed', filename='Sale deed_188_2004.pdf')
fields = res.get('fields', {})
checklist = res.get('checklist', [])

print('=== 2004 DEED KEY FIELDS ===')
for k, v in fields.items():
    if k != 'checklist':
        print(f"[{k}]: {v.get('value')}")

print('\n=== 2004 DEED CHECKLIST (18 items) ===')
for i, c in enumerate(checklist):
    status = 'PASSED' if c.get('is_valid') else 'FLAGGED'
    print(f"{i+1}. [{status}] {c.get('title')}: {c.get('details')}")
