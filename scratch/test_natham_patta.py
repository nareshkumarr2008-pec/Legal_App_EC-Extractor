import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from app.extractors.patta_extractor import PattaExtractor

raw_ocr = """தமிழ்நாடு அரசு
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
2. இத் தகவல்கள் 15-09-2026 அன்று 09:22:22 AM நேரத்தில் அச்சச் டிக்கப்பட்டட் து.
3.கை ப்பேசி கேமராவின்2D barcode படிப்பான் மூலம் படித்துத் 3G/GPRS வழி இணையதளத்தில்
சரிபார்க்ர் க்கவும்
மேற்குறிப்பிட்டுட் ள்ள புல எண் /உட்பிரிவு எண் நத்தம் நிலவரித்திட்டத்தின் போது நத்தம் அடங்கலில்
சேர்கப்பட்டுட் ள்ளது ..
"""

ext = PattaExtractor()
clean = ext.clean_text_artifacts(raw_ocr)
print("=== CLEAN TEXT AROUND OWNER ===")
for line in clean.splitlines():
    if any(k in line for k in ["உரிமையாளர்", "குப்புசாமி", "ஜானி", "புல எண்", "ரயத்து"]):
        print(repr(line))

res = ext.extract(raw_ocr)
print("\n=== EXTRACTED FIELDS ===")
for k in ["patta_number", "owner_name", "survey_numbers", "extent_details", "village", "taluk", "district", "nature_of_land", "tax_assessment"]:
    if k in res:
        print(f"{k}: {res[k].get('value')}")

if "cadastral_schedule" in res:
    print("\n=== CADASTRAL SCHEDULE ===")
    print(res["cadastral_schedule"])
