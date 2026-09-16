import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from app.extractors.sale_deed_extractor import SaleDeedExtractor
from app.extractor import DocumentExtractor

with open("scratch/ocr_text_1995.txt", "r", encoding="utf-8") as f:
    text_1995 = f.read()

with open("scratch/ocr_text_2010.txt", "r", encoding="utf-8") as f:
    text_2010 = f.read()

extractor = SaleDeedExtractor()
doc_extractor = DocumentExtractor()

print("==================================================================")
print("TESTING SALE DEED 1995 (Undivided Share of Land / Vacant Site)")
print("==================================================================")
res_1995 = extractor.extract(text_1995, filename="Sale deed_6027_1995.pdf")

for k, v in res_1995.items():
    if k == "checklist":
        continue
    val = v.get("value") if isinstance(v, dict) else v
    conf = v.get("confidence", 0) if isinstance(v, dict) else 1.0
    print(f"[{k}] (conf: {conf}): {val}")

checklist_1995 = res_1995.get("checklist", [])
print(f"\n--- 1995 CHECKLIST ({len(checklist_1995)} items) ---")
pass_count_1995 = 0
for idx, item in enumerate(checklist_1995):
    passed = item.get("is_valid")
    if passed: pass_count_1995 += 1
    status = "PASSED" if passed else "FLAGGED"
    print(f"{idx+1}. [{status}] {item.get('title')}: {item.get('details')}")

print(f"\n1995 Total Passed: {pass_count_1995}/{len(checklist_1995)}")

print("\n==================================================================")
print("TESTING SALE DEED 2010 (Apartment Flat with UDS)")
print("==================================================================")
res_2010 = extractor.extract(text_2010, filename="Sale Deed_3978_2010 - Naagesh.pdf")

for k, v in res_2010.items():
    if k == "checklist":
        continue
    val = v.get("value") if isinstance(v, dict) else v
    conf = v.get("confidence", 0) if isinstance(v, dict) else 1.0
    print(f"[{k}] (conf: {conf}): {val}")

checklist_2010 = res_2010.get("checklist", [])
print(f"\n--- 2010 CHECKLIST ({len(checklist_2010)} items) ---")
pass_count_2010 = 0
for idx, item in enumerate(checklist_2010):
    passed = item.get("is_valid")
    if passed: pass_count_2010 += 1
    status = "PASSED" if passed else "FLAGGED"
    print(f"{idx+1}. [{status}] {item.get('title')}: {item.get('details')}")

print(f"\n2010 Total Passed: {pass_count_2010}/{len(checklist_2010)}")

print("\n==================================================================")
print("TESTING FULL DOCUMENTEXTRACTOR (Bilingual & Integration Check)")
print("==================================================================")
full_res_1995 = doc_extractor.extract(text_1995, doc_type="sale_deed", filename="Sale deed_6027_1995.pdf")
print("DocumentExtractor extract success on 1995 deed! Field count:", len(full_res_1995.get("fields", {})))
full_res_2010 = doc_extractor.extract(text_2010, doc_type="sale_deed", filename="Sale Deed_3978_2010 - Naagesh.pdf")
print("DocumentExtractor extract success on 2010 deed! Field count:", len(full_res_2010.get("fields", {})))
