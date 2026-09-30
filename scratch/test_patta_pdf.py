import sys
import os
sys.path.insert(0, os.path.abspath("."))

from app.samples import SAMPLES
from app.pdf_generator import generate_ocr_pdf_report
import json

patta_sample = SAMPLES.get("patta")
if not patta_sample:
    print("No patta sample in SAMPLES! Looking at keys:", list(SAMPLES.keys()))
else:
    print("Found patta sample! Keys:", list(patta_sample.keys()))
    payload = {
        "format": "pdf",
        "doc_type": "patta",
        "filename": "Sample_Patta.pdf",
        "total_pages": 2,
        "fields": patta_sample.get("extracted_data", {}).get("fields", {}),
        "extraction": patta_sample.get("extracted_data", {}),
        "lang": "en"
    }
    for l in ["en", "ta", "both"]:
        try:
            pdf_bytes = generate_ocr_pdf_report(payload, lang=l)
            print(f"Patta PDF ({l}) generated successfully: {len(pdf_bytes)} bytes")
        except Exception as e:
            print(f"FAILED for lang={l}: {e}")
            import traceback
            traceback.print_exc()
