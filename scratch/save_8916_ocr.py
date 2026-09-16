import sys
sys.path.insert(0, '.')
from app.ocr_engine import OCREngine

engine = OCREngine()
pdf_path = r'C:\Users\nares\.gemini\antigravity-ide\brain\b2162b4d-ff00-4035-a909-5eee5b58910e\.user_uploaded\media_1789577779097.pdf'
with open(pdf_path, 'rb') as f:
    pdf_bytes = f.read()

ocr_res = engine.process_file(pdf_bytes, filename='Sale_Deed_8916_2010.pdf', lang='ta')
full_text = ocr_res.get('aggregated_text', '')
with open('scratch/ocr_text_8916_2010.txt', 'w', encoding='utf-8') as f:
    f.write(full_text)
print('OCR completed, total chars:', len(full_text))
for page in ocr_res.get('pages', []):
    pnum = page.get("page_number")
    txt = page.get("full_text", "")
    print(f"Page {pnum}: {len(txt)} chars")
