import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))
from app.extractors.sale_deed_extractor import SaleDeedExtractor

extractor = SaleDeedExtractor()

deeds = [
    ('1995 Deed', 'scratch/ocr_text_1995.txt', 'Sale deed_6027_1995.pdf'),
    ('2004 Deed', 'scratch/ocr_text_2004.txt', 'Sale deed_188_2004.pdf'),
    ('2010 Naagesh Deed', 'scratch/ocr_text_2010.txt', 'Sale Deed_3978_2010 - Naagesh.pdf'),
    ('2010 Shailaja Deed', 'scratch/ocr_text_8916_2010.txt', 'media_1789577779097.pdf')
]

for name, path, fn in deeds:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    print(f"\n=======================================================")
    print(f"TESTING: {name} ({fn})")
    print(f"=======================================================")
    res = extractor.extract(text, filename=fn)
    
    print(f"1. Reg Date:       {res.get('registration_date', {}).get('value')}")
    print(f"2. Vendor:         {res.get('vendor_details', {}).get('value')[:85]}...")
    print(f"3. Purchaser:      {res.get('purchaser_details', {}).get('value')[:85]}...")
    if 'poa_agent_details' in res:
        print(f"   POA Agent:      {res.get('poa_agent_details', {}).get('value')[:85]}...")
    print(f"4. Prev Owner:     {res.get('history_previous_owner', {}).get('value')}")
    print(f"5. Prev Doc Ref:   {res.get('previous_doc_reference', {}).get('value')}")
    print(f"6. Survey No:      {res.get('survey_number', {}).get('value')}")
    print(f"7. Sched Type:     {res.get('schedule_property_type', {}).get('value')}")
    print(f"8. Classification: {res.get('land_classification', {}).get('value')}")
    print(f"9. Extent:         {res.get('land_extent', {}).get('value')}")
    print(f"10. UDS / Built:   {res.get('apartment_uds_floor', {}).get('value')}")
    print(f"11. Boundaries:    {res.get('boundaries', {}).get('value')}")
    print(f"12. Consideratn:   {res.get('consideration_amount', {}).get('value')}")
    print(f"13. Market Val:    {res.get('market_value', {}).get('value')}")
    print(f"14. SRO Details:   {res.get('sro_details', {}).get('value')}")
    print(f"15. Doc Number:    {res.get('document_number', {}).get('value')}")
    print(f"16. Witnesses:     {res.get('witnesses', {}).get('value')}")
    
    checklist = res.get('checklist', [])
    passed = sum(1 for c in checklist if c.get('is_valid'))
    total = len(checklist)
    print(f"Checklist Score:   {passed}/{total} Passed")
    for c in checklist:
        if not c.get('is_valid'):
            print(f"  [FLAGGED] {c.get('title')}: {c.get('details')}")
