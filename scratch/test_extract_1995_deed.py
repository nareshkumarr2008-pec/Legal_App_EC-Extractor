import time
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from app.ocr_engine import OCREngine
from app.extractors.sale_deed_extractor import SaleDeedExtractor

pdf_path = r"C:\Users\nares\Downloads\Sale deed_6027_1995.pdf"

print("Running OCR on 1995 Sale Deed (Pages 1, 3, 5, 7, 9, 11, 13, 19, 21)...")
engine = OCREngine()
# Test odd pages which contain text (even pages are reverse blank/endorsement sheets)
target_pages = "1,3,5,7,9,11,13,19,21"
t0 = time.time()
ocr_res = engine.process_file(pdf_path, "Sale deed_6027_1995.pdf", lang="ta", page_range=target_pages)
print(f"OCR finished in {time.time()-t0:.2f}s")

full_text = ocr_res["aggregated_text"]
print(f"Full text length: {len(full_text)}")

# Save full text to scratch
with open("scratch/ocr_text_1995.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

extractor = SaleDeedExtractor()
ext_res = extractor.extract(full_text)

print("\n=== CURRENT EXTRACTION RESULTS ===")
for k, v in ext_res.items():
    if k != "checklist":
        val = v.get("value") if isinstance(v, dict) else v
        print(f"{k}: {val}")

print("\n=== CHECKLIST RESULTS ===")
for item in ext_res.get("checklist", []):
    status = "PASSED" if item["is_valid"] else "FLAGGED"
    print(f"[{status}] {item['title']}: {item['details']}")
