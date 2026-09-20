import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from app.extractors.patta_extractor import PattaExtractor

extractor = PattaExtractor()

# Test 1: User's Natham Patta (Doc 324)
user_natham_text = """தமிழ்நாடு அரசு
வருவாய் மற்றும் பேரிடர் மேலாண்மைத் துறை
நத்தம் பட்டா
மாவட்டம் : செங்கல்பட்டுட் வட்டம் : தாம்பரம்
வருவாய் கிராமம் : செம்பாக்கம் பட்டா எண் : 324
உரிமையாளர்கள் பெயர்
1. குப்புசாமி மகன் ஜானிகிராமன் -
நத்தம் புல எண் உட்பிட் ரிவு எண் பழைய புல எண் வகை ப்பாடு பரப்பு தீர்வைர் குறிப்பு
ஹெக் - ஏர் - சமீ ரூ - பை
128 11 128--
ரயத்துத் வாரி
மனை
0 - 0.51 2.00
---- --G.O. MS 221
dated 04.05.2023-
--
Digitally signed:
Kavitha S
Tahsildar
22/01/2024
05:47:27:PM
0 - 0.51 2.00
தாம்பரம் வட்டாட்சியர் / மண்டல துணை வட்டாட்சியரால் 22/01/2024 அன்று 05:47:27:PM நேரத்தில் மின்
கை யொப்பம் இடப்பட்டது.
குறிப்பு :
1.
மேற்கண்ட நத்தம் நில உரிமை விபரங்கள் நத்தம் தூய அடங்கலின் உண்மை நகல் என
சான்றளிக்கப்படுகிறது. இவற்றை தாங்கள் https://eservices.tn.gov.in என்ற இணைய
தளத்தில் S/NA/35/05/128/00324/30899 என்ற குறிப்பு எண்ணை உள்ளீடுளீ செய்து உறுதி
செய்துகொள்ளவும்.
"""

print("=== TEST 1: USER NATHAM PATTA (DOC 324) ===")
res1 = extractor.extract(user_natham_text)
f1 = res1.get("fields", res1)
print("Patta No:", f1["patta_number"]["value"])
print("Owner:", f1["owner_name"]["value"])
print("District:", f1["district"]["value"])
print("Taluk:", f1["taluk"]["value"])
print("Village:", f1["village"]["value"])
print("Survey Numbers:", f1["survey_numbers"]["value"])
print("Extent Summary:", f1["extent_details"].get("summary_ares_sqft"))
print("Extent Details:\n", f1["extent_details"]["value"])
print("Nature of Land:", f1["nature_of_land"]["value"])
print("Total Tax:", f1["total_tax"]["value"])
print("Portal Ref:", f1["portal_reference"]["value"])
print("Cadastral Schedule:", f1.get("cadastral_schedule"))

# Test 2: User's PDF text extracted with pdfplumber containing null bytes & dropped glyphs
user_pdfplumber_text = """வ\x00வாய் \x00ராமம் : ெசம்பாக்கம் பட்டா எண் : 324
உரிைமயாளரக் ள் ெபயர்
1. \x00ப்\x00சா\x00 மகன் ஜானி\x00ராமன் -
நத்தம்  ல எண் உட ் ரி  எண் பைழய  ல எண் வைகப்பா  பரப்   ரை் வ   ப் 
ெஹக் - ஏர ்- ச    - ைப
---- --G.O. MS 221
dated 04.05.2023-
--
ரயத ் வாரி Digitally signed:
128 11 128-- 0 - 0.51 2.00
மைன Kavitha S
Tahsildar
22/01/2024
05:47:27:PM
0 - 0.51 2.00
தாம்பரம் வட்டாட் யர ்/ மண் டல  ைண வட்டாட் யரால் 22/01/2024 அன்  05:47:27:PM ேநரத் ல்  ன்
ைகெயாப்பம் இடப்பட்ட .
  ப்  :
ேமற்கண் ட நத்தம் நில உரிைம  பரங்கள் நத்தம்  ய அடங்க ன் உண்ைம நகல் என
1.சான்றளிக்கப்ப  ற . இவற்ைற தாங்கள் https://eservices.tn.gov.in என்ற இைணய
தளத் ல் S/NA/35/05/128/00324/30899 என்ற   ப்  எண்ைண உள்ள ீ ெசய்  உ  
ெசய் ெகாள்ள ம்.
"""

print("\n=== TEST 2: USER PDFPLUMBER TEXT WITH GLYPH DROPS ===")
res2 = extractor.extract(user_pdfplumber_text)
f2 = res2.get("fields", res2)
print("Patta No:", f2["patta_number"]["value"])
print("Owner:", f2["owner_name"]["value"])
print("District:", f2["district"]["value"])
print("Taluk:", f2["taluk"]["value"])
print("Village:", f2["village"]["value"])
print("Survey Numbers:", f2["survey_numbers"]["value"])
print("Extent Summary:", f2["extent_details"].get("summary_ares_sqft"))
print("Nature of Land:", f2["nature_of_land"]["value"])
print("Total Tax:", f2["total_tax"]["value"])

# Test 3: Rural Form 10(1) Patta (Doc 1092)
rural_form10_text = """தமிழ்நாடு அரசு - வருவாய்த்துறை
நில உரிமை விபரங்கள் : 10(1) பிரிவு சான்று
PATTA EXTRACT - TAMIL NADU REVENUE DEPARTMENT

பட்டா எண்: 1092
உரிமையாளர்கள் பெயர்:
1. பக்கிரிசாமி மகன் கோவிந்தராசு
2. ஜெயலட்சுமி மனைவி பக்கிரிசாமி

மாவட்டம்: திருவாரூர்
வட்டம்: நன்னிலம்
வருவாய் கிராமம்: தூத்துக்குடி

புல எண் | உட்பிரிவு | நஞ்சை பரப்பு (ஹெக் - ஏர்)
30 | 3B | 0.28.50
30 | 5B | 0.11.50
மொத்தம் | 0.40.00
"""

print("\n=== TEST 3: RURAL FORM 10(1) PATTA (DOC 1092) ===")
res3 = extractor.extract(rural_form10_text)
f3 = res3.get("fields", res3)
print("Patta No:", f3["patta_number"]["value"])
print("Owner:\n", f3["owner_name"]["value"])
print("District:", f3["district"]["value"])
print("Taluk:", f3["taluk"]["value"])
print("Village:", f3["village"]["value"])
print("Survey Numbers:", f3["survey_numbers"]["value"])
print("Extent Details:\n", f3["extent_details"]["value"])
print("Nature of Land:", f3["nature_of_land"]["value"])
print("Total Tax:", f3["total_tax"]["value"])
