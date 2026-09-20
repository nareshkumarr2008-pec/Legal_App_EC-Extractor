# -*- coding: utf-8 -*-
import sys, re, os
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')
from app.extractors.tslr_extractor import TSLRExtractor

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
"""

ext = TSLRExtractor()
res = ext.extract(tslr_text)
print("Survey No:", res.get("survey_number", {}).get("value"))
print("Owner Name:", res.get("owner_name", {}).get("value"))
