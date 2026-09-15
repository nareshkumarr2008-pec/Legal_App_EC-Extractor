# -*- coding: utf-8 -*-
"""Test unified parser prototype on Document 1, 2, and 3"""
import sys
import os
import re
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.stdout.reconfigure(encoding='utf-8')

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

DOC3_TEXT = """தமிழ்நாடு அரசு
பதிவுத்துறை
சொத்து தொடர்பான வில்லங்கச் சான்று
சா.ப.அ: தியாகராய நகர் சான்று எண்: EC/Online/151861598/2025 மனு எண்: ECA/Online/151861598/2025 நாள்: 27-May-2025
திரு/திருமதி/செல்வி. RAMS REAL ESTATES LIMITED Tamil Nadu, India கீழ்க்கண்ட சொத்து தொடர்பாக ஏதேனும் வில்லங்கம் இருப்பின் அதன் பொருட்டு
வில்லங்கச் சான்று கோரி விண்ணப்பித்துள்ளார்.
கிராமம் சர்வே விவரம்
தியாகராய நகர் 6107/1B, 6110/1B, 6110/2, 6107/4, 7797/2
மனு சொத்து விவரம்: உரிமை மாற்றப்பட்ட விஸ்தீர்ணம்: 5720 Sq.ft, பழைய கதவு எண்: 9, பிளாக் எண்: 136, மனை எண் : , எல்லை விபரங்கள்: தெற்கு பகுதி-
Hensman Road, வடக்கு பகுதி- Building and Premises comprised n Door No. 9-A of Dhandapani Road belaonging to V. Naidu, கிழக்கு பகுதி- The Building and Premises of Velanganni Hostel
bearing Door No.44, Hensman Road, மேற்கு பகுதி- Door No.42, Hensman Road belonging to T.Krishnaswamy Pillai
1 புத்தகம் மற்றும் அதன் தொடர்புடைய அட்டவணைகள் 51 ஆண்டுகளுக்கு 01-Jan-1975 முதல் 21-May-2025 வரை இச்சொத்தைப் பொறுத்து பதிவு
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
329/1985
14-Dec-1984 
14-Dec-1984
19-Mar-1985
உரிமை மாற்றம்
1. V. ஷண்முகம் 2
2. V. சந்திரன் 1
1... மோகன சுந்தரம் 1 -
கைமாற்றுத் தொகை: 
ரூ. 2,00,00/
சந்தை மதிப்பு:
ரூ. 2,40,000/-
முந்தைய ஆவண எண்: 
1286/1932, 413/1933
அட்டவணை A விவரங்கள்: 
சொத்தின் வகைப்பாடு: வீட்டுவீ மனை
சொத்தின் விஸ்தீர்ணம்: 5720 SQ.FT.
கிராமம் மற்றும் தெரு: தியாகராய நகர், அனுமந்தராவ் தெரு புல எண் : 143, 143/8, 143/9, 6107/1B, 6110/1B
புதிய கதவு எண்: 43
பழைய கதவு எண்: 9
மனை எண் : 0 
எல்லை விபரங்கள்: 
(கி) வேளாங்கன்னி ஹாஸ்டல் & டோர் நெ 44 ண ரோடு,(தெ) ண
ரோடு,(வ) தண்டபாணி தெருவில் V நாயுடு சொந்தமான வீடுவீ நெ 9A,
1
சொத்து தொடர்பான குறிப்புரை: விஸ்தீரணம் 5720 சதுரடி s no 143pt குறிப்பு:(
ஹன்ஸ்மேன் ரோடு என்பது ஹனுமன்த் ராவ் ரோடு என உள்ளீடுள்ளீ
செய்யப்படுகிறது)
1 / 6 

1399/1987
06-Oct-1987 
06-Oct-1987
07-Oct-1987
விற்பனை ஆவணம்/
கிரைய ஆவணம்
1. S. மோகன சந்தானம்(
Principal)
2. R. வைத்திய நாதன் Agent
1.ஷெரின் வேளாங்கன்னி
சீனியர் செகண்டரி ஸ்கூல்
1111, 387
கைமாற்றுத் தொகை: 
ரூ. 7,75,000/-
சந்தை மதிப்பு:
-
முந்தைய ஆவண எண்: 
-
ஆவணக் குறிப்புகள் : .
அட்டவணை A விவரங்கள்: 
சொத்தின் வகைப்பாடு: வீட்டுவீ மனை
புல எண் : 6107/1B, 6110/1B
புதிய கதவு எண்: 43
பழைய கதவு எண்: 9
பிளாக் எண்: 136
சொத்து தொடர்பான குறிப்புரை: விஸ்: 5720 ச அடி வீடுவீ மனை.

547/1997
04-Apr-1997
04-Apr-1997
09-Apr-1997
ஈடு / அடைமானம்
1. சென்னை சிரையில் வேளாங்கன்னி சினியர் செகஸ்டரி ஸகூல்(Shaivne Vikkha senior School)
1. சென்னை மெசர்ஸ் லஷ்மி ஜெனரல் பைனான்ஸ் லிட்
1432, 45
கைமாற்றுத் தொகை: 
ரூ. 1,00,000/-
சந்தை மதிப்பு:
ரூ. 9,999/-
முந்தைய ஆவண எண்: 
-
ஆவணக் குறிப்புகள் : வட்டி 27.50% P.A. கெடு 60மாத தவணைகள்ல் செலுத்தவாய். (ஹென்ஸ் மேன் ரோடு) .
அட்டவணை A விவரங்கள்: 
சொத்தின் வகைப்பாடு: மனையும் கட்டிடமும்
சொத்தின் விஸ்தீர்ணம்: 5720 SQ.FT
கிராமம் மற்றும் தெரு: தியாகராய நகர், மற்றும் பல புல எண் : 6107/1B, 6110/1B
புதிய கதவு எண்: 9
பழைய கதவு எண்: 43
பிளாக் எண்: 136

1916/2006
10-Aug-2006 
10-Aug-2006
10-Aug-2006
இரசீது
1. சென்னை லட்சுமி
ஜெனரல் பைனான்ஸ் லிட்
1.சென்னை ஷெரைன்
வேளாங்கன்னி சீனியர்
செகன்டரி ஸ்கூல்
-
கைமாற்றுத் தொகை: 
ரூ. 1,00,000/-
சந்தை மதிப்பு:
ரூ. 1,00,000/-
முந்தைய ஆவண எண்: 
1399/ 87
ஆவணக் குறிப்புகள் : மூன் அடமானக்கடனை பைசல் செய்வதாய் .
அட்டவணை A விவரங்கள்: 
சொத்தின் வகைப்பாடு: வீட்டுவீ மனை
சொத்தின் விஸ்தீர்ணம்: 5720 சதுரடி
கிராமம் மற்றும் தெரு: தியாகராய நகர், இல்லை புல எண் : 143/3PART, 143/8, 143/PART, 3107/1B, 6110/1B
புதிய கதவு எண்: 43
பழைய கதவு எண்: 9
பிளாக் எண்: 136

1653/2019
09-Jul-2019
09-Jul-2019
09-Jul-2019
உரிமை ஆவணங்களின் ஒப்படைப்பு ஆவணம்
1. ஷெரின் வேளாங்கன்னி சீனியர் செகண்டரி ஸ்கூல்(முத.) பி கே கே பிள்ளை(முக.)
1. கோட்டக் மகேந்திரா பாங்க் லிமிடெட்
-
கைமாற்றுத் தொகை: 
-
சந்தை மதிப்பு:
ரூ. 2,50,00,000/-
முந்தைய ஆவண எண்: 
1399/1987
அட்டவணை A விவரங்கள்: 
சொத்தின் வகைப்பாடு: மனையும் கட்டிடமும்
சொத்தின் விஸ்தீர்ணம்: 5720.0 சதுரடி
கிராமம் மற்றும் தெரு: தியாகராய நகர், கண்ணதாசன் தெரு,கண்ணையா தெரு
புல எண் : 143/B, 143/PART, 6107/1B, 6110/1B
புதிய கதவு எண்: 43
பழைய கதவு எண்: 9

1852/2020
10-Nov-2020 
10-Nov-2020
10-Nov-2020
இரசீது ஆவணம்
1. கோட்டக் மகேந்திரா பாங்க் லிமிடெட்(முத.) ஸ்ரீதர்(முக.)
1.ஷெரின் வேளாங்கன்னி சீனியர் செகேன்டரி ஸ்கூல்
-
கைமாற்றுத் தொகை: 
ரூ. 2,50,00,000/-
சந்தை மதிப்பு:
-
முந்தைய ஆவண எண்: 
1653/2019
அட்டவணை A விவரங்கள்: 
சொத்தின் வகைப்பாடு: மனையும் கட்டிடமும்
சொத்தின் விஸ்தீர்ணம்: 5720.0 சதுரடி
கிராமம் மற்றும் தெரு: தியாகராய நகர், கண்ணதாசன் தெரு,கண்ணையா தெரு
புல எண் : 143/B, 143/PART, 6107/1B, 6110/1B
புதிய கதவு எண்: 43
பழைய கதவு எண்: 9

1856/2020
10-Nov-2020 
10-Nov-2020
10-Nov-2020
உரிமை ஆவணங்களின் ஒப்படைப்பு ஆவணம்
1. ஷெரின் வேளாங்கன்னி சீனியர் செகண்டரி ஸ்கூல்(முத.) பாகலா குமாரி குமாரசாமி பிள்ளை(முக.)
1.ஐ.சி.ஐ.சி.ஐ வங்கி லிமிடெட் -
கைமாற்றுத் தொகை: 
-
சந்தை மதிப்பு:
ரூ. 3,63,99,590/-
முந்தைய ஆவண எண்: 
1399/1987
அட்டவணை A விவரங்கள்: 
சொத்தின் வகைப்பாடு: மனையும் கட்டிடமும்
சொத்தின் விஸ்தீர்ணம்: 5720.0 சதுரடி
கிராமம் மற்றும் தெரு: தியாகராய நகர், கண்ணதாசன் தெரு புல எண் : 6110/1B
எல்லை விபரங்கள்: 
கிழக்கு - ஹன்ஸ்மென் ரோடு க எண் 44 வேளாங்கண்ணி ஹாஸ்டல்,மேற்கு - ஹன்ஸ்மென் ரோடு க எண் 42 , கிருஷ்ணசாமி பிள்ளை சொத்து,வடக்கு - தண்டபாணி ரோடு க எண் 9ஏ நாயுடு வீடுவீ ,தெற்கு - மேற்படி ரோடு
சொத்து தொடர்பான குறிப்புரை: விஸ்: 5720 ச அடி வீடுவீ மனை.

பதிவுகளின் எண்ணிக்கை : 7
"""


def parse_header(text: str) -> Dict[str, Any]:
    header = {
        "sro": "",
        "certificate_no": "",
        "application_no": "",
        "certificate_date": "",
        "applicant_name": "",
        "village": "",
        "survey_details": "",
        "search_period_from": "",
        "search_period_to": "",
        "search_window_years": 0.0,
        "below_30yr_standard": True,
        "zone": "",
        "district": "",
        "data_available_from": "",
        "data_available_to": "",
        "requested_extent": "",
        "requested_door_no": "",
        "requested_boundaries": ""
    }

    # 1. SRO: Tamil or English
    m_sro = re.search(r'(?:S\.R\.O|சா\.ப\.அ|சார்பதிவாளர்\s*அலுவலகம்)[^:\r\n]*[:\s]+([^:\r\n]+?)(?=\s+(?:Date|நாள்|சான்று|மனு|Zone|District)|[\r\n]|$)', text, re.I)
    if m_sro:
        header["sro"] = m_sro.group(1).strip()

    # 2. Certificate No & Application No
    m_cert = re.search(r'(?:சான்று\s*எண்|Certificate\s*No\.?)[^:\r\n]*[:\s]+([A-Za-z0-9/_-]+)', text, re.I)
    if m_cert:
        header["certificate_no"] = m_cert.group(1).strip()

    m_app = re.search(r'(?:மனு\s*எண்|Application\s*No\.?|ECA\s*No\.?)[^:\r\n]*[:\s]+([A-Za-z0-9/_-]+)', text, re.I)
    if m_app:
        header["application_no"] = m_app.group(1).strip()

    # 3. Certificate Date
    m_date = re.search(r'(?:Date\s*/\s*நாள்|Date|நாள்)[^:\r\n]*[:\s]+([\d]{1,2}[-/][A-Za-z]{3,}[-/][\d]{2,4}|[\d]{1,2}[-/][\d]{1,2}[-/][\d]{2,4})', text, re.I)
    if m_date:
        header["certificate_date"] = m_date.group(1).strip()

    # 4. Applicant Name: search only within first 1500 chars
    m_appl = re.search(r'(?:திரு/திருமதி/செல்வி\.?|Applicant|மனுதாரர்)\s*[:\.\s]*([A-Za-z0-9\s\.\&]+?)(?=\s*(?:Tamil\s*Nadu|,|கீழ்க்கண்ட|விண்ணப்பித்துள்ளார்)|[\r\n]|$)', text[:1500], re.I)
    if m_appl:
        appl_clean = m_appl.group(1).strip()
        if len(appl_clean) > 2 and not any(k in appl_clean for k in ["சான்று", "வில்லங்கம்", "விண்ணப்ப"]):
            header["applicant_name"] = appl_clean

    # 5. Village and Survey

    m_vil = re.search(r'Village\s*/கிராமம்\s*:\s*([^\s\n\r]+)', text, re.I)
    m_sur = re.search(r'Survey\s*Details\s*/சர்வே\s*விவரம்\s*:\s*([^\n\r]+)', text, re.I)
    if m_vil and m_sur:
        header["village"] = m_vil.group(1).strip()
        header["survey_details"] = m_sur.group(1).strip()
    else:
        # Pure Tamil layout:
        # கிராமம் சர்வே விவரம்
        # தியாகராய நகர் 6107/1B, 6110/1B, 6110/2, 6107/4, 7797/2
        m_tm = re.search(r'கிராமம்\s+சர்வே\s+விவரம்\s*[\r\n]+([^\r\n]+)', text)
        if m_tm:
            line_val = m_tm.group(1).strip()
            # Split at the first digit
            d_idx = re.search(r'\d', line_val)
            if d_idx:
                header["village"] = line_val[:d_idx.start()].strip()
                header["survey_details"] = line_val[d_idx.start():].strip()
            else:
                header["village"] = line_val

    # 6. Search Period
    m_period_en = re.search(r'(?:Search\s*Period|தேடுதல்\s*காலம்)[^:\r\n]*[:\s]+([\d\-A-Za-z/]+)\s*-\s*([\d\-A-Za-z/]+)', text, re.I)
    m_period_tm = re.search(r'(\d+)\s*ஆண்டுகளுக்கு\s*([\d\-A-Za-z/]+)\s*முதல்\s*([\d\-A-Za-z/]+)\s*வரை', text, re.I)
    if m_period_en:
        header["search_period_from"] = m_period_en.group(1).strip()
        header["search_period_to"] = m_period_en.group(2).strip()
    elif m_period_tm:
        header["search_period_from"] = m_period_tm.group(2).strip()
        header["search_period_to"] = m_period_tm.group(3).strip()

    if header["search_period_from"] and header["search_period_to"]:
        try:
            d1 = datetime.strptime(header["search_period_from"], "%d-%b-%Y")
            d2 = datetime.strptime(header["search_period_to"], "%d-%b-%Y")
            years = round((d2 - d1).days / 365.25, 1)
            header["search_window_years"] = years
            header["below_30yr_standard"] = (years < 30.0)
        except Exception:
            pass

    # 7. Requested Property in Header
    m_tot_ext = re.search(r'(?:மொத்த\s*விஸ்தீர்ணம்|மொத்த\s*விஸ்தீர்ணம்|Total\s*Extent)\s*:\s*([^,\r\n]+)', text, re.I)
    if m_tot_ext:
        header["requested_extent"] = m_tot_ext.group(1).strip()
    m_tr_ext = re.search(r'(?:உரிமை\s*மாற்றப்பட்ட\s*விஸ்தீர்ணம்|Transferred\s*Extent)\s*:\s*([^,\r\n]+)', text, re.I)
    if m_tr_ext and not header["requested_extent"]:
        header["requested_extent"] = m_tr_ext.group(1).strip()

    m_hdr_door = re.search(r'(?:பழைய\s*கதவு\s*எண்|புதிய\s*கதவு\s*எண்|Old\s*Door\s*No|New\s*Door\s*No)\s*:\s*([^,\r\n]+)', text, re.I)
    if m_hdr_door:
        header["requested_door_no"] = m_hdr_door.group(1).strip()

    m_hdr_bounds = re.search(r'(?:எல்லை\s*விபரங்கள்|எல்லை\s*விவரங்கள்|Boundary\s*Details)\s*:\s*([\s\S]+?)(?=(?:\d+\s*புத்தகம்|1\s*புத்தகம்|Search\s*Period|வ\.\s*எண்|Sr\.\s*No|$))', text, re.I)
    if m_hdr_bounds:
        header["requested_boundaries"] = re.sub(r'\s+', ' ', m_hdr_bounds.group(1)).strip()

    # Zone / District
    m_zone = re.search(r'Zone:\s*([A-Za-z ]+?)\s+District:\s*([A-Za-z ]+?)\s+S\.R\.O:', text)
    if m_zone:
        header["zone"] = m_zone.group(1).strip()
        header["district"] = m_zone.group(2).strip()

    return header


def parse_entries_text(text: str) -> List[Dict[str, Any]]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    doc_regex = re.compile(r'^(?:(?P<sr>\d{1,4})[\.\)]?\s+)?(?P<doc>(?:[A-Za-z0-9\.\-\(\)]+\s+)?\d{1,6}/\d{4})\b(?!\s*[-/]\s*\d{2,4})')
    date_regex = re.compile(r'\b\d{1,2}[-/][A-Za-z]{3}[-/]\d{2,4}\b')

    chunk_indices = []
    for idx, line in enumerate(lines):
        # Must not be a date line like 18/06/2025
        if re.search(r'^\d{1,2}/\d{1,2}/\d{4}$', line):
            continue
        m = doc_regex.search(line)
        if m:
            # Look backwards 1-2 lines to ensure it is NOT a prior deed reference
            prev_context = " ".join(lines[max(0, idx - 2):idx]).lower()
            if any(k in prev_context for k in ["முந்தைய", "pr number", "முந்தைய ஆவண", "பத்திர நெ", "ஆவணத்தால் திருத்தம்", "பைசல் முன் பத்திர", "ஆவணம் 1 புத்தகம்"]):
                continue

            # Look forward 1-4 lines: must contain a date!
            next_context = " ".join(lines[idx + 1:min(len(lines), idx + 5)])
            if not date_regex.search(next_context):
                continue

            sr_val = m.group("sr")
            # If sr wasn't on the line, check if the previous line was a single digit (like '1' or '2')
            if not sr_val and idx > 0 and lines[idx - 1].isdigit():
                sr_val = lines[idx - 1]

            chunk_indices.append((idx, sr_val, m.group("doc").strip()))

    entries = []
    for c_idx, (start_idx, sr_val, doc_no) in enumerate(chunk_indices):
        end_idx = chunk_indices[c_idx + 1][0] if c_idx + 1 < len(chunk_indices) else len(lines)
        chunk_lines = lines[start_idx:end_idx]
        chunk_text = "\n".join(chunk_lines)

        sr_str = sr_val or str(c_idx + 1)

        # 1. Dates
        dates = date_regex.findall(chunk_text)
        exec_d = dates[0] if len(dates) > 0 else ""
        pres_d = dates[1] if len(dates) > 1 else exec_d
        reg_d = dates[2] if len(dates) > 2 else exec_d

        # 2. Split chunk into Sections:
        # A: Header/Dates
        # B: Nature & Parties (between dates and Financials/Schedule)
        # C: Financials (Consideration, Market, PR No, Document Remarks)
        # D: Schedules (Attavanai / Schedule A, B, C...)

        # Locate Financials start
        fin_split = re.search(r'(?:கைமாற்றுத்\s*தொகை|கைமாற்றுத்\s*தொகை|Consideration\s*Value)\s*:', chunk_text, re.I)
        fin_start_pos = fin_split.start() if fin_split else len(chunk_text)

        # Parties block is between the first dates and financials
        # Find where dates end
        last_date_pos = 0
        for m in date_regex.finditer(chunk_text[:fin_start_pos]):
            last_date_pos = max(last_date_pos, m.end())

        parties_block = chunk_text[last_date_pos:fin_start_pos].strip()
        parties_lines = [l.strip() for l in parties_block.splitlines() if l.strip()]

        # Nature: check first lines of parties_block before party 1
        nature_val = ""
        party_start_idx = 0
        for p_i, pl in enumerate(parties_lines):
            if re.match(r'^(?:1\.|1\.\.\.|\d+\.)', pl):
                party_start_idx = p_i
                break
            else:
                nature_val = (nature_val + " " + pl).strip()

        p_remaining = parties_lines[party_start_idx:]
        p_text = "\n".join(p_remaining)

        # Split Executants and Claimants:
        # In TN EC, Executants start with the first '1.' or '1...'
        # Claimants start with the NEXT '1.' or '1...'!
        exec_raw = ""
        claim_raw = ""
        m_ones = list(re.finditer(r'(?<!\d)(?:1\.\s*|1\.\.\.\s*)', p_text))
        if len(m_ones) >= 2:
            exec_raw = p_text[m_ones[0].start():m_ones[1].start()].strip()
            claim_raw = p_text[m_ones[1].start():].strip()
        elif len(m_ones) == 1:
            # Check if there is an explicit Claimant or Executant label
            exec_raw = p_text.strip()
        else:
            exec_raw = p_text.strip()

        # Clean trailing vol/page from claimants (e.g. standalone '-' or '1111, 387' or '1432, 45')
        claim_raw = re.sub(r'[\r\n\s]+-\s*$', '', claim_raw).strip()
        claim_raw = re.sub(r'[\r\n\s]+\d{3,4},\s*\d{2,3}\s*$', '', claim_raw).strip()

        # 3. Financials
        cons_val = ""
        m_cons = re.search(r'(?:கைமாற்றுத்\s*தொகை|கைமாற்றுத்\s*தொகை|Consideration\s*Value)[^:\r\n]*[:\s]+([^\r\n]+)', chunk_text, re.I)
        if m_cons:
            cons_val = m_cons.group(1).strip()

        mkt_val = ""
        m_mkt = re.search(r'(?:சந்தை\s*மதிப்பு|Market\s*Value)[^:\r\n]*[:\s]+([^\r\n]+)', chunk_text, re.I)
        if m_mkt:
            mkt_val = m_mkt.group(1).strip()

        pr_val = ""
        m_pr = re.search(r'(?:முந்தைய\s*ஆவண\s*எண்|PR\s*Number)[^:\r\n]*[:\s]+([^\r\n]+)', chunk_text, re.I)
        if m_pr:
            pr_val = m_pr.group(1).strip()

        rem_val = ""
        m_rem = re.search(r'(?:ஆவணக்\s*குறிப்புகள்|Document\s*Remarks)[^:\r\n]*[:\s]+([\s\S]+?)(?=(?:அட்டவணை|Schedule|சொத்தின்|சொத்தின்|எல்லை|$))', chunk_text, re.I)
        if m_rem:
            rem_val = re.sub(r'\s+', ' ', m_rem.group(1)).strip()

        # 4. Schedules
        # First search for explicit Schedule/Attavanai headings
        sched_splits = list(re.finditer(r'(?:Schedule\s+[A-Za-z0-9]+(?:\s+Details)?|Schedule\s+Item[A-Za-z0-9]+(?:\s+Details)?|Schedule\s+BItem[A-Za-z0-9]+(?:\s+Details)?|அட்டவணை\s*[A-Za-z0-9]+\s*விவரங்கள்:?|அட்டவணை\s*விவரங்கள்:?)', chunk_text, re.I))
        if not sched_splits:
            sched_splits = list(re.finditer(r'(?:சொத்தின்\s*வகைப்பாடு|சொத்தின்\s*வகைப்பாடு|Property\s*Type)\s*:', chunk_text, re.I))
        schedules = []

        if sched_splits:
            for s_i, sm in enumerate(sched_splits):
                s_start = sm.start()
                s_end = sched_splits[s_i + 1].start() if s_i + 1 < len(sched_splits) else len(chunk_text)
                s_block = chunk_text[s_start:s_end]
                s_name = sm.group(0).strip(":")

                pt = ""
                m_pt = re.search(r'(?:சொத்தின்\s*வகைப்பாடு|சொத்தின்\s*வகைப்பாடு|Property\s*Type)[^:\r\n]*[:\s]+([^\r\n]+)', s_block, re.I)
                if m_pt: pt = m_pt.group(1).strip()

                ext = ""
                sur = ""
                # Check புல எண்-விஸ்தீர்ணம் across lines until next field
                m_se = re.search(r'(?:புல\s*எண்\s*-\s*விஸ்தீர்ணம்|புல\s*எண்\s*-\s*விஸ்தீரணம்)[^:\r\n]*[:\s]+([\s\S]+?)(?=(?:புதிய|பழைய|New|Old|கதவு|Door|பிளாக்|மனை|Plot|தள|Floor|$))', s_block, re.I)
                if m_se:
                    val_comb = re.sub(r'\s+', ' ', m_se.group(1)).strip()
                    if " - " in val_comb:
                        sur, ext = val_comb.split(" - ", 1)
                        sur = sur.strip()
                        ext = ext.strip()
                    else:
                        sur = val_comb
                else:
                    m_sur = re.search(r'(?:Survey\s*No\.?|புல\s*எண்)[^:\r\n]*[:\s]+([^\r\n]+)', s_block, re.I)
                    if m_sur: sur = m_sur.group(1).strip()
                    m_ext = re.search(r'(?:Property\s*Extent|சொத்தின்\s*விஸ்தீர்ணம்|விஸ்தீர்ணம்|விஸ்தீரணம்|Extent)[^:\r\n]*[:\s]+([^\r\n]+)', s_block, re.I)
                    if m_ext: ext = m_ext.group(1).strip()

                vs = ""
                m_vs = re.search(r'(?:கிராமம்\s*மற்றும்\s*தெரு|Village\s*&\s*Street)[^:\r\n]*[:\s]+([^\r\n]+)', s_block, re.I)
                if m_vs: vs = m_vs.group(1).strip()

                nd = ""
                m_nd = re.search(r'(?:புதிய\s*கதவு\s*எண்|New\s*Door\s*No\.?)[^:\r\n]*[:\s]+([^\r\n]+)', s_block, re.I)
                if m_nd: nd = m_nd.group(1).strip()

                od = ""
                m_od = re.search(r'(?:பழைய\s*கதவு\s*எண்|Old\s*Door\s*No\.?)[^:\r\n]*[:\s]+([^\r\n]+)', s_block, re.I)
                if m_od: od = m_od.group(1).strip()

                fl = ""
                m_fl = re.search(r'(?:தள\s*எண்|Floor\s*No\.?|Flat\s*No\.?|அடுக்குமாடிக்\s*குடியிருப்பு\s*எண்)[^:\r\n]*[:\s]+([^\r\n]+)', s_block, re.I)
                if m_fl: fl = m_fl.group(1).strip()

                bnds = ""
                m_b = re.search(r'(?:எல்லை\s*விபரங்கள்|எல்லை\s*விவரங்கள்|Boundary\s*Details)[^:\r\n]*[:\s]+([\s\S]+?)(?=(?:சொத்து\s*தொடர்பான\s*குறிப்புரை|Schedule\s*Remarks|அட்டவணை|Schedule|$))', s_block, re.I)
                if m_b: bnds = re.sub(r'\s+', ' ', m_b.group(1)).strip()

                sr_rem = ""
                m_srem = re.search(r'(?:சொத்து\s*தொடர்பான\s*குறிப்புரை|சொத்து\s*தொடர்பான\s*குறிப்புரை|Schedule\s*Remarks)[^:\r\n]*[:\s]+([\s\S]+?)(?=(?:அட்டவணை|Schedule|$))', s_block, re.I)
                if m_srem: sr_rem = re.sub(r'\s+', ' ', m_srem.group(1)).strip()

                # If ext is in sr_rem, capture it
                if not ext and sr_rem:
                    m_e2 = re.search(r'(?:விஸ்|விஸ்தீரணம்|விஸ்தீர்ணம்)[^:\d]*[:\s]*(\d+[\d\.,\s]*(?:ச\s*அடி|சதுரடி|sq\.?ft|grounds?|கிரவுண்ட்))', sr_rem, re.I)
                    if m_e2:
                        ext = m_e2.group(1).strip()

                schedules.append({
                    "schedule_name": s_name,
                    "property_type": pt,
                    "extent": ext,
                    "village_street": vs,
                    "survey_no": sur,
                    "door_no": nd or od,
                    "new_door_no": nd,
                    "old_door_no": od,
                    "flat_no": fl,
                    "boundaries": bnds,
                    "schedule_remarks": sr_rem
                })

        entries.append({
            "sr": int(sr_str) if sr_str.isdigit() else (c_idx + 1),
            "doc_no": doc_no,
            "execution_date": exec_d,
            "presentation_date": pres_d,
            "registration_date": reg_d,
            "nature": nature_val,
            "executants": re.sub(r'\s+', ' ', exec_raw).strip(),
            "claimants": re.sub(r'\s+', ' ', claim_raw).strip(),
            "consideration": cons_val,
            "market_value": mkt_val,
            "pr_number": pr_val,
            "remarks": rem_val,
            "schedules": schedules
        })

    return entries


print("\n========== DOCUMENT 1 TEST ==========")
h1 = parse_header(DOC1_TEXT)
print("Doc 1 Header:")
for k, v in h1.items():
    if v: print(f"  {k}: {v}")

e1 = parse_entries_text(DOC1_TEXT)
print(f"\nDoc 1 Entries ({len(e1)}):")
for e in e1:
    print(f"  Sr: {e['sr']} | Doc: {e['doc_no']} | Date: {e['registration_date']}")
    print(f"    Nature: {e['nature']}")
    print(f"    Exec: {e['executants']}")
    print(f"    Claim: {e['claimants']}")
    print(f"    Cons: {e['consideration']} | Mkt: {e['market_value']} | PR: {e['pr_number']}")
    print(f"    Schedules ({len(e['schedules'])}):")
    for s in e['schedules']:
        print(f"      {s['schedule_name']} | Type: {s['property_type']} | Ext: {s['extent']} | S.No: {s['survey_no']} | Door: {s['door_no']}")



def clean_party_name(raw_name: str) -> str:
    s = raw_name.split("\n")[0].strip()
    s = re.sub(r'^(?:[\.\,\:\;]+\s*|\d+\.\.\.|\d+\.\s*|\d+\s*)', '', s)
    s = re.sub(r'(?<=[a-zA-Z\u0b80-\u0bff])\s+\d{1,2}(?=\s+(?:\d{1,2}\.|\b)|$)', '', s)
    s = re.sub(r'\s*\((?:Principal|Agent|பிரின்சிபல்|பிரின்ஸ்பால்|முத\.|முதல்வர்|முக\.|முகவர்|E & ஏஜெண்ட்|ஏஜெண்ட்|ஏஜண்ட்|Lessor|Lessee)\)', '', s, flags=re.I)
    s = re.sub(r'^(?:சென்னை|மதுரை|கோவை|திருச்சி|மெஸர்ஸ்\.?|மெசர்ஸ்\.?)\s+', '', s)
    s = re.sub(r'\s+(?:Tamil Nadu|India)$', '', s, flags=re.I)
    return re.sub(r'\s+', ' ', s).strip()


def classify_entity_type(name: str) -> str:
    n_low = name.lower()
    if any(k in n_low for k in ["bank", "பாங்க்", "வங்கி", "finance", "பைனான்ஸ்", "fund"]):
        return "Bank / Financial Institution"
    elif any(k in n_low for k in ["school", "college", "trust", "charities", "சாரிடிஸ்", "academy", "foundation", "பள்ளி", "கல்லூரி"]):
        return "Trust / Educational Institution"
    elif any(k in n_low for k in ["pvt ltd", "ltd", "limited", "llp", "லிமிடெட்", "பிரைவேட்", "எல்எல்பி", "corporation", "estates", "construction"]):
        return "Corporate / Entity"
    elif any(k in n_low for k in ["authority", "development authority", "cmda", "மண்டலம்", "ஆரோரிட்டி"]):
        return "Government / Statutory Body"
    elif ";" in name or " 2. " in name or " மற்றும் " in name:
        return "Joint Ownership"
    return "Individual"


def build_owners_registry(tx_list: List[Dict[str, Any]], header_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    100% Dynamic, generalizable Title & Owners Registry Engine for any TNREGINET EC.
    Identifies all property units, resolves current legal title holders, historical owners,
    and financial institutions, producing complete owner dossiers.
    """
    if not tx_list:
        return {
            "summary": {
                "total_parties": 0,
                "current_owners_count": 0,
                "historical_owners_count": 0,
                "institutions_count": 0,
                "units_count": 0
            },
            "current_owners": [],
            "all_owners": [],
            "property_units": []
        }

    # 1. Cluster transactions by Property Unit / Schedule
    clusters = {}
    for tx in tx_list:
        scheds = tx.get("schedules") or []
        if not scheds:
            unit_key = "Main Property / Certificate Scope"
            clusters.setdefault(unit_key, {"schedules": [], "transactions": []})
            clusters[unit_key]["transactions"].append(tx)
            continue

        # Extract primary location identifier (Street + Primary S.No)
        s0 = scheds[0]
        street = (s0.get("village_street") or "").strip()
        survey = (s0.get("survey_no") or "").strip()
        flat = (s0.get("flat_no") or "").strip()
        plot = (s0.get("plot_no") or "").strip()
        door = (s0.get("door_no") or "").strip()

        # Simplify survey to primary parcel token (e.g. '6107/1B' or '4/1' or '5/10')
        primary_sy_token = re.findall(r'\b\d{1,5}(?:/[A-Za-z0-9\-]+)?\b', survey)
        sy_cluster_key = primary_sy_token[0] if primary_sy_token else survey

        # Street simplification
        street_clean = re.sub(r'^(?:Adyar,\s*|தியாகராய\s*நகர்,\s*)', '', street, flags=re.I).strip()
        if "/" in street_clean:
            street_clean = street_clean.split("/")[0].strip()

        parts = []
        if street_clean and street_clean != "-": parts.append(street_clean)
        if sy_cluster_key and sy_cluster_key != "-": parts.append(f"S.No {sy_cluster_key}")
        if flat and flat != "-": parts.append(f"Flat {flat}")
        elif plot and plot != "-": parts.append(f"Plot {plot}")

        unit_key = " | ".join(parts) if parts else "Main Property Unit"
        clusters.setdefault(unit_key, {"schedules": [], "transactions": []})
        for s in scheds:
            if s not in clusters[unit_key]["schedules"]:
                clusters[unit_key]["schedules"].append(s)
        if tx not in clusters[unit_key]["transactions"]:
            clusters[unit_key]["transactions"].append(tx)

    # 2. Track Title Devolution & Build Owner Dossiers
    conveyance_kws = ["sale", "கிரைய", "கிைரய", "விற்பனை", "விற்பைன", "settlement", "செட்டில்மென்ட்", "தான", "gift", "பாகப்பிரிவினை", "partition", "conveyance", "உரிமை மாற்றம்"]
    mortgage_kws = ["mortgage", "அடைமானம்", "ஈடு", "ஒப்படைப்பு", "ஒப்பைடப்பு", "உரிமை ஆவண", "modt", "deposit of title"]
    receipt_kws = ["receipt", "இரசீது", "ரசீது", "discharge", "release", "விடுதலை"]

    # Global party index
    party_profiles = {}

    def get_or_create_party(name: str):
        clean = clean_party_name(name)
        if not clean or clean in ["-", "None", "Null"]:
            return None
        # Normalize key
        norm_key = re.sub(r'[^a-zA-Z0-9\u0b80-\u0bff]', '', clean).lower()
        if norm_key not in party_profiles:
            from app.translator import transliterate_tamil_text, format_bilingual_entity
            # Create bilingual name
            has_tamil = any('\u0b80' <= c <= '\u0bff' for c in clean)
            bilingual_name = format_bilingual_entity(clean) if has_tamil else clean

            party_profiles[norm_key] = {
                "owner_id": norm_key,
                "name": clean,
                "name_bilingual": bilingual_name,
                "role": "Registered Party",
                "is_current_owner": False,
                "entity_type": classify_entity_type(clean),
                "property_units": [],
                "acquisition": None,
                "transferred_to": None,
                "mortgages": [],
                "has_active_mortgages": False,
                "transactions": [],
                "total_tx_count": 0
            }
        return party_profiles[norm_key]

    # Process each unit cluster
    unit_summaries = []
    for unit_key, unit_data in clusters.items():
        u_txs = unit_data["transactions"]
        u_scheds = unit_data["schedules"]
        primary_sched = u_scheds[0] if u_scheds else {}

        # Trace devolution chronologically
        unit_current_holder = None

        for tx in u_txs:
            nat = (tx.get("nature") or "").lower()
            doc_no = tx.get("doc_no") or "-"
            dt = tx.get("registration_date") or tx.get("execution_date") or "-"
            cons = tx.get("consideration") or "-"
            mkt = tx.get("market_value") or "-"

            exec_raw = tx.get("executants") or ""
            claim_raw = tx.get("claimants") or ""

            # Executant parties
            exec_parties = [p for p in re.split(r'(?<!\d)\d+\.\s*', exec_raw) if p.strip()] or [exec_raw]
            claim_parties = [p for p in re.split(r'(?<!\d)\d+\.\s*', claim_raw) if p.strip()] or [claim_raw]

            # Register transaction in parties
            for ep in exec_parties:
                p_obj = get_or_create_party(ep)
                if p_obj:
                    p_obj["total_tx_count"] += 1
                    p_obj["transactions"].append({
                        "doc_no": doc_no,
                        "date": dt,
                        "nature": tx.get("nature") or "-",
                        "role": "Executant / Transferor",
                        "counterparty": clean_party_name(claim_raw),
                        "amount": cons if cons != "-" else mkt
                    })
                    if unit_key not in p_obj["property_units"]:
                        p_obj["property_units"].append(unit_key)

            for cp in claim_parties:
                p_obj = get_or_create_party(cp)
                if p_obj:
                    p_obj["total_tx_count"] += 1
                    p_obj["transactions"].append({
                        "doc_no": doc_no,
                        "date": dt,
                        "nature": tx.get("nature") or "-",
                        "role": "Claimant / Transferee",
                        "counterparty": clean_party_name(exec_raw),
                        "amount": cons if cons != "-" else mkt
                    })
                    if unit_key not in p_obj["property_units"]:
                        p_obj["property_units"].append(unit_key)

            # Check Title Transfer deeds
            if any(k in nat for k in conveyance_kws):
                for cp in claim_parties:
                    c_obj = get_or_create_party(cp)
                    if c_obj:
                        c_obj["acquisition"] = {
                            "doc_no": doc_no,
                            "date": dt,
                            "nature": tx.get("nature") or "-",
                            "consideration": cons,
                            "market_value": mkt,
                            "acquired_from": clean_party_name(exec_raw),
                            "unit": unit_key,
                            "extent": primary_sched.get("extent") or "-"
                        }
                        # Previous owner now transferred out
                        if unit_current_holder and unit_current_holder != c_obj:
                            unit_current_holder["transferred_to"] = {
                                "doc_no": doc_no,
                                "date": dt,
                                "transferred_to": c_obj["name"]
                            }
                            unit_current_holder["role"] = "Historical / Prior Owner"
                            unit_current_holder["is_current_owner"] = False

                        unit_current_holder = c_obj
                        unit_current_holder["role"] = "Current Legal Owner / Absolute Title Holder"
                        unit_current_holder["is_current_owner"] = True

            # Check Mortgage deeds
            elif any(k in nat for k in mortgage_kws) and not any(k in nat for k in receipt_kws):
                # Executant is Mortgagor / Borrower, Claimant is Lender
                for ep in exec_parties:
                    e_obj = get_or_create_party(ep)
                    if e_obj:
                        e_obj["mortgages"].append({
                            "doc_no": doc_no,
                            "date": dt,
                            "lender": clean_party_name(claim_raw),
                            "amount": cons if cons != "-" else mkt,
                            "status": "OPEN",
                            "discharge_doc": "-"
                        })
                        e_obj["has_active_mortgages"] = True

                for cp in claim_parties:
                    c_obj = get_or_create_party(cp)
                    if c_obj and c_obj["entity_type"] == "Bank / Financial Institution":
                        c_obj["role"] = "Institutional Mortgagee / Lender"

            # Check Receipt / Discharge deeds
            elif any(k in nat for k in receipt_kws):
                # Executant is Bank discharging, Claimant is Owner getting release
                pr_ref = tx.get("pr_number") or ""
                rem_ref = tx.get("remarks") or ""
                ref_str = f"{pr_ref} {rem_ref}"

                for cp in claim_parties:
                    c_obj = get_or_create_party(cp)
                    if c_obj:
                        for m in c_obj["mortgages"]:
                            if m["doc_no"] in ref_str or m["doc_no"] == pr_ref:
                                m["status"] = "CLOSED"
                                m["discharge_doc"] = f"Doc {doc_no} ({dt})"
                        c_obj["has_active_mortgages"] = any(m["status"] == "OPEN" for m in c_obj["mortgages"])

        unit_summaries.append({
            "unit_key": unit_key,
            "current_owner": unit_current_holder["name"] if unit_current_holder else "-",
            "extent": primary_sched.get("extent") or "-",
            "survey_no": primary_sched.get("survey_no") or "-",
            "door_no": primary_sched.get("door_no") or "-",
            "total_transactions": len(u_txs)
        })

    all_owners_list = list(party_profiles.values())
    current_owners = [o for o in all_owners_list if o["is_current_owner"]]
    historical_owners = [o for o in all_owners_list if not o["is_current_owner"] and o["acquisition"]]
    institutions = [o for o in all_owners_list if o["entity_type"] in ["Bank / Financial Institution", "Government / Statutory Body"]]

    return {
        "summary": {
            "total_parties": len(all_owners_list),
            "current_owners_count": len(current_owners),
            "historical_owners_count": len(historical_owners),
            "institutions_count": len(institutions),
            "units_count": len(clusters)
        },
        "current_owners": current_owners,
        "historical_owners": historical_owners,
        "institutions": institutions,
        "all_owners": all_owners_list,
        "property_units": unit_summaries
    }


print("\n========== TESTING OWNERS REGISTRY ON DOC 1 ==========")
reg1 = build_owners_registry(e1, h1)
print(f"Doc 1 Summary: {reg1['summary']}")
print("Doc 1 Current Owners:")
for co in reg1["current_owners"]:
    print(f"  * {co['name']} ({co['entity_type']}) - Role: {co['role']}")
    print(f"    Acquired via: Doc {co['acquisition']['doc_no']} ({co['acquisition']['date']}) from {co['acquisition']['acquired_from']}")
    print(f"    Amount: {co['acquisition']['consideration']}")
print("Doc 1 All Parties:")
for o in reg1["all_owners"]:
    print(f"  - {o['name']} | Role: {o['role']} | Entity: {o['entity_type']} | Tx Count: {o['total_tx_count']}")



print("\n========== DOCUMENT 3 TEST ==========")
h3 = parse_header(DOC3_TEXT)
print("Doc 3 Header:")
for k, v in h3.items():
    if v: print(f"  {k}: {v}")

e3 = parse_entries_text(DOC3_TEXT)
print(f"\nDoc 3 Entries ({len(e3)}):")
for e in e3:
    print(f"  Sr: {e['sr']} | Doc: {e['doc_no']} | Date: {e['registration_date']}")
    print(f"    Nature: {e['nature']}")
    print(f"    Exec: {e['executants']}")
    print(f"    Claim: {e['claimants']}")
    print(f"    Cons: {e['consideration']} | Mkt: {e['market_value']} | PR: {e['pr_number']}")
    print(f"    Schedules ({len(e['schedules'])}):")
    for s in e['schedules']:
        print(f"      {s['schedule_name']} | Type: {s['property_type']} | Ext: {s['extent']} | S.No: {s['survey_no']} | Door: {s['door_no']}")

print("\n========== TESTING OWNERS REGISTRY ON DOC 3 ==========")
reg3 = build_owners_registry(e3, h3)
print(f"Doc 3 Summary: {reg3['summary']}")
print("Doc 3 Current Owners:")
for co in reg3["current_owners"]:
    print(f"  * {co['name']} ({co['entity_type']}) - Role: {co['role']}")
    print(f"    Acquired via: Doc {co['acquisition']['doc_no']} ({co['acquisition']['date']}) from {co['acquisition']['acquired_from']}")
    print(f"    Amount: {co['acquisition']['consideration']}")
    print(f"    Loans: {len(co['mortgages'])}")
    for m in co['mortgages']:
        print(f"      - Mortgage {m['doc_no']} to {m['lender']} ({m['amount']}): Status = {m['status']} (Discharge: {m['discharge_doc']})")
print("Doc 3 Historical Owners:")
for ho in reg3["historical_owners"]:
    print(f"  * {ho['name']} | Acquired from: {ho['acquisition']['acquired_from']} -> Transferred to: {ho.get('transferred_to')}")

