import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pdfplumber
import pypdfium2 as pdfium
from app.ocr_engine import OCREngine

pdf_path = "C:/Users/nares/Downloads/Sale Deed_3978_2010 - Naagesh.pdf"
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

engine = OCREngine()
t0 = time.time()
with pdfplumber.open(pdf_path) as pdf_plum:
    num_pages = len(pdf_plum.pages)
    print(f"Opened PDF with {num_pages} pages in {time.time()-t0:.2f}s")
    for i, page in enumerate(pdf_plum.pages):
        p_t0 = time.time()
        lines, words = engine._extract_native_pdf_lines(page, float(page.width), float(page.height))
        txt = page.extract_text() or ""
        print(f"Page {i+1:02d}: lines={len(lines)}, words={len(words)}, text_len={len(txt.strip())} in {time.time()-p_t0:.3f}s")

print(f"Total time for all 35 pages: {time.time()-t0:.2f}s")
