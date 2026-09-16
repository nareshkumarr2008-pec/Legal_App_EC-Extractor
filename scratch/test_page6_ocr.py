import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import pypdfium2 as pdfium
from app.ocr_engine import OCREngine
ocr_engine = OCREngine()

pdf_path = "C:/Users/nares/Downloads/Sale Deed_3978_2010 - Naagesh.pdf"
pdf = pdfium.PdfDocument(pdf_path)
print("Total pages:", len(pdf))

print("Rendering page 6...")
page = pdf[5]
pil_img = page.render(scale=2.0).to_pil()
print("Page 6 image size:", pil_img.size)

print("Starting PaddleOCR...")
t0 = time.time()
res = ocr_engine.process_image(pil_img, lang="ta")
dur = time.time() - t0
print(f"Page 6 completed in {dur:.2f}s, lines: {len(res.get('lines', []))}")
for l in res.get("lines", []):
    print("Line:", l.get("text"))
