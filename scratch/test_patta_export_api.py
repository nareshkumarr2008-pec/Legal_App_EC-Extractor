import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from app.server import app

client = TestClient(app)
pdf_path = "C:/Users/nares/.gemini/antigravity-ide/brain/c0843d56-25be-489c-a1ff-5484e7b05a64/.user_uploaded/media_1789880958984.pdf"

with open(pdf_path, "rb") as f:
    ocr_res = client.post(
        "/api/ocr/process",
        files={"file": ("patta_doc_324.pdf", f, "application/pdf")},
        data={"doc_type": "patta", "lang": "ta"}
    )

print("OCR status:", ocr_res.status_code)
if ocr_res.status_code == 200:
    res_data = ocr_res.json()
    extraction = res_data.get("extracted_data", {})
    
    # Now simulate the frontend calling /api/export
    for lang in ["en", "ta", "both"]:
        payload = {
            "format": "pdf",
            "doc_type": "patta",
            "filename": "patta_doc_324.pdf",
            "total_pages": res_data.get("total_pages", 2),
            "extraction": extraction,
            "fields": extraction.get("fields", {}),
            "checklist": [],
            "lang": lang
        }
        exp_res = client.post("/api/export", json=payload)
        print(f"Export lang={lang} status: {exp_res.status_code}, content-len: {len(exp_res.content)}")
        if exp_res.status_code != 200:
            print("Export error:", exp_res.text)
        else:
            with open(f"scratch/patta_exported_{lang}.pdf", "wb") as f_out:
                f_out.write(exp_res.content)
            print(f"Saved scratch/patta_exported_{lang}.pdf")
else:
    print("OCR error:", ocr_res.text)
