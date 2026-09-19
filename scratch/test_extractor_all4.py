import sys
import os
import time

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

t0 = time.time()
for name, path, fn in deeds:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    print(f"\n=======================================================")
    print(f"TESTING: {name} ({fn})")
    print(f"=======================================================")
    t_start = time.time()
    res = extractor.extract(text, filename=fn)
    dur = (time.time() - t_start) * 1000

    print(f"1. Reg Date:       {res.get('registration_date', {}).get('value')}")
    print(f"2. Vendor:         {res.get('vendor_details', {}).get('value')[:90]}...")
    print(f"3. Purchaser:      {res.get('purchaser_details', {}).get('value')[:90]}...")
    if 'poa_agent_details' in res:
        print(f"   POA Agent:      {res.get('poa_agent_details', {}).get('value')}")
    print(f"4. Prev Owner:     {res.get('history_previous_owner', {}).get('value')}")
    print(f"5. Mother Deed:    {res.get('previous_doc_reference', {}).get('value')}")
    print(f"6. Survey No:      {res.get('survey_number', {}).get('value')}")
    print(f"7. Sched Type:     {res.get('schedule_property_type', {}).get('value')}")
    print(f"8. Extent:         {res.get('land_extent', {}).get('value')}")
    print(f"9. UDS / Built:    {res.get('apartment_uds_floor', {}).get('value')}")
    print(f"10. Boundaries:    {res.get('boundaries', {}).get('value')}")
    print(f"11. SRO Details:   {res.get('sro_details', {}).get('value')}")
    print(f"12. Doc Number:    {res.get('document_number', {}).get('value')}")
    
    # Assertions for user requirements
    assert 'pan_number' not in res, "Error: pan_number must not be present"
    assert 'masked_aadhaar' not in res, "Error: masked_aadhaar must not be present"
    assert 'consideration_amount' not in res, "Error: consideration_amount must not be present"
    assert 'market_value' not in res, "Error: market_value must not be present"
    assert 'payment_breakdown' not in res, "Error: payment_breakdown must not be present"
    assert 'witnesses' not in res, "Error: witnesses must not be present"
    assert 'document_drafter' not in res, "Error: document_drafter must not be present"
    
    checklist = res.get('checklist', [])
    passed = sum(1 for c in checklist if c.get('is_valid'))
    total = len(checklist)
    print(f"Checklist Score:   {passed}/{total} Passed")
    print(f"Extraction Time:   {dur:.1f} ms")

total_dur = (time.time() - t0) * 1000
print(f"\nAll 4 deeds verified successfully in {total_dur:.1f} ms total!")
