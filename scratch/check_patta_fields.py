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

res_data = ocr_res.json()
print("res_data keys:", list(res_data.keys()))
ext = res_data.get("extracted_data") or res_data.get("extraction") or {}
print("ext keys:", list(ext.keys()))
fields = ext.get("fields", {})
print("fields count:", len(fields))
for k, v in fields.items():
    if isinstance(v, dict):
        print(f"{k}: {v.get('value')}")
    else:
        print(f"{k}: {v}")
