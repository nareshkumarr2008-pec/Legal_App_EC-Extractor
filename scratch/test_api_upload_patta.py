import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from app.server import app

client = TestClient(app)

pdf_path = "C:/Users/nares/.gemini/antigravity-ide/brain/c0843d56-25be-489c-a1ff-5484e7b05a64/.user_uploaded/media_1789880958984.pdf"

with open(pdf_path, "rb") as f:
    response = client.post(
        "/api/ocr/process",
        files={"file": ("patta_doc_324.pdf", f, "application/pdf")},
        data={"doc_type": "patta", "lang": "ta"}
    )

print("Status Code:", response.status_code)
if response.status_code == 200:
    data = response.json()
    fields = data.get("extracted_data", {}).get("fields", {})
    print("=== API END-TO-END UPLOAD EXTRACTION RESULTS ===")
    print("Patta Number:", fields.get("patta_number", {}).get("value"))
    print("Owner Name:", fields.get("owner_name", {}).get("value"))
    print("District:", fields.get("district", {}).get("value"))
    print("Taluk:", fields.get("taluk", {}).get("value"))
    print("Village:", fields.get("village", {}).get("value"))
    print("Survey Numbers:", fields.get("survey_numbers", {}).get("value"))
    print("Extent Details:\n", fields.get("extent_details", {}).get("value"))
    print("Nature of Land:", fields.get("nature_of_land", {}).get("value"))
    print("Total Tax:", fields.get("total_tax", {}).get("value"))
    print("Portal Reference:", fields.get("portal_reference", {}).get("value"))
else:
    print("Error:", response.text)
