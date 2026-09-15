# -*- coding: utf-8 -*-
"""Test EC Extraction on Document 1 OCR text"""
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')
from app.extractors.ec_extractor import ECExtractor

DOC1_TEXT = """தமிழ்நாடு அரசு
பதிவுத்துறை
சொத்து தொடர்பான வில்லங்கச் சான்று
சா.ப.அ: தியாகராய நகர் சான்று எண்: EC/Online/162081396/2025 மனு எண்: ECA/Online/162081396/2025 நாள்: 12-Sep-2025
திரு/திருமதி/செல்வி. RAMS REAL ESTATES LIMITED Tamil Nadu, India கீழ்க்கண்ட சொத்து தொடர்பாக ஏதேனும் வில்லங்கம் இருப்பின் அதன் பொருட்டு
வில்லங்கச் சான்று கோரி விண்ணப்பித்துள்ளார்.
கிராமம் சர்வே விவரம்
தியாகராய நகர் 6107/1B, 6110/1B, 6110/2, 6107/4, 7797/2
மனு சொத்து விவரம்: மொத்த விஸ்தீர்ணம்: 5720 Sq.ft, உரிமை மாற்றப்பட்ட விஸ்தீர்ணம்: 5720 Sq.ft, பழைய கதவு எண்: 9, பிளாக் எண்: 136, மனை எண் : ,
எல்லை விபரங்கள்: தெற்கு பகுதி- Hensman Road and, வடக்கு பகுதி- Building and Premises comprised in Door No. 9-A of Dhandapani Road belonging to V. Naidu,, கிழக்கு பகுதி-
The Building and Premises of Velanganni Hostel bearing Door No.44, Hensman Road, மேற்கு பகுதி- Door No.42, Hensman Road belonging to T.Krishnaswamy Pillai
1 புத்தகம் மற்றும் அதன் தொடர்புடைய அட்டவணைகள் 1 ஆண்டுகளுக்கு 22-May-2025 முதல் 09-Sep-2025 வரை இச்சொத்தைப் பொறுத்து பதிவு
செய்திட்ட நடவடிக்கைகள் மற்றும் வில்லங்கங்கள் குறித்து தேடுதல் மேற்கொள்ளப்பட்டது.
வ.
எண்
ஆவண எண் மற்றும்
ஆண்டு
எழுதிக் கொடுத்த
நாள் & தாக்கல்
நாள் & பதிவு
நாள்
தன்மை எழுதிக் கொடுத்தவர்(கள்) எழுதி வாங்கியவர்(கள்)
தொகுதி எண்
மற்றும் பக்க எண்
1754/2025
18-Jun-2025 
18-Jun-2025
18-Jun-2025
இரசீது ஆவணம்
1. ஐ.சி.ஐ.சி.ஐ வங்கி
லிமிடெட்(முத.)
ஏ ஏ வி பார்ட்னெர்ஸால்
நியமிக்கப்பட்ட பிரதிநிதி
விக்னேஷ்()
1.ஷெரின் வேளாங்கன்னி
சீனியர் செகண்டரி ஸ்கூல்
-
கைமாற்றுத் தொகை: 
ரூ. 3,63,99,590/-
சந்தை மதிப்பு:
-
முந்தைய ஆவண எண்: 
1856/2020
அட்டவணை A விவரங்கள்: 
சொத்தின் வகைப்பாடு: மனையும் கட்டிடமும்
கிராமம் மற்றும் தெரு: தியாகராய நகர், KANNADASAN STREET /
KANNADASAN ROAD
புல எண்-விஸ்தீர்ணம்: 6107/1B, 6110/1B - 5720.0 சதுரடி
புதிய கதவு எண்: 43
பழைய கதவு எண்: 9
எல்லை விபரங்கள்: 
1
சொத்து தொடர்பான குறிப்புரை: விஸ்: 5720 ச அடி வீடுவீ மனை.
1 / 3

கிழக்கு - ஹன்ஸ்மென் ரோடு க எண் 44 வேளாங்கண்ணி
ஹாஸ்டல்,மேற்கு - ஹன்ஸ்மென் ரோடு க எண் 42 , கிருஷ்ணசாமி
பிள்ளை சொத்து,வடக்கு - தண்டபாணி ரோடு க எண் 9ஏ நாயுடு
வீடுவீ ,தெற்கு - மேற்படி ரோடு
2200/2025
24-Jul-2025 
24-Jul-2025
24-Jul-2025
விற்பனை ஆவணம்/
கிரைய ஆவணம்
1. ஷ்ரைன் வேளாங்கன்னி
சீனியர் செகண்டரி
ஸ்கூல்(முத.)
ஷ்ரைன் வேளாங்கன்னி
சீனியர் செகண்டரி ஸ்கூல்
காக திருமதி. பகலாகுமாரி
குமாரசாமி பிள்ளை
என்கின்ற பி. கே. கே.
பிள்ளை(முக.)
ஷ்ரைன் வேளாங்கன்னி
சீனியர் செகண்டரி ஸ்கூல்
காக திரு. கே. டி. பிள்ளை
என்கின்ற தங்க செல்லப்பா
பிள்ளை(முக.)
1.மெஸர்ஸ். ராம்ஸ்
கன்ஸ்டிரக்ஷன்
எல்எல்பி(முத.)
மெஸர்ஸ். ராம்ஸ்
கன்ஸ்டிரக்ஷன் எல்எல்பி
க்காக மெஸர்ஸ். ராம்ஸ்
ரியல் எஸ்டேட்ஸ் லிமிடெட்
காக திரு. வெங்கடராம்
ரவிகிருஷ்ணன்(முக.)
-
கைமாற்றுத் தொகை: 
ரூ. 11,00,00,000/-
சந்தை மதிப்பு:
ரூ. 11,00,00,000/-
முந்தைய ஆவண எண்: 
1399/1987
அட்டவணை A விவரங்கள்: 
சொத்தின் வகைப்பாடு: மனையும் கட்டிடமும்
கிராமம் மற்றும் தெரு: தியாகராய நகர், KANNADASAN STREET /
KANNADASAN ROAD
புல எண்-விஸ்தீர்ணம்: 143, 143/8, 143/9, 6107/1B, 6107/4, 6110/1B, 6110/2,
7797/2 - 5720.0 சதுரடி
புதிய கதவு எண்: 20
பழைய கதவு எண்: 9 then 43
தள எண்: G,1,2 
2
எல்லை விபரங்கள்: 
கிழக்கு - ஹென்ஸ்மேன் ரோடு தற்போது கண்ணதாசன் தெருவில்
உள்ள சொத்தின் கதவு எண்.44, புதிய எண்.18, புதிய டி. எஸ்.
எண்கள்.6107/2, 6110/1 & 7797/1-ல் உள்ளது.,மேற்கு - ஹென்ஸ்மேன் ரோடு
தற்போது கண்ணதாசன் தெரு, கதவு எண்.42 புதிய டி. எஸ். எண்.6107/3&
6109& 7796,வடக்கு - திரு. வி. நாயுடுவிற்கு சொந்தமான சொத்து,
தண்டபாணி தெரு, கதவு எண்.9-எ, புதிய டி. எஸ். எண்.6107/1-ல்
உள்ளது.,தெற்கு - ஹென்ஸ்மேன் ரோடு, தற்போது கண்ணதாசன் தெரு
2 / 3 

பதிவுகளின் எண்ணிக்கை : 2
"""

extractor = ECExtractor()
res = extractor.extract(DOC1_TEXT)

print("=== SRO & HEADER ===")
print("SRO:", res.get("sro_office", {}).get("value"))
print("Village:", res.get("village", {}).get("value"))
print("Survey Searched:", res.get("survey_searched", {}).get("value"))
print("Search Period:", res.get("search_period", {}).get("value"))
print("Search Period Standard:", res.get("search_period_standard", {}).get("value"))
print("Total Entries:", res.get("total_entries", {}).get("value"))

print("\n=== CURRENT OWNER ===")
print("Owner Name:", res.get("current_owner", {}).get("name"))
print("Owner Type:", res.get("current_owner", {}).get("type"))
print("Doc No:", res.get("current_owner", {}).get("doc_no"))
print("Date:", res.get("current_owner", {}).get("date"))
print("Property Owners list count:", len(res.get("current_owner", {}).get("property_owners", [])))
for po in res.get("current_owner", {}).get("property_owners", []):
    print("  Unit:", po.get("unit"), "| Owner:", po.get("owner_name"), "| Doc:", po.get("doc_no"))

print("\n=== ENTRIES ===")
txs = res.get("transactions_table", {}).get("value", [])
print(f"Parsed {len(txs)} transactions:")
for t in txs:
    print(f"Sr: {t.get('sr')} | Doc: {t.get('doc_no')} | Nature: {t.get('nature')} | Exec: {t.get('executants')} | Claim: {t.get('claimants')}")
    print(f"   Schedules ({len(t.get('schedules', []))}):")
    for s in t.get('schedules', []):
        print(f"     {s}")
