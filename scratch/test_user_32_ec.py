# scratch/test_user_32_ec.py
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from app.ocr_engine import OCREngine
from app.extractor import DocumentExtractor
import json

p = r"C:\Users\nares\.gemini\antigravity-ide\brain\d334da03-d61c-47a1-ba36-7733443c83fd\.user_uploaded\media_1789384674570.pdf"
with open(p, 'rb') as f:
    content = f.read()

print(f"Read PDF: {len(content)} bytes")
ocr = OCREngine()
ocr_res = ocr.process_file(content, 'test.pdf', lang='ta')
print(f"OCR finished: {len(ocr_res['pages'])} pages")

extractor = DocumentExtractor()
ext_res = extractor.extract(ocr_res['aggregated_text'], doc_type='ec', pages=ocr_res['pages'], file_bytes=content, filename='test.pdf')

fields = ext_res.get('fields', {})
print("search_period:", fields.get('search_period'))
print("search_period_standard:", fields.get('search_period_standard'))
print("survey_searched:", fields.get('survey_searched'))
print("property_extent:", fields.get('property_extent'))
print("active_mortgages:", fields.get('active_mortgages'))
print("court_attachments:", fields.get('court_attachments'))

txs = fields.get('transactions_table', {}).get('value', [])
print(f"\nExtracted {len(txs)} transactions:")
for i in [0, 3, 10, 15, 17, 18, 19, 21, 27, 28, 29, 30, 31]:
    if i < len(txs):
        t = txs[i]
        print(f"\n=== TX #{i+1} ===")
        print(f"Doc: {t.get('doc_no')} | Date: {t.get('date')} | Nature: {t.get('nature')}")
        print(f"Executants raw: {t.get('executants')}")
        print(f"Claimants raw:  {t.get('claimants')}")
        print(f"Consideration: {t.get('consideration')} | Cons Norm: {t.get('consideration_norm')}")
        print(f"Remarks: {t.get('remarks')}")
        print(f"Schedules: {t.get('schedules')}")
        print(f"Page index: {t.get('page_index')}")
