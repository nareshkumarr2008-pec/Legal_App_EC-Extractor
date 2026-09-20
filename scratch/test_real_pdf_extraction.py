import sys
import json
from app.ocr_engine import OCREngine
from app.extractors.patta_extractor import PattaExtractor

pdf_path = r"C:\Users\nares\.gemini\antigravity-ide\brain\c0843d56-25be-489c-a1ff-5484e7b05a64\.user_uploaded\media_1789880958984.pdf"

ocr = OCREngine()
with open(pdf_path, "rb") as f:
    doc = ocr.process_file(f.read(), "media_1789880958984.pdf")

ext = PattaExtractor()
fields = ext.extract(doc)

out = {
    "fields": {k: v.get("value") for k, v in fields.items() if isinstance(v, dict) and "value" in v},
    "cadastral_schedule": fields.get("cadastral_schedule", [])
}

with open("scratch/real_pdf_result.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print("SUCCESSFULLY EXTRACTED AND SAVED TO scratch/real_pdf_result.json")
