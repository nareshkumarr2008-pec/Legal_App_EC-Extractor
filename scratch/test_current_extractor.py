import sys, re
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding='utf-8')

from app.extractors.sale_deed_extractor import SaleDeedExtractor

extractor = SaleDeedExtractor()
deeds = [
    ("1995 DEED", "scratch/ocr_text_1995.txt", "Sale deed_6027_1995.pdf"),
    ("2004 DEED", "scratch/ocr_text_2004.txt", "Sale deed_188_2004.pdf"),
    ("2010 DEED", "scratch/ocr_text_2010.txt", "Sale Deed_3978_2010 - Naagesh.pdf"),
]

for title, path, fn in deeds:
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    res = extractor.extract(raw, filename=fn)
    fields = res.get("fields", {})
    checklist = res.get("checklist", [])
    
    print(f"\n{'='*60}\n{title} ({fn})\n{'='*60}")
    print("Vendor:", fields.get("vendor_details", {}).get("value", "")[:100])
    print("Purchaser:", fields.get("purchaser_details", {}).get("value", "")[:100])
    print("POA Agent:", fields.get("poa_agent_details", {}).get("value", "None")[:100])
    print("Prev Doc:", fields.get("previous_doc_reference", {}).get("value", "")[:100])
    print("Prev Owner:", fields.get("history_previous_owner", {}).get("value", "")[:100])
    print("Survey:", fields.get("survey_number", {}).get("value"))
    print("VTD:", fields.get("village_taluk_district", {}).get("value", "")[:100])
    print("Land Extent:", fields.get("land_extent", {}).get("value"))
    print("UDS & Flat:", fields.get("apartment_uds_floor", {}).get("value"))
    print("Consideration:", fields.get("consideration_amount", {}).get("value"))
    print("Market Value:", fields.get("market_value", {}).get("value"))
    print("Payment:", fields.get("payment_breakdown", {}).get("value", "")[:120])
    print("SRO:", fields.get("sro_details", {}).get("value"))
    print("Doc No:", fields.get("document_number", {}).get("value"))
    print("Reg Date:", fields.get("registration_date", {}).get("value"))
    print("Witnesses:", fields.get("witnesses", {}).get("value"))
    
    passed = sum(1 for c in checklist if c.get("is_valid"))
    print(f"\nCHECKLIST PASSED: {passed}/{len(checklist)}")
    for i, c in enumerate(checklist):
        if not c.get("is_valid"):
            print(f"  FAILED ITEM {i+1}: {c.get('title')} - {c.get('details')}")
