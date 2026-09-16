import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pdfplumber
from app.extractors.sale_deed_extractor import SaleDeedExtractor

pdf_path = "C:/Users/nares/Downloads/Sale Deed_3978_2010 - Naagesh.pdf"

all_text = []
pages_data = []

with pdfplumber.open(pdf_path) as pdf:
    for i, p in enumerate(pdf.pages):
        txt = p.extract_text() or ""
        pages_data.append({"page_number": i + 1, "full_text": txt})
        all_text.append(f"--- PAGE {i+1} ---\n" + txt)

full_combined_text = "\n".join(all_text)
print(f"Total pages extracted: {len(pages_data)}, Total text length: {len(full_combined_text)}")

extractor = SaleDeedExtractor()
fields = extractor.extract(full_combined_text)

with open("scratch/real_extraction_results.json", "w", encoding="utf-8") as f:
    json.dump(fields, f, ensure_ascii=False, indent=2)

print("Results written to scratch/real_extraction_results.json successfully!")
