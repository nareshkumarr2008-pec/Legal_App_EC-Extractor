# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')
from app.ocr_engine import OCREngine
from app.extractors.tslr_extractor import TSLRExtractor

engine = OCREngine()
pdf_path = r"C:\Users\nares\Downloads\TSLR tst 1.pdf"
with open(pdf_path, 'rb') as f:
    pdf_bytes = f.read()

res = engine.process_file(pdf_bytes, "TSLR tst 1.pdf", lang="ta")
print("=== RAW OCR LINES ===")
for idx, page in enumerate(res.get("pages", [])):
    print(f"--- PAGE {idx+1} ({len(page.get('lines', []))} lines) ---")
    for l in page.get("lines", []):
        print(repr(l.get("text", "")))

ext = TSLRExtractor()
extracted = ext.extract(res.get("full_text", ""), pages=res.get("pages", []))
print("=== EXTRACTED OWNER NAME ===")
print(extracted.get("owner_name"))
