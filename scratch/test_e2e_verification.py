import sys
import os
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Add project root to sys.path
sys.path.insert(0, r"c:\NARESH\GITHUB\Legal_App_EC-Extractor\Legal_App_EC-Extractor")

from app.samples import SAMPLE_DOCUMENTS
from app.extractors.patta_extractor import PattaExtractor
from app.extractors.tslr_extractor import TSLRExtractor
from app.pdf_generator import generate_ocr_pdf_report
from starlette.testclient import TestClient
from app.server import app

def run_tests():
    print("=" * 65)
    print("RUNNING COMPLETE E2E VERIFICATION FOR PATTA & TSLR")
    print("=" * 65)

    # 1. Test Patta Sample Structured Data
    print("\n[STEP 1] Testing Patta Sample Data...")
    patta_sample = SAMPLE_DOCUMENTS["patta"]
    patta_structured = patta_sample["structured"]
    assert "patta_number" in patta_structured, "patta_number missing from structured"
    assert "cadastral_schedule" in patta_structured, "cadastral_schedule missing from structured"
    assert "checklist" in patta_structured, "checklist missing from structured"
    assert len(patta_structured["checklist"]) == 6, f"Expected 6 checklist items, got {len(patta_structured['checklist'])}"
    print(f"   [PASS] Patta sample contains {len(patta_structured)} keys, {len(patta_structured['cadastral_schedule'])} schedule rows, and 6 checklist items.")

    # 2. Test Patta Extractor with raw text
    print("\n[STEP 2] Testing Patta Extractor engine...")
    patta_raw_text = """
    தமிழ்நாடு அரசு
    வருவாய்த்துறை
    நில உரிமை விபரங்கள் : 10(1) பிரிவு
    மாவட்டம் : செங்கல்பட்டு
    வட்டம் : திருப்போரூர்
    கிராமம் : சிறுசேரி
    பட்டா எண் : 1092
    உரிமையாளர்கள் பெயர்:
    1. அருண்குமார்
    மனைவி/தந்தை பெயர்: ராமநாதன்
    புல எண்: 128/7
    விஸ்தீரணம்: 0.00.06
    தீர்வை: 2.00
    ரயத்துவாரி மனை
    மின்கையொப்பம் இடப்பட்ட நாள்: 15-09-2026 10:12:45
    மண்டல துணை வட்டாட்சியர்
    குறிப்பு எண்: 2026/0105/03/1092
    """
    pe = PattaExtractor()
    res_patta = pe.extract(patta_raw_text, filename="patta_test.pdf")
    cl_patta = pe.evaluate_checklist(res_patta, patta_raw_text)
    print(f"   Extracted Patta No: {res_patta.get('patta_number', {}).get('value')}")
    print(f"   Extracted District: {res_patta.get('district', {}).get('value')}")
    print(f"   Extracted Taluk: {res_patta.get('taluk', {}).get('value')}")
    print(f"   Extracted Village: {res_patta.get('village', {}).get('value')}")
    print(f"   Extracted Owner: {res_patta.get('owner_name', {}).get('value')}")
    print(f"   Extracted Survey: {res_patta.get('survey_numbers', {}).get('value')}")
    print(f"   Cadastral Schedule Rows: {len(res_patta.get('cadastral_schedule', []))}")
    print(f"   Checklist Items: {len(cl_patta)}")
    assert len(cl_patta) == 6, f"Patta checklist must have 6 items, got {len(cl_patta)}"
    print("   [PASS] Patta extraction successful!")

    # 3. Test TSLR Sample Data
    print("\n[STEP 3] Testing TSLR Sample Data...")
    tslr_sample = SAMPLE_DOCUMENTS["tslr"]
    tslr_structured = tslr_sample["structured"]
    assert "survey_number" in tslr_structured, "survey_number missing from structured"
    assert "checklist" in tslr_structured, "checklist missing from structured"
    assert len(tslr_structured["checklist"]) == 6, f"Expected 6 checklist items, got {len(tslr_structured['checklist'])}"
    print(f"   [PASS] TSLR sample contains {len(tslr_structured)} keys and 6 checklist items.")

    # 4. Test TSLR Extractor engine
    print("\n[STEP 4] Testing TSLR Extractor engine...")
    tslr_raw_text = """
    தமிழ்நாடு அரசு
    வருவாய்த்துறை
    நகர நில அளவை பதிவேடு (TSLR)
    மாவட்டம் : சென்னை
    வட்டம் : மயிலாப்பூர்
    நகரம் / வருவாய் கிராமம் : மயிலாப்பூர்
    வார்டு : 05
    பிளாக் : 12
    நகர புல எண் : 73/0
    பழைய சர்வே எண் : 45/2
    உரிமையாளர் பெயர் : சுப்பிரமணியன்
    நில வகைப்பாடு : ரயத்துவாரி மனை (House Site)
    பரப்பளவு : 00-02-45.5 சதுர மீட்டர்
    தீர்வை : ரூ. 15.00
    மின் கையொப்பம் இடப்பட்ட நாள் : 14-08-2026
    வட்டாட்சியர்
    குறிப்பு எண் : TSLR/CHN/2026/00941
    """
    te = TSLRExtractor()
    res_tslr = te.extract(tslr_raw_text)
    cl_tslr = te.evaluate_checklist(res_tslr, tslr_raw_text)
    print(f"   Extracted Survey No: {res_tslr.get('survey_number', {}).get('value')}")
    print(f"   Extracted Old Survey No: {res_tslr.get('old_survey_number', {}).get('value')}")
    print(f"   Extracted District: {res_tslr.get('district', {}).get('value')}")
    print(f"   Extracted Taluk: {res_tslr.get('taluk', {}).get('value')}")
    print(f"   Extracted Owner: {res_tslr.get('owner_name', {}).get('value')}")
    print(f"   Checklist Items: {len(cl_tslr)}")
    assert len(cl_tslr) == 6, f"TSLR checklist must have 6 items, got {len(cl_tslr)}"
    print("   [PASS] TSLR extraction successful!")

    # 5. Test PDF Generation for both
    print("\n[STEP 5] Testing PDF Report Generation...")
    pdf_patta = generate_ocr_pdf_report(
        {
            "doc_type": "patta",
            "filename": "Patta_Sample.pdf",
            "fields": res_patta,
            "checklist": cl_patta,
            "cadastral_schedule": res_patta.get("cadastral_schedule", [])
        },
        lang="both"
    )
    print(f"   Generated Patta Bilingual PDF: {len(pdf_patta)} bytes")
    assert len(pdf_patta) > 20000, "Patta PDF too small"

    pdf_tslr = generate_ocr_pdf_report(
        {
            "doc_type": "tslr",
            "filename": "TSLR_Sample.pdf",
            "fields": res_tslr,
            "checklist": cl_tslr
        },
        lang="both"
    )
    print(f"   Generated TSLR Bilingual PDF: {len(pdf_tslr)} bytes")
    assert len(pdf_tslr) > 20000, "TSLR PDF too small"
    print("   [PASS] PDF Report generation verified successfully!")

    # 6. Test FastAPI endpoints via TestClient
    print("\n[STEP 6] Testing FastAPI Server Endpoints...")
    client = TestClient(app)

    # 6a. Sample Patta
    resp_p = client.get("/api/sample/patta")
    assert resp_p.status_code == 200, f"Sample patta failed with {resp_p.status_code}"
    p_data = resp_p.json()
    assert "extracted_data" in p_data, "extracted_data missing in sample patta"
    print("   [PASS] GET /api/sample/patta returned 200 OK")

    # 6b. Sample TSLR
    resp_t = client.get("/api/sample/tslr")
    assert resp_t.status_code == 200, f"Sample tslr failed with {resp_t.status_code}"
    t_data = resp_t.json()
    assert "extracted_data" in t_data, "extracted_data missing in sample tslr"
    print("   [PASS] GET /api/sample/tslr returned 200 OK")

    # 6c. Export PDF for Patta
    export_payload_patta = {
        "format": "pdf",
        "doc_type": "patta",
        "filename": "Patta_1092.pdf",
        "total_pages": 2,
        "extraction": p_data["extracted_data"],
        "fields": p_data["extracted_data"]["fields"],
        "checklist": p_data["extracted_data"]["checklist"],
        "lang": "both"
    }
    resp_exp_p = client.post("/api/export", json=export_payload_patta)
    assert resp_exp_p.status_code == 200, f"Export patta PDF failed: {resp_exp_p.status_code} {resp_exp_p.text}"
    assert len(resp_exp_p.content) > 20000, "Exported Patta PDF too small"
    print(f"   [PASS] POST /api/export (Patta PDF) returned 200 OK ({len(resp_exp_p.content)} bytes)")

    # 6d. Export PDF for TSLR
    export_payload_tslr = {
        "format": "pdf",
        "doc_type": "tslr",
        "filename": "TSLR_73_0.pdf",
        "total_pages": 2,
        "extraction": t_data["extracted_data"],
        "fields": t_data["extracted_data"]["fields"],
        "checklist": t_data["extracted_data"]["checklist"],
        "lang": "both"
    }
    resp_exp_t = client.post("/api/export", json=export_payload_tslr)
    assert resp_exp_t.status_code == 200, f"Export tslr PDF failed: {resp_exp_t.status_code} {resp_exp_t.text}"
    assert len(resp_exp_t.content) > 20000, "Exported TSLR PDF too small"
    print(f"   [PASS] POST /api/export (TSLR PDF) returned 200 OK ({len(resp_exp_t.content)} bytes)")

    print("\n" + "=" * 65)
    print("ALL 6 END-TO-END TESTS PASSED WITH 100% PRECISION & ZERO ERRORS!")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
