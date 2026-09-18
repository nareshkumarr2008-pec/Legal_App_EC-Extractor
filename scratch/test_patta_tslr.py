# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath("."))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import json
from app.extractors.patta_extractor import PattaExtractor
from app.extractors.tslr_extractor import TSLRExtractor

patta_text = """தநா அர	
வ வா\x0c ம ேப ட ேமலா ைம ைற
 ல உ ைம பர க! : இ.எ 10(1) % &
மாவ'ட : (௫வா* வ'ட : ந+,ல 
வ வா\x0c -ராம : . /01 ப'டா எ : 1092
உ ைமயாள க! ெபய 
1 ேகா 5தரா	 மக+ ப/- சா
வ.எ 
7ல எ 8 
உ'% & 
ந+ெச\x0c 7+ெச\x0c ம றைவ
பர:7 ; ைவ பர:7 ; ைவ பர:7 ; ைவ 09:7
ெஹ. ஏ * ைப ெஹஏ * ைப ெஹ. ஏ * ைப
1 30 - 3B 0 28.50 06 69
2024/0103/20/179137
08-02-2024
2 30 - 5B 0 11.50 02 70
2024/0103/20/179137
08-02-2024
ெமா த - 0 40.00 9 39 0 0 0 0
+ைகெய:ப / Digital Signature : 08-02-2024 அ+ 03:35:26 PM ேநர (> இட:ப'ட 
ெபய /Name : KUPPUSAMY V
பத / Designation: Zonal Deputy Tahsildar
இட /Place : ந+,ல (02) வ'ட ,
(௫வா* (20) மாவ'ட 
09:7
1
ேம க ட தகவ> / சா+9த நக> வர க! + ப(ேவ'1? 5 ெபற:ப'டைவ.இவ ைற
தா க! https://eservices.tn.gov.in எ+ற இைணய தள (> 2024/0103/20/179137 எ+ற 09:7
எ ைண உ!A ெச\x0c உ ( ெச\x0c ெகா!ள& .
2 இ தகவ>க! 17-08-2026 அ+ 12:01:01 PM ேநர (> அBச1/க:ப'ட .
3
ைக:ேபC ேகமரா + 2D barcode ப1:பா+ Dல இ தகவ>கைள இைணய தள (>
ச பா /க& ."""

tslr_text = """Certified that the above is a true extract from the Town Survey Land Register maintained in the Taluk. மின் கை யொப்பம் / Digital Signature : 31-08-2025
பெயர் / Name : Charles P ர்
பதவி / Designation : Zonal Deputy Tahsildar
இடம் / Place : தாம்பரம் வட்டட் ம் / Tambaram, செங்கல்பட்டுட் மாவட்டட் ம் / Chengalpattu
CERTIFICATE
EXTRACT FROM THE TOWN SURVEY LAND REGISTER
District : Chengalpattu Taluk : Tambaram Town : Tambaram Ward : ward-I selaiyur
S.No
Block
Code
and
Name
Of
Locality
Number
O.Sur No
and
Letter
Municipal
Door No.
Govt,Mitta,
Zamindari,Inam
Dry,Wet,
Unassessed,
Promboke,
House-site
Source
Of
Irrigation
and
Class
If Double
Crop,Rate
of
Composition
Class
and
Sort
of
soil
Taram
Rate per
Acre/Hectare
Extent By Town
Survey
Assesment
Municipal
Register
Adangal (UDS
Details)
How
the
holding
is
utilised
Remarks
Sur.
Field
Sub
Div.
Rs. Paise Hectare Ares
Sq.
Meter Municipal Govt.
1
Block :
Block-27-..
73 0
380/1A1C
23 -
23 ரயத்துத் வாரி புஞ்சை - 0- 0.00 0 2 64.0 - 0.00 -
நாராயணன்
மகன் நா
கோவிந்தராஜூ
2025/0153/35/005324TR
DT. 2025-08-31 TR DT:
31-08-2025
குறிப்பு / Remarks :
1. மேற்கண்ட தகவல் / சான்றிதழ் நகல் விவரங்கள் மின் பதிவேட்டிட் லிருந்து பெறப்பட்டட் வை. இவற்றை தாங்கள் https://eservices.tn.gov.in என்ற இணைய
தளத்தில் URB/35/05/003/009/0027/73/0 என்ற குறிப்பு எண்ணை உள்ளீடுளீ செய்து உறுதி செய்துகொள்ளவும்.
The above information / certificate details are generated from Digital records. This can be verified at the eServices portal https://eservices.tn.gov.in by giving the
reference number URB/35/05/003/009/0027/73/0
2. இத் தகவல்கள் 16-09-2026 அன்று 08:00:45 AM நேரத்தில் அச்சச் டிக்கப்பட்டட் து.
The certificate was printed on 16-09-2026 at 08:00:45 AM
3. கை ப்பேசி கேமராவின்2D barcode படிப்பான் மூலம் படித்துத் 3G/GPRS வழி இணையதளத்தில் சரிபார்க்ர் க்கவும்
Scan with 2D Barcode reader of mobile phone camera and check on website using 3G/GPRS."""

print("=== TESTING PATTA EXTRACTOR ===")
p_ext = PattaExtractor()
p_res = p_ext.extract(patta_text)
for k, v in p_res.items():
    print(f"[{k}]: {v.get('value')}")

print("\n=== TESTING TSLR EXTRACTOR ===")
t_ext = TSLRExtractor()
t_res = t_ext.extract(tslr_text)
for k, v in t_res.items():
    print(f"[{k}]: {v.get('value')}")
