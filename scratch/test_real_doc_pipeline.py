import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import time
from app.ocr_engine import OCREngine
from app.extractor import DocumentExtractor

pdf_path = "C:/Users/nares/Downloads/Sale Deed_3978_2010 - Naagesh.pdf"
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

print(f"Loaded {pdf_path}: {len(pdf_bytes)} bytes")
ocr_engine = OCREngine()
extractor = DocumentExtractor()

t0 = time.time()
print("Starting OCR processing of PDF...")
ocr_result = ocr_engine.process_file(pdf_bytes, filename="Sale Deed_3978_2010 - Naagesh.pdf", lang="ta")
print(f"OCR finished in {time.time() - t0:.2f}s across {len(ocr_result.get('pages', []))} pages")

t1 = time.time()
print("Starting field extraction...")
extracted = extractor.extract(ocr_result["aggregated_text"], doc_type="sale_deed", pages=ocr_result['pages'])
print(f"Extraction finished in {time.time() - t1:.2f}s")

fields = extracted.get("fields", {})
with open("scratch/final_real_fields.json", "w", encoding="utf-8") as f:
    json.dump(fields, f, ensure_ascii=False, indent=2)
print("Dumped to scratch/final_real_fields.json successfully!")
