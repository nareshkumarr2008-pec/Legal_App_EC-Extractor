# -*- coding: utf-8 -*-
"""Comprehensive verification of Tea Shop Undo, PDF Upload Handling, and Manual Updates."""
import urllib.request
import json
import os
import re
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test_no_tea_shop_in_codebase():
    print(">>> 1. Checking for 'tea shop' in all relevant files...")
    target_files = [
        "app/extractors/building_plan_extractor.py",
        "app/extractors/tslr_extractor.py",
        "app/samples.py",
        "static/index.html",
        "static/app.js"
    ]
    found_any = False
    for path in target_files:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            # check case insensitive
            matches = re.findall(r'(?:tea\s*shop|டீக்கடை|தேனீர்\s*கடை)', content, re.IGNORECASE)
            if matches:
                print(f"  [FAIL] Found {len(matches)} occurrences in {path}: {matches}")
                found_any = True
            else:
                print(f"  [PASS] {path} is 100% clean of tea shop references.")
    assert not found_any, "Tea shop references found in codebase!"

def test_api_health_and_categories():
    print("\n>>> 2. Testing API health & categories...")
    r = requests.get("http://127.0.0.1:8000/api/health", timeout=5)
    assert r.status_code == 200, f"Health check failed with {r.status_code}"
    print(f"  [PASS] Server is healthy (status {r.status_code})")

    r_cat = requests.get("http://127.0.0.1:8000/api/categories", timeout=5)
    assert r_cat.status_code == 200, f"Categories failed with {r_cat.status_code}"
    cat_data = r_cat.json()
    cats = [c["id"] for c in cat_data.get("categories", [])]
    assert "building_plan" in cats, "building_plan not in categories"
    print(f"  [PASS] Found {len(cats)} categories including 'building_plan'")

def test_building_plan_sample():
    print("\n>>> 3. Testing building_plan sample endpoint...")
    r = requests.get("http://127.0.0.1:8000/api/sample/building_plan", timeout=5)
    assert r.status_code == 200, f"Sample building_plan returned {r.status_code}"
    data = r.json()
    fields = data.get("extracted_data", {}).get("fields", {})
    b_use = fields.get("building_use", {}).get("value", "")
    print(f"  Building Use value: '{b_use}'")
    assert "tea" not in b_use.lower(), "Tea shop found in building_use value!"
    assert "shop_details" not in fields or "tea" not in str(fields.get("shop_details", {})).lower()
    print("  [PASS] building_plan sample is clean and valid.")

def test_pdf_upload_api():
    print("\n>>> 4. Testing real PDF upload to /api/ocr/process...")
    test_pdf = "scratch/test_report_2010.pdf"
    assert os.path.exists(test_pdf), f"Missing test PDF {test_pdf}"

    with open(test_pdf, "rb") as f:
        files = {"file": ("registered_sale_deed.pdf", f, "application/pdf")}
        data = {
            "doc_type": "sale_deed",
            "lang": "ta",
            "use_llm": "false",
            "max_pages": 1
        }
        res = requests.post("http://127.0.0.1:8000/api/ocr/process", files=files, data=data, timeout=60)
        assert res.status_code == 200, f"PDF upload failed with status {res.status_code}: {res.text[:300]}"
        json_resp = res.json()
        assert json_resp.get("total_pages", 0) >= 1, "Expected at least 1 page in OCR result"
        fields = json_resp.get("extraction", {}).get("fields", {})
        print(f"  [PASS] PDF OCR succeeded! Processed {json_resp.get('total_pages')} page(s), extracted {len(fields)} fields.")

def test_frontend_js_functions():
    print("\n>>> 5. Testing frontend JavaScript window exports & dropzone wiring...")
    with open("static/app.js", "r", encoding="utf-8") as f:
        app_js = f.read()

    required_symbols = [
        "window.updateManualField",
        "window.saveCustomFieldFromInput",
        "window.triggerBrowseFile",
        "window.handleFileInputChange",
        "window.triggerProcess",
        "function setupDropzone",
        "function showToastNotification",
        "function renderStandardFieldsLayout"
    ]
    for sym in required_symbols:
        assert sym in app_js, f"Missing symbol {sym} in static/app.js"
        print(f"  [PASS] Found {sym}")

if __name__ == "__main__":
    test_no_tea_shop_in_codebase()
    test_api_health_and_categories()
    test_building_plan_sample()
    test_pdf_upload_api()
    test_frontend_js_functions()
    print("\n=======================================================")
    print("  ALL VERIFICATION CHECKS PASSED PERFECTLY!")
    print("=======================================================")
