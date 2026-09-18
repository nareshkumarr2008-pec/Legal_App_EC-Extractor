# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath("."))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from app.extractor import DocumentExtractor
from scratch.test_patta_tslr import patta_text, tslr_text

extractor = DocumentExtractor()

print("==================================================")
print("TEST 1: FULL STACK EXTRACTION FOR PATTA")
print("==================================================")
patta_result = extractor.extract(patta_text, doc_type="auto")
print("Detected doc_type:", patta_result.get("document_type_id"))
print("Document Type Name:", patta_result.get("document_type"))
print("Key Fields Extracted:")
for k, v in patta_result.get("fields", {}).items():
    if isinstance(v, dict):
        print(f"  {k}: {v.get('value')} (conf: {v.get('confidence')})")
    elif k == "schedule":
        print(f"  schedule count: {len(v)} items")
print("\nChecklist Results:")
for chk in patta_result.get("checklist", []):
    t = chk.get("title") or chk.get("rule_name") or chk.get("item")
    d = chk.get("detail") or chk.get("details") or chk.get("remarks")
    print(f"  [{chk.get('status')}]: {t} -> {d}")

print("\n==================================================")
print("TEST 2: FULL STACK EXTRACTION FOR TSLR")
print("==================================================")
tslr_result = extractor.extract(tslr_text, doc_type="auto")
print("Detected doc_type:", tslr_result.get("document_type_id"))
print("Document Type Name:", tslr_result.get("document_type"))
print("Key Fields Extracted:")
for k, v in tslr_result.get("fields", {}).items():
    if isinstance(v, dict):
        print(f"  {k}: {v.get('value')} (conf: {v.get('confidence')})")
print("\nChecklist Results:")
for chk in tslr_result.get("checklist", []):
    t = chk.get("title") or chk.get("rule_name") or chk.get("item")
    d = chk.get("detail") or chk.get("details") or chk.get("remarks")
    print(f"  [{chk.get('status')}]: {t} -> {d}")

print("\nALL FULL-STACK EXTRACTION TESTS COMPLETED!")
