# -*- coding: utf-8 -*-
"""
Bilingual Translation Layer for Real Estate OCR.
Primary engine: IndicTrans2 (AI4Bharat) — true neural Tamil ↔ English translation.
Fallback engine: Phonetic transliteration (rule-based, no model required).

Standard Output Format:  English Name (Tamil Name)
Examples:
    - Village: Kallidaikurichi (கள்ளிடைக்குறிச்சி)
    - District: Villupuram (விழுப்புரம்)
    - Taluk: Ambasamudram (அம்பாசமுத்திரம்)
    - Owner: Elangovan (S/o Nagappan) (நாகப்பன் மகன் இளங்கோவன்)
"""

import re
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# IndicTrans2 engine — imported lazily (None until first use)
try:
    from app.indic_translator import translate_to_tamil, translate_to_english, is_available as _it2_available
    _INDICTRANS2_IMPORTED = True
except ImportError:
    _INDICTRANS2_IMPORTED = False
    def translate_to_tamil(text): return None   # type: ignore
    def translate_to_english(text): return None  # type: ignore
    def _it2_available(): return False            # type: ignore

# Independent Tamil vowels
TAMIL_VOWELS = {
    'அ': 'a', 'ஆ': 'aa', 'இ': 'i', 'ஈ': 'ee', 'உ': 'u', 'ஊ': 'oo',
    'எ': 'e', 'ஏ': 'e', 'ஐ': 'ai', 'ஒ': 'o', 'ஓ': 'o', 'ஔ': 'au',
}

# Consonants: Unvoiced (default) and Voiced (intervocalic / post-nasal)
TAMIL_CONSONANTS = {
    'க': ('k', 'g'), 'ங': ('ng', 'ng'), 'ச': ('s', 's'), 'ஞ': ('ny', 'ny'),
    'ட': ('t', 'd'), 'ண': ('n', 'n'), 'த': ('th', 'th'), 'ந': ('n', 'n'),
    'ப': ('p', 'b'), 'ம': ('m', 'm'), 'ய': ('y', 'y'), 'ர': ('r', 'r'),
    'ல': ('l', 'l'), 'வ': ('v', 'v'), 'ழ': ('zh', 'zh'), 'ள': ('l', 'l'),
    'ற': ('r', 'r'), 'ன': ('n', 'n'), 'ஜ': ('j', 'j'), 'ஷ': ('sh', 'sh'),
    'ஸ': ('s', 's'), 'ஹ': ('h', 'h'), 'க்ஷ': ('ksh', 'ksh')
}

# Vowel diacritics / signs
TAMIL_VOWEL_SIGNS = {
    'ா': 'aa', 'ி': 'i', 'ீ': 'ee', 'ு': 'u', 'ூ': 'oo',
    'ெ': 'e', 'ே': 'e', 'ை': 'ai', 'ொ': 'o', 'ோ': 'o', 'ௌ': 'au',
    '்': ''  # Virama removes inherent vowel
}

# Canonical dictionary of Tamil Nadu revenue locations for official government spellings
CANONICAL_PLACES = {
    # Districts
    "திருவாரூர்": "Thiruvarur", "thiruvarur": "திருவாரூர்",
    "திருவாளூர்": "Thiruvarur", "திருவாளுர்": "Thiruvarur", "திடுவாதர்": "Thiruvarur",
    "விழுப்புரம்": "Villupuram", "villupuram": "விழுப்புரம்",
    "தஞ்சாவூர்": "Thanjavur", "thanjavur": "தஞ்சாவூர்",
    "ஈரோடு": "Erode", "erode": "ஈரோடு",
    "சேலம்": "Salem", "salem": "சேலம்", "சலம்": "Salem",
    "மதுரை": "Madurai", "madurai": "மதுரை",
    "கோயம்புத்தூர்": "Coimbatore", "coimbatore": "கோயம்புத்தூர்",
    "சென்னை": "Chennai", "chennai": "சென்னை",
    "திருச்சிராப்பள்ளி": "Tiruchirappalli", "tiruchirappalli": "திருச்சிராப்பள்ளி",
    "தூத்துக்குடி": "Thoothukudi", "thoothukudi": "தூத்துக்குடி", "தாத்துச்குய": "Thoothukudi",
    "திண்டுக்கல்": "Dindigul", "dindigul": "திண்டுக்கல்",
    "திருப்பூர்": "Tiruppur", "tiruppur": "திருப்பூர்",
    "திருநெல்வேலி": "Tirunelveli", "tirunelveli": "திருநெல்வேலி",
    "வேலூர்": "Vellore", "vellore": "வேலூர்",
    "கடலூர்": "Cuddalore", "cuddalore": "கடலூர்",
    "நாகப்பட்டினம்": "Nagapattinam", "nagapattinam": "நாகப்பட்டினம்",
    "புதுக்கோட்டை": "Pudukkottai", "pudukkottai": "புதுக்கோட்டை",
    "ராமநாதபுரம்": "Ramanathapuram", "ramanathapuram": "ராமநாதபுரம்",
    "சிவகங்கை": "Sivaganga", "sivaganga": "சிவகங்கை",
    "விருதுநகர்": "Virudhunagar", "virudhunagar": "விருதுநகர்",
    "தேனி": "Theni", "theni": "தேனி",
    "கரூர்": "Karur", "karur": "கரூர்",
    "நாமக்கல்": "Namakkal", "namakkal": "நாமக்கல்",
    "நீலகிரி": "Nilgiris", "nilgiris": "நீலகிரி",
    "தர்மபுரி": "Dharmapuri", "dharmapuri": "தர்மபுரி",
    "கிருஷ்ணகிரி": "Krishnagiri", "krishnagiri": "கிருஷ்ணகிரி",
    "அரியலூர்": "Ariyalur", "ariyalur": "அரியலூர்",
    "பெரம்பலூர்": "Perambalur", "perambalur": "பெரம்பலூர்",
    "காஞ்சிபுரம்": "Kanchipuram", "kanchipuram": "காஞ்சிபுரம்",
    "திருவள்ளூர்": "Tiruvallur", "tiruvallur": "திருவள்ளூர்",
    "ராணிப்பேட்டை": "Ranipet", "ranipet": "ராணிப்பேட்டை",
    "திருப்பத்தூர்": "Tirupathur", "tirupathur": "திருப்பத்தூர்",
    "தென்காசி": "Tenkasi", "tenkasi": "தென்காசி",
    "கன்னியாகுமரி": "Kanyakumari", "kanyakumari": "கன்னியாகுமரி",
    "கள்ளக்குறிச்சி": "Kallakurichi", "kallakurichi": "கள்ளக்குறிச்சி",
    "செங்கல்பட்டு": "Chengalpattu", "chengalpattu": "செங்கல்பட்டு", "chengleput": "செங்கல்பட்டு",
    "சங்கல்பட்டு": "Chengalpattu", "ெசங்கல்பட்டு": "Chengalpattu",
    "chengleput joint i": "செங்கல்பட்டு இணை I", "chengleput joint 1": "செங்கல்பட்டு இணை I", "chengleput joint": "செங்கல்பட்டு இணை",
    "மயிலாடுதுறை": "Mayiladuthurai", "mayiladuthurai": "மயிலாடுதுறை",

    # Taluks
    "திண்டிவனம்": "Tindivanam", "tindivanam": "திண்டிவனம்",
    "செங்கல்பட்டு": "Chengalpattu", "chengalpattu": "செங்கல்பட்டு",
    "பட்டுக்கோட்டை": "Pattukkottai", "pattukkottai": "பட்டுக்கோட்டை",
    "நன்னிலம்": "Nannilam", "nannilam": "நன்னிலம்", "நள்aிலம்": "நன்னிலம்", "நளகாலம்": "நன்னிலம்",
    "கோபிசெட்டிபாளையம்": "Gobichettipalayam", "gobichettipalayam": "கோபிசெட்டிபாளையம்",
    "பொள்ளாச்சி": "Pollachi", "pollachi": "பொள்ளாச்சி",
    "மேலூர்": "Melur", "melur": "மேலூர்",
    "அத்தூர்": "Attur", "attur": "அத்தூர்",
    "மன்னார்குடி": "Mannargudi", "mannargudi": "மன்னார்குடி",
    "கோடவாசல்": "Kodavasal", "kodavasal": "கோடவாசல்",
    "நீடாமங்கலம்": "Needamangalam", "needamangalam": "நீடாமங்கலம்",
    "வலங்கைமான்": "Valangaiman", "valangaiman": "வலங்கைமான்",
    "அம்பத்தூர்": "Ambattur", "ambattur": "அம்பத்தூர்",
    "மாம்பலம்": "Mambalam", "mambalam": "மாம்பலம்",
    "திருவொற்றியூர்": "Tiruvottiyur", "tiruvottiyur": "திருவொற்றியூர்",
    "மேட்டுப்பாளையம்": "Mettupalayam", "mettupalayam": "மேட்டுப்பாளையம்",
    "சூலூர்": "Sulur", "sulur": "சூலூர்",
    "தாம்பரம்": "Tambaram", "tambaram": "தாம்பரம்",
    "பல்லாவரம்": "Pallavaram", "pallavaram": "பல்லாவரம்",
    "ஆலந்தூர்": "Alandur", "alandur": "ஆலந்தூர்",
    "ஆவடி": "Avadi", "avadi": "ஆவடி",
    "சேலையூர்": "Selaiyur", "selaiyur": "சேலையூர்",
    "பூந்தமல்லி": "Poonamallee", "poonamallee": "பூந்தமல்லி",

    # Villages
    "அலப்பாக்கம்": "Alappakkam", "alappakkam": "அலப்பாக்கம்",
    "வடமங்கலம்": "Vadamangalam", "vadamangalam": "வடமங்கலம்",
    "கீழையூர்": "Keezhaiyur", "keezhaiyur": "கீழையூர்",
    "சித்தோடு": "Chithode", "chithode": "சித்தோடு",
    "ஓடையகுளம்": "Odayakulam", "odayakulam": "ஓடையகுளம்", "உடையகுளம்": "ஓடையகுளம்",
    "செங்கபடை": "Sengapadai", "sengapadai": "செங்கபடை",
    "குமாரப்பாளையம்": "Kumarapalayam", "kumarapalayam": "குமாரப்பாளையம்",
    "வேளச்சேரி": "Velachery", "velachery": "வேளச்சேரி",
    "செம்பாக்கம்": "Sembakkam", "sembakkam": "செம்பாக்கம்",
    "சம்பாக்கம்": "Sembakkam", "ெசம்பாக்கம்": "செம்பாக்கம்", "சமெ்பாக்கம்": "Sembakkam",
    "சோழிங்கநல்லூர்": "Sholinganallur", "sholinganallur": "சோழிங்கநல்லூர்",
    "ஆலந்தூர்": "Alandur", "alandur": "ஆலந்தூர்",
    "அடையாறு": "Adyar", "adyar": "அடையாறு", "adayar": "அடையாறு",
    "மயிலாப்பூர்": "Mylapore", "mylapore": "மயிலாப்பூர்",
    "கிண்டி": "Guindy", "guindy": "கிண்டி",
    "சென்னை தெற்கு": "Chennai South", "chennai south": "சென்னை தெற்கு",
    "சென்னை வடக்கு": "Chennai North", "chennai north": "சென்னை வடக்கு",
    "சென்னை மத்தி": "Chennai Central", "chennai central": "சென்னை மத்தி",
    "அம்பாசமுத்திரம்": "Ambasamudram", "ambasamudram": "அம்பாசமுத்திரம்",
    "கள்ளிடைக்குறிச்சி": "Kallidaikurichi", "kallidaikurichi": "கள்ளிடைக்குறிச்சி",
    "அயனாவரம்": "Ayanavaram", "ayanavaram": "அயனாவரம்",
    "வில்லிவாக்கம்": "Villivakkam", "villivakkam": "வில்லிவாக்கம்",
    "பெரம்பூர்": "Perambur", "perambur": "பெரம்பூர்",
    "எழும்பூர்": "Egmore", "egmore": "எழும்பூர்",
    "புரசைவாக்கம்": "Purasawalkam", "purasawalkam": "புரசைவாக்கம்",
    "மண்ணடி": "Mannady", "mannady": "மண்ணடி",
    "ராயபுரம்": "Royapuram", "royapuram": "ராயபுரம்",
    "தண்டையார்பேட்டை": "Tondiarpet", "tondiarpet": "தண்டையார்பேட்டை",

    # State name -- surprisingly not a "district/taluk/village" but shows up
    # constantly in institution names ("Tamilnadu Industrial ... Corporation",
    # "Tamil Nadu Housing Board", etc.), and without an entry here it fell
    # through to the raw phonetic engine and came out unreadable.
    "தமிழ்நாடு": "Tamil Nadu", "tamil nadu": "தமிழ்நாடு", "tamilnadu": "தமிழ்நாடு",
}

COMMON_NAMES = {
    "சுகுமார்": "Sukumar", "sukumar": "சுகுமார்",
    "முத்துலட்சுமி": "Muthulakshmi", "muthulakshmi": "முத்துலட்சுமி",
    "இராமன்": "Raman", "raman": "இராமன்", "ராமன்": "Raman",
    "செந்தில்குமார்": "Senthilkumar", "senthilkumar": "செந்தில்குமார்",
    "சந்தில்குமார்": "Senthilkumar",
    "சண்முகம்": "Shanmugam", "shanmugam": "சண்முகம்",
    "ராஜேந்திரன்": "Rajendran", "rajendran": "ராஜேந்திரன்", "இராஜந்திரன்": "Rajendran", "இராஜேந்திரன்": "Rajendran",
    "பக்கிரிசாமி": "Pakkirisamy", "pakkirisamy": "பக்கிரிசாமி",
    "கோவிந்தராசு": "Govindarasu", "govindarasu": "கோவிந்தராசு",
    "கோவிந்தராஜூ": "Govindarajoo", "govindarajoo": "கோவிந்தராஜூ", "கோவிந்தராஜு": "Govindarajoo", "கோவிந்தராஜ்": "Govindaraj",
    "நாராயணன்": "Narayanan", "narayanan": "நாராயணன்", "நாராயண": "Narayanan",
    "வேலுசாமி": "Velusamy", "velusamy": "வேலுசாமி",
    "பான்னுசாமி": "Ponnusamy", "பொன்னுசாமி": "Ponnusamy", "ponnusamy": "பொன்னுசாமி",
    "தனலட்சுமி": "Dhanalakshmi", "dhanalakshmi": "தனலட்சுமி",
    "சுப்பிரமணியம்": "Subramaniam", "subramaniam": "சுப்பிரமணியம்",
    "பாலசுப்பிரமணியம்": "Balasubramaniam", "balasubramaniam": "பாலசுப்பிரமணியம்",
    "சின்னக்கண்ணு": "Chinnakannu", "chinnakannu": "சின்னக்கண்ணு", "சின்னகண்ணு": "Chinnakannu",
    "ரங்கநாதன்": "Ranganathan", "ranganathan": "ரங்கநாதன்", "ரெங்கநாதன்": "Ranganathan",
    "அருண்குமார்": "Arunkumar", "arunkumar": "அருண்குமார்",
    "ராமநாதன்": "Ramanathan", "ramanathan": "ராமநாதன்",
    "சின்னசாமி": "Chinnaswamy", "chinnaswamy": "சின்னசாமி",
    "அம்சவல்லி": "Amsavalli", "amsavalli": "அம்சவல்லி",
    "கிருஷ்ணன்": "Krishnan", "krishnan": "கிருஷ்ணன்",
    "கிருஷ்ணம்மாள்": "Krishnammal", "krishnammal": "கிருஷ்ணம்மாள்",
    "கிருஷ்ண": "Krishna", "krishna": "கிருஷ்ண",
    "கிருஷ்ணகுமார்": "Krishnakumar", "krishnakumar": "கிருஷ்ணகுமார்",
    "கிருஷ்ணமூர்த்தி": "Krishnamoorthy", "krishnamoorthy": "கிருஷ்ணமூர்த்தி",
    "கிருஷ்ணசாமி": "Krishnaswamy", "krishnaswamy": "கிருஷ்ணசாமி",
    "கிருஷ்ணவேணி": "Krishnaveni", "krishnaveni": "கிருஷ்ணவேணி",
    "கிருஷ்ணகிரி": "Krishnagiri", "krishnagiri": "கிருஷ்ணகிரி",
    "மோகன்": "Mohan", "mohan": "மோகன்",
    "மோகனா": "Mohana", "mohana": "மோகனா",
    "மோகன": "Mohan",
    "சுவாமி": "Swami", "swami": "சுவாமி", "swamy": "சுவாமி",
    "சுவாமிநாதன்": "Swaminathan", "swaminathan": "சுவாமிநாதன்",
    "சாமி": "Samy", "samy": "சாமி",
    "ராமானுஜம்": "Ramanujam", "ramanujam": "ராமானுஜம்",
    "இராமானுஜம்": "Ramanujam",
    "ராமானுஜன்": "Ramanujan", "ramanujan": "ராமானுஜன்",
    "ராமனுஜம்": "Ramanujam",
    "அலோக்": "Alok", "alok": "அலோக்",
    "குமார்": "Kumar", "kumar": "குமார்",
    "அலோக் குமார்": "Alok Kumar", "alok kumar": "அலோக் குமார்",
    "குலேச்சா": "Gulechha", "குலிசா": "Gulechha", "gulechha": "குலேச்சா", "gulecha": "குலேச்சா",
    "ரகுராம்": "Raghuram", "raghuram": "ரகுராம்",
    "சுகுமாரன்": "Sukumaran", "sukumaran": "சுகுமாரன்",
    "பாலாஜி": "Balaji", "balaji": "பாலாஜி",
    "விஸ்வேஸ்வர": "Visweswara", "visweswara": "விஸ்வேஸ்வர",
    "ரெட்டி": "Reddy", "reddy": "ரெட்டி",
    "ராஜகோபால்": "Rajagopal", "rajagopal": "ராஜகோபால்",
    "சுஜாதா": "Sujatha", "sujatha": "சுஜாதா",
    "சுமதி": "Sumathi", "sumathi": "சுமதி",
    "தீபா": "Deepa", "deepa": "தீபா",
    "மணி": "Mani", "mani": "மணி",
    "வள்ளியம்மை": "Valliyammai", "valliyammai": "வள்ளியம்மை",
    "வள்ளியம்மாள்": "Valliammal", "valliammal": "வள்ளியம்மாள்",
    "அண்ணாமலை": "Annamalai", "அண்ணாமைல": "Annamalai", "annamalai": "அண்ணாமலை",
    "லலிதா": "Lalitha", "lalitha": "லலிதா",
    "டாக்டர்": "Dr.", "டாக்டர்.": "Dr.", "dr.": "டாக்டர்.", "dr": "டாக்டர்.", "doctor": "டாக்டர்",
    "மங்காதேவி": "Mangadevi", "mangadevi": "மங்காதேவி",
    "மங்கா தேவி": "Manga Devi", "manga devi": "மங்கா தேவி",
    "மங்கா": "Manga", "manga": "மங்கா",
    "தேவி": "Devi", "devi": "தேவி",
    "விமலாதேவி": "Vimaladevi", "vimaladevi": "விமலாதேவி",
    "ஷோபனாதேவி": "Shobanadevi", "shopanaathevi": "ஷோபனாதேவி", "shobanadevi": "ஷோபனாதேவி",
    "மஞ்சுளாதேவி": "Manjuladevi", "manysulaathevi": "மஞ்சுளாதேவி", "manjuladevi": "மஞ்சுளாதேவி",
    "சங்கீதா": "Sangeetha", "sangeetha": "சங்கீதா",
    "விஸ்வேஸ்வர ரெட்டி": "Visweswara Reddy", "visweswara reddy": "விஸ்வேஸ்வர ரெட்டி",
    "விஸ்வேஸ்வர": "Visweswara", "visweswara": "விஸ்வேஸ்வர", "visvesvara": "விஸ்வேஸ்வர",
    "கார்த்திக்": "Karthik", "karthik": "கார்த்திக்",
    "பிரியா": "Priya", "priya": "பிரியா",
    "அக்னி": "Agni", "agni": "அக்னி",
    "ஸ்னேகா": "Sneha", "ஸ்நேகா": "Sneha", "சினேகா": "Sneha", "சிநேகா": "Sneha",
    "sneha": "ஸ்னேகா", "snago": "Sneha",
    "பிரகாஷ்": "Prakash", "பிரகாஷ": "Prakash", "பிரகாசம்": "Prakasam",
    "prakash": "பிரகாஷ்", "piragaash": "Prakash", "piragash": "Prakash",
    "உத்ரா": "Uthra", "uthra": "உத்ரா", "uthraa": "உத்ரா",
    "பிரபு": "Prabhu", "prabhu": "பிரபு",
    "பிரசாத்": "Prasad", "prasad": "பிரசாத்",
    "பிரதீப்": "Pradeep", "pradeep": "பிரதீப்",
    "பிரவீன்": "Praveen", "praveen": "பிரவீன்",
    "ஊர்மிளா": "Urmila", "urmila": "ஊர்மிளா",
    "ராவ்": "Rao", "rao": "ராவ்",
    "பத்தினி": "Bathini", "bathini": "பத்தினி",

    # Bank, Finance & Institutional Word Mappings
    "கோட்டக்": "Kotak", "கோடக்": "Kotak", "கொட்டக்": "Kotak", "kotak": "கோட்டக்",
    "மேகந்திரா": "Mahindra", "மகிந்திரா": "Mahindra", "மகேந்திரா": "Mahindra", "mahindra": "மகிந்திரா",
    "பாங்க்": "Bank", "பேங்க்": "Bank", "பாங்கு": "Bank", "வங்கி": "Bank", "bank": "பாங்க்",
    "லட்சுமி": "Lakshmi", "லஷ்மி": "Lakshmi", "லட்ஸுமி": "Lakshmi", "lakshmi": "லட்சுமி",
    "ஜெனரல்": "General", "ஜெனறல்": "General", "general": "ஜெனரல்",
    "பைனான்ஸ்": "Finance", "பினான்ஸ்": "Finance", "finance": "பைனான்ஸ்",
    "சிரையில்": "Siraiyil", "சிறையில்": "Siraiyil", "siraiyil": "சிரையில்",
    "ஷெரின்": "Sherin", "sherin": "ஷெரின்",
    "ஷ்ரைன்": "Shrine", "shrine": "ஷ்ரைன்",
    "வேளாங்கன்னி": "Velankanni", "வேளாங்கண்ணி": "Velankanni", "velankanni": "வேளாங்கன்னி",
    "சீனியர்": "Senior", "சினியர்": "Senior", "senior": "சீனியர்",
    "செகண்டரி": "Secondary", "செகன்டரி": "Secondary", "செகஸ்டரி": "Secondary", "செகஸ்தரி": "Secondary", "செகேன்டரி": "Secondary", "secondary": "செகண்டரி",
    "ஸ்கூல்": "School", "ஸகூல்": "School", "school": "ஸ்கூல்",
    "மெசர்ஸ்": "M/s.", "மெஸர்ஸ்": "M/s.", "மெஸ்ர்ஸ்": "M/s.",

    # Biblical / English "za" names
    "எலிசபத்": "Elizabeth", "elizabeth": "எலிசபத்",
    "எலிசபெத்": "Elizabeth", "elisabeth": "எலிசபத்",
    "எலிஸபத்": "Elizabeth", "எலிஸபெத்": "Elizabeth",
    "எலிசா": "Eliza", "eliza": "எலிசா",
    "எலிஸா": "Eliza",
    "லிசா": "Liza", "liza": "லிசா",
    "லிஸா": "Liza",

    # Arabic / Persian / Urdu / Indian "za" names
    "மிர்சா": "Mirza", "மிர்ஸா": "Mirza", "மிர்ஜா": "Mirza", "mirza": "மிர்சா",
    "ஹம்சா": "Hamza", "ஹம்ஸா": "Hamza", "ஹம்ஜா": "Hamza", "hamza": "ஹம்சா",
    "பைசல்": "Faizal", "பைஸல்": "Faizal", "ஃபைசல்": "Faizal", "ஃபைஸல்": "Faizal", "faizal": "பைசல்", "faisal": "பைசல்",
    "ரசா": "Raza", "ரஸா": "Raza", "ரஜா": "Raza", "raza": "ரசா",
    "ரசாக்": "Razak", "ரஸாக்": "Razak", "ரஜாக்": "Razak", "razak": "ரசாக்", "razaak": "ரசாக்",
    "அப்துல் ரசாக்": "Abdul Razak", "abdul razak": "அப்துல் ரசாக்",
    "பர்சானா": "Farzana", "ஃபர்சானா": "Farzana", "ஃபர்ஸானா": "Farzana", "farzana": "ஃபர்சானா",
    "ஜாகிர்": "Zakir", "சாகிர்": "Zakir", "ஸாகிர்": "Zakir", "zakir": "ஜாகிர்",
    "ஜமீர்": "Zameer", "சமீர்": "Zamir", "ஸமீர்": "Zameer", "zameer": "ஜமீர்", "zamir": "ஜமீர்",
    "ஜாஹிர்": "Zahir", "ஜாகீர்": "Zaheer", "ஸாஹிர்": "Zahir", "zahir": "ஜாஹிர்", "zaheer": "ஜாஹிர்",
    "ரியாஸ்": "Riyaz", "ரியாஜ்": "Riyaz", "riyaz": "ரியாஸ்", "riaz": "ரியாஸ்",
    "பெரோஸ்": "Feroz", "பிரோஸ்": "Feroz", "ஃபிரோஸ்": "Feroz", "ஃபிரோஜ்": "Feroz", "feroz": "பெரோஸ்", "feroze": "பெரோஸ்",
    "அஜீஸ்": "Aziz", "அஸீஸ்": "Aziz", "அசிஸ்": "Aziz", "aziz": "அஜீஸ்", "azeez": "அஜீஸ்",
    "அப்துல் அஜீஸ்": "Abdul Aziz", "abdul aziz": "அப்துல் அஜீஸ்",
    "அசார்": "Azhar", "அஸ்ஹர்": "Azhar", "அஜ்ஹர்": "Azhar", "azhar": "அசார்",
    "நசீர்": "Nazeer", "நஸீர்": "Nazeer", "நஜீர்": "Nazeer", "nazeer": "நசீர்", "nazir": "நசீர்",
    "நஜீர் அகமது": "Nazeer Ahamed", "nazeer ahamed": "நஜீர் அகமது",
    "நசீர் அகமது": "Nazeer Ahamed", "நசீர் அஹமது": "Nazeer Ahamed",
    "அகமது": "Ahamed", "அஹமது": "Ahamed", "ahamed": "அகமது", "ahmed": "அகமது",
    "ஜைனப்": "Zainab", "சைனப்": "Zainab", "ஸைனப்": "Zainab", "zainab": "ஜைனப்",
    "ஜுபைதா": "Zubaida", "சுபைதா": "Zubaida", "ஸுபைதா": "Zubaida", "zubaida": "ஜுபைதா", "zubeida": "ஜுபைதா",
    "நாசியா": "Nazia", "நாஸியா": "Nazia", "நாஜியா": "Nazia", "nazia": "நாசியா",
    "மும்தாஜ்": "Mumtaz", "மும்தாஸ்": "Mumtaz", "mumtaz": "மும்தாஜ்",
    "நவாஸ்": "Nawaz", "நவாஜ்": "Nawaz", "nawaz": "நவாஸ்",
    "ஷாநவாஸ்": "Shahnawaz", "ஷாநவாஜ்": "Shahnawaz", "shahnawaz": "ஷாநவாஸ்",
    "ஷாசாத்": "Shahzad", "ஷாஸாத்": "Shahzad", "ஷாஜாத்": "Shahzad", "shahzad": "ஷாசாத்",
    "இம்தியாஸ்": "Imtiaz", "இம்தியாஜ்": "Imtiaz", "imtiaz": "இம்தியாஸ்", "imtiyaz": "இம்தியாஸ்",
    "அயாஸ்": "Ayaz", "அயாஜ்": "Ayaz", "ayaz": "அயாஸ்",
    "சர்பராஸ்": "Sarfaraz", "சர்பராஜ்": "Sarfaraz", "sarfaraz": "சர்பராஸ்",
    "பர்வேஸ்": "Parvez", "பர்வேஜ்": "Parvez", "parvez": "பர்வேஸ்", "pervez": "பர்வேஸ்",
    "ஜாபர்": "Zafar", "சபார்": "Zafar", "ஸாபர்": "Zafar", "zafar": "ஜாபர்",
    "ஜியா": "Zia", "ஸியா": "Zia", "zia": "ஜியா", "ziya": "ஜியா",
    "முசாபர்": "Muzaffar", "முஸாஃபர்": "Muzaffar", "முஜாபர்": "Muzaffar", "muzaffar": "முசாபர்",

    # Additional Indian names & EC party names
    "நீத்து": "Neetu", "neetu": "நீத்து", "நீது": "Neetu", "neethu": "நீத்து",
    "ஹிந்துஜா": "Hinduja", "hinduja": "ஹிந்துஜா", "இந்துஜா": "Hinduja",
    "நீத்து எம். ஹிந்துஜா": "Neetu M. Hinduja", "neetu m. hinduja": "நீத்து எம். ஹிந்துஜா",
    "neetu.m. hinduja": "நீத்து எம். ஹிந்துஜா", "neetu m hinduja": "நீத்து எம். ஹிந்துஜா",
    "மனோகர்லால்": "Manoharlal", "manoharlal": "மனோகர்லால்",
    "மனோகர்லால் இந்துஜா": "Manoharlal Hinduja", "manogarlaal inthujaa": "Manoharlal Hinduja",
    "மனொகர்லால் இன்துஜா": "Manoharlal Hinduja", "manogarlal hinduja": "மனோகர்லால் இந்துஜா",
    "ஜாண்": "John", "ஜான்": "John", "ஜொஹ்ன்": "John", "john": "ஜான்",
    "பாப்டிஸ்ட்": "Baptist", "பப்டிஸ்ட்": "Baptist", "baptist": "பாப்டிஸ்ட்",
    "லஸ்ராடோ": "Lasrado", "லஸ்ரடொ": "Lasrado", "லஸ்ரடோ": "Lasrado", "lasrado": "லஸ்ராடோ", "lasardo": "லஸ்ராடோ",
    "பிளேவி": "Flavy", "ப்லவ்ய்": "Flavy", "flavy": "பிளேவி",
    "டெய்சி": "Daisy", "டைஸ்ய்": "Daisy", "daisy": "டெய்சி",
}

REAL_ESTATE_TERMS = {
    # Directions
    "வடக்கில்": "North", "வடக்கு": "North", "north": "வடக்கு",
    "தெற்கில்": "South", "தெற்கு": "South", "south": "தெற்கு",
    "கிழக்கில்": "East", "கிழக்கு": "East", "east": "கிழக்கு",
    "மேற்கில்": "West", "மேற்கு": "West", "west": "மேற்கு",

    # Property details
    "மனை": "Plot / Site", "plot": "மனை",
    "எண்": "No.", "number": "எண்",
    "புல": "Survey", "survey": "சர்வே / புல",
    "சர்வே": "Survey",
    "சொத்து": "Property", "சொத்து": "Property", "property": "சொத்து",
    "விவரம்": "Details", "விவரங்கள்": "Details", "details": "விவரங்கள்",
    "கிராமம்": "Village", "village": "கிராமம்",
    "வட்டம்": "Taluk", "taluk": "வட்டம்",
    "மாவட்டம்": "District", "district": "மாவட்டம்",
    "ஆவணம்": "Document / Deed", "document": "ஆவணம்",
    "சார்பதிவாளர்": "Sub-Registrar", "sub": "சார்", "registrar": "பதிவாளர்",
    "அலுவலகம்": "Office", "office": "அலுவலகம்",
    "நாள்": "Date", "date": "நாள்",
    "தேடுதல்": "Search", "search": "தேடுதல்",
    "காலம்": "Period", "period": "காலம்",
    "விஸ்தீரணம்": "Extent", "பரப்பு": "Extent", "extent": "விஸ்தீரணம் / பரப்பு",
    "கைமாற்றுத்": "Consideration", "consideration": "கைமாற்றுத் தொகை",
    "தொகை": "Amount", "தொகை": "Amount", "amount": "தொகை", "value": "மதிப்பு",
    "சந்தை": "Market", "market": "சந்தை",
    "மதிப்பு": "Value",
    "முந்தைய": "Prior", "prior": "முந்தைய",
    "குறிப்புகள்": "Remarks", "remarks": "குறிப்புகள்",
    "தான": "Gift", "gift": "தானம்",
    "செட்டில்மெண்ட்": "Settlement", "settlement": "செட்டில்மெண்ட்",
    "கிரையப்": "Sale", "கிரையம்": "Sale", "sale": "கிரையம்", "conveyance": "கிரையப் பத்திரம்",
    "பத்திரம்": "Deed", "deed": "பத்திரம்",
    "வில்லங்கம்": "Encumbrance", "encumbrance": "வில்லங்கம்",
    "சான்றிதழ்": "Certificate", "சான்று": "Certificate", "certificate": "சான்றிதழ்",
    "படிவம்": "Form", "form": "படிவம்",
    "உரிமையாளர்": "Owner", "owner": "உரிமையாளர்",
    "பரிவர்த்தனை": "Transaction", "transaction": "பரிவர்த்தனை",
    "பரிவர்த்தனைகள்": "Transactions", "transactions": "பரிவர்த்தனைகள்",
    "எழுதி": "Executed",
    "கொடுத்தவர்": "Executant", "கொடுத்தவர்": "Executant", "executant": "எழுதிக் கொடுத்தவர்", "executants": "எழுதிக் கொடுத்தவர்கள்",
    "வாங்கியவர்": "Claimant", "claimant": "எழுதி வாங்கியவர்", "claimants": "எழுதி வாங்கியவர்கள்",
    "அடுக்குமாடி": "Apartment / Flat", "flat": "அடுக்குமாடி குடியிருப்பு",
    "குடியிருப்பு": "Residential", "residential": "குடியிருப்பு",
    "கதவு": "Door", "door": "கதவு",
    "புதிய": "New", "new": "புதிய",
    "பழைய": "Old", "old": "பழைய",
    "பிளாக்": "Block", "block": "பிளாக்",
    "தெரு": "Street", "street": "தெரு",
    "சாலை": "Road", "road": "சாலை",
    "நகரம்": "Town", "town": "நகரம்",
    "சதுரடி": "Sq. Ft", "sqft": "சதுரடி", "sq.ft": "சதுரடி",
    "சதுர": "Square", "square": "சதுர",
    "மீட்டர்": "Meter", "meter": "மீட்டர்",
    "சென்ட்": "Cent", "cent": "சென்ட்",
    "ஏக்கர்": "Acre", "acre": "ஏக்கர்",
    "அடமானம்": "Mortgage", "mortgage": "அடமானம்",
    "விடுதலை": "Release", "release": "விடுதலை",
    "பாகப்பிரிவினை": "Partition", "partition": "பாகப்பிரிவினை",
    "அதிகாரப்": "Power of", "power": "அதிகாரம்", "attorney": "முகவர் / பத்திரம்",
    "அரசு": "Government", "government": "அரசு",
    "பதிவு": "Registration", "registration": "பதிவு",
    "துறை": "Department", "department": "துறை",
    "வங்கி": "Bank", "bank": "வங்கி",
    "பேங்க்": "Bank", "ேபங்க்": "Bank", "ெபங்க்": "Bank", "பெங்க்": "Bank",
    "கடன்": "Loan", "loan": "கடன்",
    "இன்மை": "Nil", "nil": "இன்மை",

    # Common institution/company words -- these recur constantly in
    # executant/claimant names (banks, employers, government corporations)
    # across every EC. Without a dictionary hit each one used to fall
    # through to the raw phonetic engine word-by-word and come out as
    # unreadable, meaningless syllables (e.g. "Industrial" -> a bare vowel
    # sign with nothing to attach to). These are real Tamil words, not
    # phonetic guesses, so the bilingual pairing actually carries meaning.
    "industrial": "தொழில்துறை", "investment": "முதலீடு",
    "corporation": "கழகம்", "limited": "லிமிடெட்",
    "employees": "ஊழியர்கள்", "employee": "ஊழியர்",
    "provident": "வருங்கால", "fund": "நிதி",
    "chartered": "சார்டர்டு", "standard": "ஸ்டாண்டர்ட்",
    "deposit": "வைப்பு", "deposits": "வைப்புகள்",
    "lessee": "குத்தகைக்கு எடுத்தவர்", "lessor": "குத்தகைக்கு விட்டவர்",
    "lessees": "குத்தகைக்கு எடுத்தவர்கள்", "lessors": "குத்தகைக்கு விட்டவர்கள்",
    "குத்தகைக்கு விட்டவர்": "Lessor", "குத்தகைக்கு விட்டவர்கள்": "Lessors",
    "குத்தகை கொடுப்பவர்": "Lessor", "குத்தகை கொடுத்தவர்": "Lessor",
    "குத்தகைக்கு எடுத்தவர்": "Lessee", "குத்தகைக்கு எடுத்தவர்கள்": "Lessees",
    "குத்தகைதாரர்": "Lessee", "குத்தகைதாரர்கள்": "Lessees",
    "lease": "குத்தகை", "insurance": "காப்பீடு",
    "industries": "தொழில்கள்", "private": "தனியார்",
    "public": "பொது", "services": "சேவைகள்", "service": "சேவை",

    # Administrative and Jurisdiction terms
    "taluk": "வட்டம்",
    "district": "மாவட்டம்",
    "village": "கிராமம்",
    "jurisdiction": "எல்லை",
    "sro": "சார்பதிவாளர் அலுவலகம்",
    "sub-registrar": "சார்பதிவாளர்",
    "sub registrar": "சார்பதிவாளர்",
    "office": "அலுவலகம்",
    "zone": "மண்டலம்",
    "south": "தெற்கு",
    "north": "வடக்கு",
    "central": "மத்தி",
    "chennai south": "சென்னை தெற்கு",
    "chennai north": "சென்னை வடக்கு",
    "chennai central": "சென்னை மத்தி",
    "adayar": "அடையாறு",
    "adyar": "அடையாறு",
    "guindy": "கிண்டி",
    "mylapore": "மயிலாப்பூர்",
    "velachery": "வேளச்சேரி",
    "thiruvarur": "திருவாரூர்",
    "coimbatore": "கோயம்புத்தூர்",
    "madurai": "மதுரை",
    "salem": "சேலம்",
    "tirunelveli": "திருநெல்வேலி",
    "thoothukudi": "தூத்துக்குடி",
}


# ---------------------------------------------------------------------------
# English → Tamil phonetic transliteration tables
# ---------------------------------------------------------------------------

# Multi-char cluster → Tamil (checked longest-first)
_EN_TA_MULTI: list[tuple[str, str]] = [
    # Vowel clusters (order: longest first)
    ("oo",  "ூ"),  ("ee",  "ீ"),  ("ai",  "ை"),  ("au",  "ௌ"),
    ("ou",  "ௌ"),  ("aa",  "ா"),  ("ae",  "ை"),
    # Consonant clusters
    ("ksh", "க்ஷ"), ("thr", "த்ர"), ("shr", "ஷ்ர"),
    ("sh",  "ஷ"),  ("ch",  "ச"),  ("ng",  "ங"),   ("ny",  "ஞ"),
    ("nh",  "ஞ"),  ("zh",  "ழ"),  ("th",  "த"),   ("ph",  "ப"),
    ("gh",  "க"),  ("kh",  "க"),  ("bh",  "ப"),   ("dh",  "த"),
    ("jh",  "ஜ"),  ("ck",  "க்க"), ("tt",  "ட்ட"), ("ll",  "ல்ல"),
    ("nn",  "ண்ண"), ("mm",  "ம்ம"), ("rr",  "ற்ற"), ("ss",  "ஸ்ஸ"),
    ("pp",  "ப்ப"), ("bb",  "ப்ப"), ("dd",  "ட்ட"), ("ff",  "ப்"),
    # Indian nasal + dental combinations
    ("ndu", "ந்து"), ("nda", "ந்தா"), ("ndi", "ந்தி"), ("nde", "ந்தே"),
    ("nd",  "ந்த்"), ("nth", "ந்த்"), ("nt",  "ந்த்"),
    ("thu", "த்து"), ("thi", "தி"),  ("tha", "தா"),  ("the", "தே"),
]

# Single char → Tamil consonant (no inherent vowel added separately)
_EN_TA_SINGLE_CONS: dict[str, str] = {
    'k': 'க', 'g': 'க', 'c': 'க', 's': 'ஸ', 'z': 'ஸ',
    't': 'ட', 'd': 'ட', 'p': 'ப', 'b': 'ப', 'f': 'ப',
    'm': 'ம', 'n': 'ன', 'y': 'ய', 'r': 'ர', 'l': 'ல',
    'v': 'வ', 'w': 'வ', 'j': 'ஜ', 'h': 'ஹ', 'q': 'க',
    'x': 'க்ஸ',
}

# Single char → Tamil vowel sign (when following a consonant) or standalone vowel
_EN_TA_VOWEL_SIGN: dict[str, str] = {
    'a': 'அ', 'i': 'இ', 'u': 'உ', 'e': 'எ', 'o': 'ஒ',
}
_EN_TA_VOWEL_DIAC: dict[str, str] = {
    'a': 'ா', 'i': 'ி', 'u': 'ு', 'e': 'ெ', 'o': 'ொ',
}

# Bare Tamil consonant letters (no virama) that a dependent vowel sign can
# legally attach to. Used by _phonetic_english_to_tamil to decide whether an
# incoming vowel should become a dependent matra (ெ, ி, ொ ...) or a standalone
# vowel letter (எ, இ, ஒ ...). Anything else sitting in out_chars[-1] -- a
# space, a digit, punctuation, or a consonant that already got its own virama
# (் ) -- is NOT a bare consonant, so a vowel right after it must be written
# as an independent vowel letter, never a bare matra with nothing to attach
# to (a bare matra like "ி" with no preceding consonant is not valid Tamil
# orthography and is exactly what produced the garbled "ின்டுஸ்ட்ரிஅல்" for
# "Industrial" when this function ran on a multi-word phrase -- every space
# was being misread as "a consonant is waiting for its vowel").
_TAMIL_BASE_CONSONANTS = {
    'க', 'ங', 'ச', 'ஞ', 'ட', 'ண', 'த', 'ந', 'ப', 'ம',
    'ய', 'ர', 'ல', 'வ', 'ழ', 'ள', 'ற', 'ன', 'ஜ', 'ஷ', 'ஸ', 'ஹ',
}



# --------------------------------------------------------------------------
# General Purpose Tamil Text Transliteration & Normalization Glossary
# --------------------------------------------------------------------------

BANK_AND_INSTITUTION_MAP = {
    # Standalone Bank terms & loanwords
    "பேங்க்": "Bank",
    "ேபங்க்": "Bank",
    "ெபங்க்": "Bank",
    "பெங்க்": "Bank",
    "வங்கி": "Bank",
    "ஐசிஐசிஐ பேங்க் லிமிடெட்": "ICICI Bank Limited",
    "ஐசிஐசிஐ பேங்க்": "ICICI Bank",
    "ஐசிஐசிஐ": "ICICI",
    "ஐ.சி.ஐ.சி.ஐ": "ICICI",
    "ஐ.சி.ஐ.சி.ஐ பேங்க்": "ICICI Bank",
    "ஐ.சி.ஐ.சி.ஐ பேங்க் லிமிடெட்": "ICICI Bank Limited",
    "icici பேங்க் லிமிடெட்": "ICICI Bank Limited",
    "icici பேங்க்": "ICICI Bank",
    "icici ேபங்க் லிமிடெட்": "ICICI Bank Limited",
    "icici ேபங்க்": "ICICI Bank",
    "பேங்க் ஆப் பரோடா": "Bank of Baroda",
    "ேபங்க் ஆப் பேராடா": "Bank of Baroda",
    "பேங்க் ஆப் பேராடா": "Bank of Baroda",
    "பேங்க் ஆப்": "Bank of",
    "ேபங்க் ஆப்": "Bank of",
    "பரோடா": "Baroda",
    "பேராடா": "Baroda",
    "பேங்க் ஆப் மகாராஷ்ட்ரா": "Bank of Maharashtra",
    "ேபங்க் ஆப் மகாராஷ்ட்ரா": "Bank of Maharashtra",
    "மகாராஷ்ட்ரா": "Maharashtra",
    "ரெப்கோ ஹோம் பைனான்ஸ்": "Repco Home Finance",
    "ெரப்ேகா ேஹாம் ைபனான்ஸ்": "Repco Home Finance",
    "ரெப்கோ": "Repco",
    "ெரப்ேகா": "Repco",
    "ஹோம் பைனான்ஸ்": "Home Finance",
    "ேஹாம் ைபனான்ஸ்": "Home Finance",
    "ஹோம்": "Home",
    "ேஹாம்": "Home",
    "பைனான்ஸ்": "Finance",
    "ைபனான்ஸ்": "Finance",
    "ஐடிபிஐ பேங்க்": "IDBI Bank",
    "ஐ.டி.பி.ஐ பேங்க்": "IDBI Bank",
    "ஐடிபிஐ ேபங்க்": "IDBI Bank",
    "ஐடிபிஐ": "IDBI Bank",
    "சிட்டி யூனியன் பேங்க் லிமிடெட்": "City Union Bank Limited",
    "சிட்டி யூனியன் பேங்க்": "City Union Bank",
    "ஸ்டேட் பேங்க் ஆப் இந்தியா": "State Bank of India",
    "இந்தியன் ஓவர்சீஸ் பேங்க்": "Indian Overseas Bank",
    "திவான் ஹவுசிங் பைனான்ஸ் கார்ப்பரேஷன் லிமிடெட்": "Dewan Housing Finance Corporation Limited (DHFL)",
    "திவான் ஹவுசிங்": "DHFL",
    "செங்கல்பட்டு கிளை": "Chengalpattu Branch",
    "ெசங்கல்பட்டு கிைள": "Chengalpattu Branch",
    "செங்கல்பட்டு": "Chengalpattu",
    "ெசங்கல்பட்டு": "Chengalpattu",
    "கிளை": "Branch",
    "கிைள": "Branch",
    "முதல்வர்": "Principal",
    "முகவர்": "Agent",
    "ஏஜெண்ட்": "Agent",
    "ஏெஜண்ட்": "Agent",
    "பிரின்சிபல்": "Principal",
    "பிரின்ஸ்பால்": "Principal",  # legacy misspelling, still recognized as input
    "விற்பனையாளர்": "Vendor",
    "வாங்குபவர்": "Purchaser",
    "கிரயப்பத்திரம்": "Sale Deed",
    "கிைரயப்பத்திரம்": "Sale Deed",
    "அடமானம்": "Mortgage",
    "ரசீது": "Receipt",
    "விடுதலை": "Discharge",
    "ரமேஷ்": "Ramesh",
    "ரேமஷ்": "Ramesh",
    "நதியா": "Nathiya",
    "சுரேஷ் குமார்": "Suresh Kumar",
    "சுேரஷ் குமார்": "Suresh Kumar",
    "தியாகராஜன்": "Thiyagarajan",
    "நஜீர் அகமது": "Najeer Ahamed",
    "நஜர்ீ அகமது": "Najeer Ahamed",
    "ஹாஜிரா பானு": "Hajira Banu",
    "தேவிமோகன்": "Devi Mohan",
    "ேதவிேமாகன்": "Devi Mohan",
    "தேவிமேகான்": "Devi Mohan",
    "ேதவிேமகான்": "Devi Mohan",
    "சாதிக் அலி": "Sadiq Ali",
    "விஜயலட்சுமி": "Vijayalakshmi",
    "லலிதா": "Lalitha",
}

INSTITUTIONAL_LOANWORDS_MAP = {
    # Ownership / incorporation type
    "பிரைவேட் லிமிடெட்": "Private Limited",
    "ப்ரைவேட் லிமிடெட்": "Private Limited",
    "பிரைேவட் லிமிடெட்": "Private Limited",
    "பிரைவேட்": "Private",
    "ப்ரைவேட்": "Private",
    "பிரைேவட்": "Private",
    "பப்ளிக் லிமிடெட்": "Public Limited",
    "பப்ளிக்": "Public",
    "லிமிடெட்": "Limited",
    "லிமிடட்": "Limited",
    "லிட்.": "Ltd.",
    "இன்கார்ப்பரேட்டட்": "Incorporated",
    "எல்.எல்.பி": "LLP",
    "எல்எல்பி": "LLP",

    # Firm / entity type
    "கம்பெனி": "Company",
    "கம்பனி": "Company",
    "கார்ப்பரேஷன்": "Corporation",
    "கார்ப்பொரேஷன்": "Corporation",
    "சொசைட்டி": "Society",
    "சொசைட்டீ": "Society",
    "கூட்டுறவு சங்கம்": "Co-operative Society",
    "ட்ரஸ்ட்": "Trust",
    "சாரிடபிள் ட்ரஸ்ட்": "Charitable Trust",
    "ஃபவுண்டேஷன்": "Foundation",
    "பவுண்டேஷன்": "Foundation",
    "ஃபெடரேஷன்": "Federation",
    "பெடரேஷன்": "Federation",
    "க்ரூப்": "Group",
    "கிரூப்": "Group",
    "போர்டு": "Board",
    "அத்தாரிட்டி": "Authority",
    "ஆதாரிட்டி": "Authority",

    # Department / function / commerce names
    "பிஸ்னஸ் & மேனேஜ்மெண்ட் சர்வீஸ்": "Business & Management Services",
    "பிஸ்னஸ் & மேனேஜ்மெண்ட் சர்வீசஸ்": "Business & Management Services",
    "பிசினஸ் & மேனேஜ்மெண்ட் சர்வீஸ்": "Business & Management Services",
    "பிசினஸ் & மேனேஜ்மெண்ட் சர்வீசஸ்": "Business & Management Services",
    "மேனேஜ்மெண்ட் சர்வீஸ்": "Management Services",
    "மேனேஜ்மெண்ட் சர்வீசஸ்": "Management Services",
    "மேனேஜ்மெண்ட்": "Management",
    "மேனேஜ்மென்ட்": "Management",
    "மேேனஜ்மெண்ட்": "Management",
    "மேேனஜ்மென்ட்": "Management",
    "பிஸ்னஸ்": "Business",
    "பிசினஸ்": "Business",
    "பிஸினஸ்": "Business",
    "வணிகம்": "Business",
    "சர்வீசஸ்": "Services",
    "சர்விசஸ்": "Services",
    "சர்வீஸ்": "Services",
    "சர்விஸ்": "Services",
    "இண்டஸ்ட்ரீஸ்": "Industries",
    "இண்டஸ்ட்ரிஸ்": "Industries",
    "எண்டர்பிரைசஸ்": "Enterprises",
    "எண்டர்பிரைஸ்": "Enterprise",
    "அசோசியேட்ஸ்": "Associates",
    "அசோஸியேட்ஸ்": "Associates",

    # Real-estate / construction firm types
    "எஸ்டேட்ஸ்": "Estates",
    "எஸ்டேட்": "Estate",
    "எஸ்டெட்ஸ்": "Estates",
    "பவுண்டேஷன்": "Foundation",
    "பவுண்டேஷன்ஸ்": "Foundations",
    "பவுண்டேசன்": "Foundation",
    "பவுன்டெஷன்": "Foundation",
    "டெவலப்பர்ஸ்": "Developers",
    "டெவலப்பர்": "Developer",
    "பில்டர்ஸ்": "Builders",
    "பில்டர்": "Builder",
    "புரமோட்டர்ஸ்": "Promoters",
    "புரமோட்டர்": "Promoter",
    "கன்ஸ்ட்ரக்ஷன்ஸ்": "Constructions",
    "கன்ஸ்ட்ரக்ஷன்": "Construction",
    "ரியல் எஸ்டேட்": "Real Estate",
    "ஹவுசிங்": "Housing",
    "ஹவுஸிங்": "Housing",

    # Finance / insurance sector
    "பேங்க்": "Bank",
    "ேபங்க்": "Bank",
    "வங்கி": "Bank",
    "ஃபைனான்ஸ்": "Finance",
    "இன்சூரன்ஸ்": "Insurance",
    "இன்ஷூரன்ஸ்": "Insurance",
    "மியூச்சுவல் ஃபண்ட்": "Mutual Fund",
    "சிட் ஃபண்ட்": "Chit Fund",
    "சிட்பண்ட்": "Chit Fund",
}

_INSTITUTIONAL_GLOSSARY_SORTED = sorted(
    {**BANK_AND_INSTITUTION_MAP, **INSTITUTIONAL_LOANWORDS_MAP}.items(),
    key=lambda kv: len(kv[0]),
    reverse=True,
)

_REVERSE_INSTITUTIONAL_MAP = {v.lower(): k for k, v in INSTITUTIONAL_LOANWORDS_MAP.items()}
_REVERSE_INSTITUTIONAL_MAP.update({
    "business": "பிஸ்னஸ்",
    "management": "மேனேஜ்மெண்ட்",
    "services": "சர்வீஸ்",
    "service": "சர்வீஸ்",
    "private": "பிரைவேட்",
    "limited": "லிமிடெட்",
    "private limited": "பிரைவேட் லிமிடெட்",
    "pvt ltd": "பிரைவேட் லிமிடெட்",
    "bank": "பேங்க்",
    "bank limited": "பேங்க் லிமிடெட்",
    "icici": "ICICI",
    "icici bank": "ICICI பேங்க்",
    "icici bank limited": "ICICI பேங்க் லிமிடெட்",
    "estates": "எஸ்டேட்ஸ்",
    "estate": "எஸ்டேட்",
    "foundation": "பவுண்டேஷன்",
    "foundations": "பவுண்டேஷன்ஸ்",
})


def normalize_tamil_visual_order(text: str) -> str:
    """
    Normalizes visual-order Tamil text into standard canonical logical-order Unicode Tamil.
    Idempotent.
    """
    if not text:
        return ""
    s = str(text)

    # 1. Composite "o"/"oo" vowels that arrive split across the consonant in visual order.
    # Must NOT be preceded by a consonant [க-ஹ] without virama, because [consonant] + ெ/ே
    # is already a complete canonical syllable (e.g. னே in ஸ்னேகா, மே in மேகா, ரே in ரேகா, தே in தேவா).
    s = re.sub(r'(?<![க-ஹ])ெ([க-ஹ])ா', r'\1ொ', s)
    s = re.sub(r'(?<![க-ஹ])ே([க-ஹ])ா', r'\1ோ', s)

    # 2. Any remaining pre-base vowel sign -- ெ ே ை only -- placed before its consonant
    s = re.sub(r'(?<![க-ஹ])([ெேை])([க-ஹ])', r'\2\1', s)

    # 3. Post-base vowel sign (ா-ௌ) that lands after a CONSONANT+VIRAMA pair
    s = re.sub(r'([க-ஹ])்([ா-ௌ])', r'\2\1்', s)

    return s


def _strip_stray_script_marks(s: str) -> str:
    """
    Strips leftover Tamil combining vowel signs / virama from English/Latin text
    so output is clean, pure English without hybrid Tamil characters.
    """
    if not s:
        return s
    has_latin = any('a' <= c.lower() <= 'z' for c in s)
    has_tamil = any('\u0b80' <= c <= '\u0bff' for c in s)
    if not (has_latin and has_tamil):
        return s
    # Strip Tamil combining marks attached directly to or adjacent to Latin letters
    cleaned = re.sub(r'(?<=[A-Za-z0-9])[\u0b82\u0bbe-\u0bcd\u0bd7]+', '', s)
    cleaned = re.sub(r'[\u0b82\u0bbe-\u0bcd\u0bd7]+(?=[A-Za-z0-9])', '', cleaned)
    # If whole Tamil base letters are still fused onto Latin text, separate with space
    cleaned = re.sub(r'(?<=[A-Za-z0-9])([\u0b80-\u0bff]+)', r' \1', cleaned)
    cleaned = re.sub(r'([\u0b80-\u0bff]+)(?=[A-Za-z0-9])', r'\1 ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned or s


def _apply_institutional_glossary(s: str) -> str:
    """
    Swap known bank/institution names and generic corporate loanwords
    (Private Limited, Management, Services, Business, ...) for English form.
    """
    if not s:
        return s
    for k, v in _INSTITUTIONAL_GLOSSARY_SORTED:
        if k in s:
            s = s.replace(k, v)
    return s


def clean_initials_and_dots(text: str) -> str:
    """
    Normalizes initials and periods in names:
    - Collapses multiple consecutive periods: '..' or '...' -> '.'
    - Uppercases initials: 'B.n.' -> 'B.N.', 'b.n.' -> 'B.N.', 't.g.' -> 'T.G.'
    - Ensures single dot on initials: 'G..' -> 'G.'
    - Ensures space between initials and following name: 'B.N.சுவாமி' -> 'B.N. சுவாமி'
    - Collapses duplicate Tamil vowel signs from OCR glitches: 'மேே' -> 'மே'
    """
    if not text:
        return text
    # 1. Collapse multiple consecutive periods and strip leading punctuation
    cleaned = re.sub(r'\.{2,}', '.', text)
    cleaned = re.sub(r'^\s*[\.\,\:\;]+\s*', '', cleaned)

    # 1b. Ensure space if an initial is glued onto a name with a dot e.g. "Neetu.m." -> "Neetu M."
    cleaned = re.sub(r'([A-Za-z]{2,})\.([A-Za-z])(?:\.|$|\s)', r'\1 \2. ', cleaned)

    # 2. Uppercase initials like B.n. or b.n. or G.
    def _fix_initials(m):
        return re.sub(r'([a-zA-Z])\.', lambda x: x.group(1).upper() + '.', m.group(0))
    cleaned = re.sub(r'\b(?:[A-Za-z]\.)+', _fix_initials, cleaned)

    # 3. Ensure a space between the trailing dot of initials and the start of a word/name
    cleaned = re.sub(r'(\b(?:[A-Z]\.)+)(?=[\u0b80-\u0bff]|[A-Za-z]{2,})', r'\1 ', cleaned)

    # 4. Collapse any repeated periods again if created
    cleaned = re.sub(r'\.{2,}', '.', cleaned)

    # 5. Separate டாக்டர். if followed immediately by a name: 'டாக்டர்.விஸ்வேஸ்வர' -> 'டாக்டர். விஸ்வேஸ்வர'
    cleaned = re.sub(r'(டாக்டர்\.)([^\s\.])', r'\1 \2', cleaned)

    # 6. Defense-in-depth: strip leftover Tamil combining marks glued onto Latin letters
    cleaned = _strip_stray_script_marks(cleaned)

    return cleaned.strip()


def dynamic_english_to_tamil(text: str) -> str:
    """
    Translates any English name/place to Tamil.
    Primary: Canonical and administrative dictionary lookup.
    Secondary: IndicTrans2 neural translation (accurate, context-aware).
    Fallback: Phonetic transliteration rules (always available).
    """
    word = (text or "").strip()
    if not word:
        return ""

    if word == "&":
        return "&"

    word = clean_initials_and_dots(word)

    # Translate Dr. to டாக்டர்.
    word = re.sub(r'\bdr\.?\s*', 'டாக்டர். ', word, flags=re.I)

    # If it's a pure initials block like "B.N." or "G." or "R.":
    # Keep as Latin initials since Tamil legal documents preserve Latin initials.
    if re.match(r'^(?:[A-Z]\.)+$', word, flags=re.I):
        return word.upper()

    # 1. Quick canonical and administrative dictionary lookup first (instant, accurate)
    lookup = (
        CANONICAL_PLACES.get(word.lower())
        or COMMON_NAMES.get(word.lower())
        or REAL_ESTATE_TERMS.get(word.lower())
        or _REVERSE_INSTITUTIONAL_MAP.get(word.lower())
    )
    if lookup and any('\u0b80' <= c <= '\u0bff' for c in lookup):
        return lookup

    # 1b. Multi-word phrases (institution names, org names, addresses): look
    # each word up against the same dictionaries individually before falling
    # back to phonetics for the whole phrase. A phrase like "Tamil Nadu
    # Industrial Investment Corporation" will rarely appear as one exact
    # dictionary entry, but "Tamil Nadu" and generic institutional words
    # often do -- resolving those correctly and only phoneticizing the
    # genuinely-unknown words (usually just proper nouns) gives a much more
    # readable result than phoneticizing the entire phrase from scratch.
    if ' ' in word:
        # Check if the whole phrase matches reverse institutional map
        phrase_lookup = _REVERSE_INSTITUTIONAL_MAP.get(word.lower())
        if phrase_lookup:
            return phrase_lookup
        # Drop bare English articles -- they have no Tamil equivalent worth
        # phoneticizing and official Tamil renderings of institution names
        # simply omit them (e.g. "The Tamilnadu Industrial ..." becomes
        # "தமிழ்நாடு தொழில்துறை ..."), so keeping "தெ" etc. only adds noise.
        _ARTICLES = {'the', 'a', 'an'}
        return " ".join(
            dynamic_english_to_tamil(w) for w in word.split(' ')
            if w and w.lower() not in _ARTICLES
        )

    # 2. Try IndicTrans2 neural translation (best quality)
    if _INDICTRANS2_IMPORTED and _it2_available():
        try:
            result = translate_to_tamil(word)
            # Reject results that still contain stray Latin letters mixed in —
            # a known failure mode of small distilled NMT models on proper
            # nouns, which can echo back part of the source script instead of
            # translating it. A clean en->ta result should be pure Tamil.
            if result and any('\u0b80' <= c <= '\u0bff' for c in result) and not any('a' <= c.lower() <= 'z' for c in result):
                logger.debug(f"IndicTrans2 en→ta: {word!r} → {result!r}")
                return result
            elif result:
                logger.warning(f"IndicTrans2 en→ta returned mixed-script output for {word!r}: {result!r} — falling back to phonetic")
        except Exception as e:
            logger.warning(f"IndicTrans2 en→ta failed for {word!r}: {e}")

    # 3. Phonetic fallback
    return _phonetic_english_to_tamil(word)


def _phonetic_english_to_tamil(text: str) -> str:
    """Pure phonetic rule-based English→Tamil transliteration (fallback)."""
    word = text.strip()
    if not word:
        return ""

    if word == "&":
        return "&"

    # Process word-by-word: the vowel-sign/vowel-letter decision below only
    # looks at the *immediately preceding* output character, so without this
    # split, the tail end of one word (often a space, or a dead consonant
    # ending in virama) bleeds into the vowel logic for the start of the
    # next word -- e.g. "Tamilnadu Industrial" would run together into one
    # continuous state machine and mis-transliterate "Industrial"'s leading
    # "I" as if it were attaching to whatever came right before the space.
    # Splitting here guarantees every word starts from a clean slate, so a
    # leading vowel is always rendered as an independent vowel letter.
    if ' ' in word:
        return " ".join(_phonetic_english_to_tamil(w) for w in word.split(' ') if w) 

    s = word.lower()
    out_chars: list[str] = []
    i = 0
    n = len(s)

    while i < n:
        # Try longest multi-char cluster first
        matched = False
        for cluster, ta in _EN_TA_MULTI:
            cl = len(cluster)
            if s[i:i+cl] == cluster:
                if cluster in ("oo", "ee", "ai", "au", "ou", "aa", "ae"):
                    if out_chars and out_chars[-1] in _TAMIL_BASE_CONSONANTS:
                        out_chars.append(ta)
                    else:
                        _STANDALONE = {"oo": "ஊ", "ee": "ஈ", "ai": "ஐ", "au": "ஔ", "ou": "ஔ", "aa": "ஆ", "ae": "ஐ"}
                        out_chars.append(_STANDALONE.get(cluster, ta))
                else:
                    out_chars.append(ta)
                i += cl
                matched = True
                break

        if matched:
            continue

        ch = s[i]

        if ch in _EN_TA_VOWEL_SIGN:
            if out_chars and out_chars[-1] in _TAMIL_BASE_CONSONANTS:
                if ch == 'a':
                    if i == n - 1:
                        # Trailing 'a' in Indian names (Hinduja, Deepa, Priya, Pooja, Sneha)
                        out_chars.append('ா')
                    else:
                        pass  # inherent 'a'
                else:
                    out_chars.append(_EN_TA_VOWEL_DIAC[ch])
            else:
                out_chars.append(_EN_TA_VOWEL_SIGN[ch])
            i += 1

        elif ch in _EN_TA_SINGLE_CONS:
            # Word-initial 'n' in Tamil is ALWAYS dental 'ந', never alveolar 'ன'
            if ch == 'n' and (i == 0 or (out_chars and out_chars[-1] not in _TAMIL_BASE_CONSONANTS and out_chars[-1] != '்')):
                ta_cons = 'ந'
            # 't' in Indian names before a vowel is dental 'த' (Neetu, Geeta, Sita, Anita)
            elif ch == 't' and (i == 0 or (i + 1 < n and s[i+1] in _EN_TA_VOWEL_SIGN)):
                # If followed by 'u' at end of word: 'த்து' (e.g. Neetu -> நீத்து)
                if i + 1 < n and s[i+1] == 'u' and i + 2 == n:
                    out_chars.append('த்து')
                    i += 2
                    continue
                ta_cons = 'த'
            else:
                ta_cons = _EN_TA_SINGLE_CONS[ch]

            # A consonant only stays "bare" (ready to take the next character
            # as a dependent vowel sign) when a vowel immediately follows it.
            # That includes end-of-word: an English word almost always ends
            # on the consonant *sound*, not "consonant + a" (e.g. "Investment"
            # ends on a dead 't', not "ta"), so a trailing consonant with
            # nothing after it needs a virama too.
            next_is_vowel = i + 1 < n and s[i+1] in _EN_TA_VOWEL_SIGN
            if next_is_vowel:
                out_chars.append(ta_cons)
            else:
                out_chars.append(ta_cons)
                out_chars.append('்')
            i += 1

        else:
            out_chars.append(ch)
            i += 1

    return "".join(out_chars)


def dynamic_transliterate_tamil(word: str) -> str:
    """
    Translates any Tamil word/phrase to English.
    Primary: IndicTrans2 neural translation.
    Fallback: Phonetic rule-based transliteration.
    """
    clean = (word or "").strip()
    if not clean:
        return ""

    # Normalize initials and multiple dots first
    clean = clean_initials_and_dots(clean)

    # Normalize visual order (moves misplaced pre-base vowels to post-base, idempotent)
    clean = normalize_tamil_visual_order(clean)

    # Translate டாக்டர் / டாக்டர். to Dr.
    clean = re.sub(r'\bடாக்டர்\.?\s*', 'Dr. ', clean)

    # Apply corporate / institutional loanword glossary (Private Limited, Management, Services, Business, etc.)
    clean = _apply_institutional_glossary(clean)

    # 1. Quick dictionary lookup for exact match
    if clean in COMMON_NAMES:
        return COMMON_NAMES[clean]
    if clean in CANONICAL_PLACES:
        return CANONICAL_PLACES[clean]
    if clean in REAL_ESTATE_TERMS:
        return REAL_ESTATE_TERMS[clean]

    # 1b. Multi-word phrases / initials + names:
    # If the string contains spaces or initials, split and resolve each token
    if ' ' in clean:
        tokens = clean.split(' ')
        translated_tokens = []
        for t in tokens:
            if not t:
                continue
            # If token is Latin initials like B.N. or G. or R.S.K., keep as-is
            if re.match(r'^(?:[A-Z]\.)+$', t, flags=re.I):
                translated_tokens.append(clean_initials_and_dots(t))
            elif re.match(r'^[A-Za-z0-9&/,\.\-]+$', t):
                # Already Latin/English or symbol (e.g. "Business", "&", "Private", "Limited")
                translated_tokens.append(t)
            elif t in COMMON_NAMES:
                translated_tokens.append(COMMON_NAMES[t])
            elif t in CANONICAL_PLACES:
                translated_tokens.append(CANONICAL_PLACES[t])
            elif t in REAL_ESTATE_TERMS:
                translated_tokens.append(REAL_ESTATE_TERMS[t])
            elif t in INSTITUTIONAL_LOANWORDS_MAP:
                translated_tokens.append(INSTITUTIONAL_LOANWORDS_MAP[t])
            else:
                # Transliterate individual token
                translated_tokens.append(_phonetic_tamil_to_english(t))
        result = " ".join(translated_tokens)
        return _strip_stray_script_marks(result)

    # 2. Try IndicTrans2 neural translation (best quality)
    if _INDICTRANS2_IMPORTED and _it2_available():
        try:
            result = translate_to_english(clean)
            # Reject results that still contain leftover Tamil script — a
            # known failure mode of small distilled NMT models on unfamiliar
            # proper nouns, which can echo back part of the source text
            # instead of transliterating it (e.g. "Vimalaathave" + stray "ல்").
            # A clean ta->en result should be pure Latin script.
            if result and any('a' <= c.lower() <= 'z' for c in result) and not any('\u0b80' <= c <= '\u0bff' for c in result):
                logger.debug(f"IndicTrans2 ta→en: {clean!r} → {result!r}")
                return result.strip().title()
            elif result:
                logger.warning(f"IndicTrans2 ta→en returned mixed-script output for {clean!r}: {result!r} — falling back to phonetic")
        except Exception as e:
            logger.warning(f"IndicTrans2 ta→en failed for {clean!r}: {e}")

    # 3. Phonetic fallback (deterministic, always produces pure Latin script)
    return _phonetic_tamil_to_english(clean)


def _phonetic_tamil_to_english(word: str) -> str:
    """Pure phonetic rule-based Tamil→English transliteration (fallback)."""
    clean = word.strip()
    chars = list(clean)
    out = []
    i = 0
    while i < len(chars):
        c = chars[i]
        if c in TAMIL_VOWELS:
            out.append(TAMIL_VOWELS[c])
            i += 1
        elif c in TAMIL_CONSONANTS:
            prev_is_nasal = (len(out) > 0 and out[-1] in ['ng', 'n', 'm', 'ny'])
            prev_is_vowel = (len(out) > 0 and any(out[-1].endswith(v) for v in ['a', 'aa', 'i', 'ee', 'u', 'oo', 'e', 'ai', 'o']))
            use_voiced = prev_is_nasal or (prev_is_vowel and c in ['ட', 'க'])
            cons = TAMIL_CONSONANTS[c][1] if use_voiced else TAMIL_CONSONANTS[c][0]
            if i + 1 < len(chars) and chars[i + 1] in TAMIL_VOWEL_SIGNS:
                v_sign = chars[i + 1]
                v_sound = TAMIL_VOWEL_SIGNS[v_sign]
                out.append(cons + v_sound)
                i += 2
            else:
                out.append(cons + 'a')
                i += 1
        elif c in TAMIL_VOWEL_SIGNS:
            # Orphaned or duplicate vowel sign with no preceding base consonant
            v_sound = TAMIL_VOWEL_SIGNS[c]
            if not (out and out[-1].endswith(v_sound)):
                out.append(v_sound)
            i += 1
        elif '\u0b80' <= c <= '\u0bff':
            # Other Tamil character (virama, aytham, etc.)
            i += 1
        else:
            out.append(c)
            i += 1

    res = "".join(out)
    res = re.sub(r'ngg', 'ng', res)
    res = re.sub(r'ee$', 'i', res)
    res = re.sub(r'aiyoor', 'aiyur', res)
    res = re.sub(r'oo$', 'ur', res)

    # Sound rules for Tamil-English names & loanwords
    res = re.sub(r'thevi\b', 'devi', res, flags=re.I)
    res = re.sub(r'thevee\b', 'devi', res, flags=re.I)
    res = re.sub(r'\bthevi', 'devi', res, flags=re.I)
    res = re.sub(r'\bmangaa\b', 'Manga', res, flags=re.I)
    res = re.sub(r'mangaathevi', 'Mangadevi', res, flags=re.I)
    res = re.sub(r'mangaadevi', 'Mangadevi', res, flags=re.I)
    res = re.sub(r'taagtar\b\.?', 'Dr.', res, flags=re.I)
    res = re.sub(r'taaktar\b\.?', 'Dr.', res, flags=re.I)
    res = re.sub(r'\btaagtar', 'Dr.', res, flags=re.I)
    res = re.sub(r'\btaaktar', 'Dr.', res, flags=re.I)
    res = re.sub(r'kirushna', 'krishna', res, flags=re.I)
    res = re.sub(r'mmaal\b', 'mmal', res, flags=re.I)
    res = re.sub(r'ammaal\b', 'ammal', res, flags=re.I)
    res = re.sub(r'\bmokan', 'mohan', res, flags=re.I)
    res = re.sub(r'mokan\b', 'mohan', res, flags=re.I)
    res = re.sub(r'\bmogan', 'mohan', res, flags=re.I)
    res = re.sub(r'mogan\b', 'mohan', res, flags=re.I)
    res = re.sub(r'\bsuvaa', 'swa', res, flags=re.I)
    res = re.sub(r'suvaami\b', 'swami', res, flags=re.I)
    res = re.sub(r'swaami\b', 'swami', res, flags=re.I)
    res = re.sub(r'\braamaanuja', 'ramanuja', res, flags=re.I)
    res = re.sub(r'\bpeng\b', 'Bank', res, flags=re.I)
    res = re.sub(r'\bpenk\b', 'Bank', res, flags=re.I)
    res = re.sub(r'\bneedu\b', 'Neetu', res, flags=re.I)
    res = re.sub(r'\bneethu\b', 'Neetu', res, flags=re.I)
    res = re.sub(r'\bhintuja\b', 'Hinduja', res, flags=re.I)
    res = re.sub(r'\bhintujaa\b', 'Hinduja', res, flags=re.I)
    res = re.sub(r'\binthuja\b', 'Hinduja', res, flags=re.I)
    res = re.sub(r'\binthujaa\b', 'Hinduja', res, flags=re.I)
    res = re.sub(r'\besteds\b', 'Estates', res, flags=re.I)
    res = re.sub(r'\bfoundatiosn\b', 'Foundations', res, flags=re.I)
    res = re.sub(r'\bpisnas\b', 'Business', res, flags=re.I)
    res = re.sub(r'\bpisinas\b', 'Business', res, flags=re.I)
    res = re.sub(r'\bpisnass\b', 'Business', res, flags=re.I)
    res = re.sub(r'\bsarvees\b', 'Services', res, flags=re.I)
    res = re.sub(r'\bsarvis\b', 'Services', res, flags=re.I)
    res = re.sub(r'\bpiraivad\b', 'Private', res, flags=re.I)
    res = re.sub(r'\bpiraivet\b', 'Private', res, flags=re.I)
    res = re.sub(r'\blimided\b', 'Limited', res, flags=re.I)
    res = re.sub(r'\blimidat\b', 'Limited', res, flags=re.I)
    res = re.sub(r'\bmenajmend\b', 'Management', res, flags=re.I)
    res = re.sub(r'\bmenejmend\b', 'Management', res, flags=re.I)
    res = re.sub(r'\belisapath\b', 'Elizabeth', res, flags=re.I)
    res = re.sub(r'\belisapeth\b', 'Elizabeth', res, flags=re.I)
    res = re.sub(r'\belisapat\b', 'Elizabeth', res, flags=re.I)
    res = re.sub(r'\belisaapath\b', 'Elizabeth', res, flags=re.I)
    res = re.sub(r'\belisaapeth\b', 'Elizabeth', res, flags=re.I)

    res = _strip_stray_script_marks(res)
    res = re.sub(r'[\u0b80-\u0bff]+', '', res)

    # Title-case each word properly without lowercasing initials like B.N.
    tokens = res.split()
    return " ".join(t if re.match(r'^(?:[A-Z]\.)+$', t) or t == '&' else t.capitalize() for t in tokens)


def format_bilingual_entity(text: str) -> str:
    """
    Formats any location/entity strictly as:
        English Name (Tamil Name)
    Handles:
        1. 'விழுப்புரம் (Villupuram)' -> 'Villupuram (விழுப்புரம்)'
        2. 'Villupuram (விழுப்புரம்)' -> 'Villupuram (விழுப்புரம்)'
        3. Pure Tamil: 'தஞ்சாவூர்' -> 'Thanjavur (தஞ்சாவூர்)'
        4. Pure English: 'Erode' -> 'Erode (ஈரோடு)'
    """
    if not text or text == "Not Detected":
        return "Not Detected"

    clean = text.strip()
    
    # Strip any residual label noise (e.g. '/ District')
    clean = re.sub(r'^[/:\-\s]*(?:district|taluk|village|revenue|மாவட்டம்|வட்டம்|கிராமம்)[/:\-\s]*', '', clean, flags=re.IGNORECASE).strip()
    if not clean:
        return "Not Detected"

    # Normalize visual order & repair known OCR dropped Kombu / typo entities
    clean = normalize_tamil_visual_order(clean)
    clean = re.sub(r'\b(?:சமெ்பாக்கம்|சம்பாக்கம்|ெசம்பாக்கம்)\b', 'செம்பாக்கம்', clean)
    clean = re.sub(r'\b(?:சங்கல்பட்டு|ெசங்கல்பட்டு)\b', 'செங்கல்பட்டு', clean)
    clean = re.sub(r'\bமராவட்டம்\b', 'மாவட்டம்', clean)

    # 1. Check if Tamil (English) e.g. 'விழுப்புரம் (Villupuram)'
    m1 = re.match(r'^([\u0b80-\u0bff\s,\./\-]+?)\s*\(([A-Za-z0-9\s,\./\-]+)\)$', clean)
    if m1:
        ta_part = m1.group(1).strip()
        en_part = m1.group(2).strip()
        ta_norm = CANONICAL_PLACES.get(en_part.lower()) or ta_part
        return f"{en_part} ({ta_norm})"

    # 2. Check if English (Tamil) e.g. 'Villupuram (விழுப்புரம்)'
    m2 = re.match(r'^([A-Za-z0-9\s,\./\-]+?)\s*\(([\u0b80-\u0bff\s,\./\-]+)\)$', clean)
    if m2:
        en_part = m2.group(1).strip()
        ta_part = m2.group(2).strip()
        if ta_part in CANONICAL_PLACES:
            en_part = CANONICAL_PLACES[ta_part]
        ta_norm = CANONICAL_PLACES.get(en_part.lower()) or ta_part
        return f"{en_part} ({ta_norm})"

    has_tamil = any('\u0b80' <= c <= '\u0bff' for c in clean)
    has_english = any('a' <= c.lower() <= 'z' for c in clean)

    if has_tamil and not has_english:
        en_val = (
            CANONICAL_PLACES.get(clean)
            or COMMON_NAMES.get(clean)
            or REAL_ESTATE_TERMS.get(clean)
            or dynamic_transliterate_tamil(clean)
        )
        # Restore canonical Tamil spelling if registered, avoiding raw OCR typo reproduction
        ta_canonical = (
            CANONICAL_PLACES.get(en_val.lower())
            or COMMON_NAMES.get(en_val.lower())
            or clean
        )
        return f"{en_val} ({ta_canonical})"
    elif has_english and not has_tamil:
        # Check whole phrase first
        ta_val = (
            CANONICAL_PLACES.get(clean.lower())
            or COMMON_NAMES.get(clean.lower())
            or REAL_ESTATE_TERMS.get(clean.lower())
        )
        if not ta_val:
            # Special handling for "X Taluk / Jurisdiction" or "X Taluk"
            m_taluk = re.match(r'^(.+?)\s+Taluk(?:\s*/\s*Jurisdiction)?$', clean, re.IGNORECASE)
            if m_taluk:
                base_place = m_taluk.group(1).strip()
                ta_place = dynamic_english_to_tamil(base_place)
                return f"{clean} ({ta_place} வட்டம்)"
            m_dist = re.match(r'^(.+?)\s+District$', clean, re.IGNORECASE)
            if m_dist:
                base_place = m_dist.group(1).strip()
                ta_place = dynamic_english_to_tamil(base_place)
                return f"{clean} ({ta_place} மாவட்டம்)"
            m_sro = re.match(r'^(.+?)\s+S\.?R\.?O\.?$', clean, re.IGNORECASE)
            if m_sro:
                base_place = m_sro.group(1).strip()
                ta_place = dynamic_english_to_tamil(base_place)
                return f"{clean} ({ta_place} சார்பதிவாளர் அலுவலகம்)"

            # Dynamically translate/transliterate words
            words = clean.split()
            ta_words = []
            for w in words:
                w_clean = re.sub(r'^[^\w]+|[^\w]+$', '', w)
                w_ta = (
                    CANONICAL_PLACES.get(w_clean.lower())
                    or COMMON_NAMES.get(w_clean.lower())
                    or REAL_ESTATE_TERMS.get(w_clean.lower())
                    or dynamic_english_to_tamil(w_clean)
                )
                ta_words.append(w_ta if w_ta else w)
            ta_val = " ".join(ta_words)
        return f"{clean} ({ta_val})" if ta_val else clean
    else:
        # Both scripts present without parens (e.g. "ICICI பேங்க் லிமிடெட்")
        en_val = dynamic_transliterate_tamil(clean)
        return f"{en_val} ({clean})" if en_val else clean

def format_bilingual_field_dict(raw_val: str) -> dict:
    """
    Formats any field value into structured { "english": "...", "tamil": "..." }
    for frontend key-value card rendering.
    """
    raw_s = str(raw_val).strip() if raw_val is not None else ""
    if not raw_s or raw_s in ("Not Detected", "None", "-"):
        return {"english": raw_s or "Not Detected", "tamil": raw_s or "கண்டறியப்படவில்லை"}

    formatted = format_bilingual_entity(raw_s)
    if not formatted or not isinstance(formatted, str):
        formatted = raw_s

    m = re.match(r'^(.*?)\s*\((.+?)\)$', formatted)
    if m:
        return {"english": m.group(1).strip(), "tamil": m.group(2).strip()}

    # Check if purely numbers or survey format
    if re.match(r'^[0-9A-Za-z/,\.\-\s]+$', raw_s) and not any('\u0b80' <= c <= '\u0bff' for c in raw_s):
        return {"english": raw_s, "tamil": raw_s}

    return {"english": formatted, "tamil": raw_s}


def format_bilingual_owner(raw_owner_str: str) -> str:
    """
    Translates and formats owner name(s) and kinship strictly as:
        English Name(s) (Tamil Name(s))
    """
    if not raw_owner_str or raw_owner_str == "Not Detected":
        return "Not Detected"

    clean_str = raw_owner_str.strip()

    # 1. Bilingual kinship lines:
    # e.g. "1. முத்துலட்சுமி (Muthulakshmi) கணவர் / Wife of இராமன் (Raman)"
    # e.g. "2. சந்தில்குமார் (Senthilkumar) மகன் / Son of இராமன் (Raman)"
    bi_pat = r'(\d+\.?\s*)?([^\(\n]+?)\s*\(([A-Za-z\s]+)\)\s*(?:(மகன்|மகள்|மனைவி|கணவர்)\s*/\s*)?(?:Son|Wife|Daughter|Husband)\s+of\s+([^\(\n]+?)\s*\(([A-Za-z\s]+)\)'
    bi_matches = list(re.finditer(bi_pat, clean_str, re.IGNORECASE))
    if bi_matches:
        results = []
        for m in bi_matches:
            prefix = m.group(1) or ""
            ta_owner = m.group(2).strip()
            en_owner = m.group(3).strip()
            ta_parent = m.group(5).strip()
            en_parent = m.group(6).strip()

            rel_text = m.group(0).lower()
            rel_en, rel_ta = ("S/o", "மகன்") if 'son' in rel_text or 'மகன்' in rel_text else (
                ("W/o", "மனைவி") if 'wife' in rel_text or 'மனைவி' in rel_text else (
                    ("D/o", "மகள்") if 'daughter' in rel_text or 'மகள்' in rel_text else ("H/o", "கணவர்")
                )
            )
            # In Tamil culture, wife of husband is "கணவர் [Husband]" or "[Husband] மனைவி"
            if 'கணவர்' in rel_text and 'wife of' in rel_text:
                rel_ta = "மனைவி"

            results.append(f"{en_owner} ({rel_en} {en_parent}) ({ta_parent} {rel_ta} {prefix}{ta_owner})")
        return ", ".join(results)

    # 2. Pure Tamil Kinship pattern: [Parent] (மகன்|மகள்|மனைவி|கணவர்) [Owner]
    ta_pat = r'([A-Za-z\u0b80-\u0bff]+)\s+(மகன்|மகள்|மனைவி|கணவர்)\s+([A-Za-z\u0b80-\u0bff]+)'
    ta_matches = list(re.finditer(ta_pat, clean_str))
    if ta_matches:
        results = []
        for m in ta_matches:
            ta_parent = m.group(1).strip()
            ta_rel = m.group(2).strip()
            ta_owner = m.group(3).strip()

            rel_en = "S/o" if ta_rel == "மகன்" else (
                "W/o" if ta_rel == "மனைவி" else (
                    "D/o" if ta_rel == "மகள்" else "H/o"
                )
            )
            en_parent = CANONICAL_PLACES.get(ta_parent) or COMMON_NAMES.get(ta_parent) or dynamic_transliterate_tamil(ta_parent)
            en_owner = CANONICAL_PLACES.get(ta_owner) or COMMON_NAMES.get(ta_owner) or dynamic_transliterate_tamil(ta_owner)

            results.append(f"{en_owner}, {rel_en} {en_parent} ({ta_parent} {ta_rel} {ta_owner})")
        return ", ".join(results)

    # 3. English Kinship / Legal Heirs pattern
    en_pat = r'([A-Za-z\s]+?)\s*(?:,\s*|\s+)(?:(Son of|Wife of|Daughter of|Husband of|W/o|S/o|D/o))\s+(?:Late\s+)?([A-Za-z\s]+)'
    en_matches = list(re.finditer(en_pat, clean_str, re.IGNORECASE))
    if en_matches:
        results = []
        seen = set()
        for m in en_matches:
            p_name = m.group(1).strip()
            rel_raw = m.group(2).strip().lower()
            parent = re.sub(r'\(Legal.*$', '', m.group(3), flags=re.IGNORECASE).strip()
            if p_name.lower() in seen or len(p_name) < 2:
                continue
            seen.add(p_name.lower())

            rel_en = 'W/o' if 'wife' in rel_raw or 'w/o' in rel_raw else (
                'S/o' if 'son' in rel_raw or 's/o' in rel_raw else (
                    'D/o' if 'daughter' in rel_raw or 'd/o' in rel_raw else 'H/o'
                )
            )
            rel_ta = 'மனைவி' if rel_en == 'W/o' else ('மகன்' if rel_en == 'S/o' else ('மகள்' if rel_en == 'D/o' else 'கணவர்'))
            late = "Late " if "late" in clean_str.lower() else ""

            # Tamil equivalents: look up in dict or transliterate dynamically
            def _en_to_ta(name: str) -> str:
                looked = COMMON_NAMES.get(name.lower())
                if looked:
                    return looked
                # word-by-word transliteration
                return " ".join(dynamic_english_to_tamil(w) for w in name.split())

            ta_name = _en_to_ta(p_name)
            ta_parent_name = _en_to_ta(parent)

            rel_ta_label = f"{ta_parent_name} {rel_ta} {ta_name}"
            results.append(f"{p_name} ({rel_en} {late}{parent}) ({rel_ta_label})")

        if results:
            suffix = " — all legal heirs" if "legal heir" in clean_str.lower() else ""
            return ", ".join(results) + suffix

    return format_bilingual_entity(clean_str)


def translate_word_bilingual(word: str) -> str:
    """
    Translates a single word or token dynamically:
    - If Tamil word: translates to English (e.g. வடக்கில் -> North, மனை -> Plot, கிராமம் -> Village)
    - If English word: translates to Tamil (e.g. Property -> சொத்து, Village -> கிராமம்)
    """
    if not word:
        return ""
    clean = re.sub(r'^[^\w\u0b80-\u0bff]+|[^\w\u0b80-\u0bff]+$', '', word).strip()
    if not clean or clean.isdigit() or (len(clean) <= 1 and not ('\u0b80' <= clean <= '\u0bff')):
        return ""

    c_low = clean.lower()
    # 1. Check real estate dictionary
    if clean in REAL_ESTATE_TERMS:
        return REAL_ESTATE_TERMS[clean]
    if c_low in REAL_ESTATE_TERMS:
        return REAL_ESTATE_TERMS[c_low]

    # 2. Check canonical places / common names
    if clean in CANONICAL_PLACES:
        return CANONICAL_PLACES[clean]
    if c_low in CANONICAL_PLACES:
        return CANONICAL_PLACES[c_low]
    if clean in COMMON_NAMES:
        return COMMON_NAMES[clean]
    if c_low in COMMON_NAMES:
        return COMMON_NAMES[c_low]

    # 3. Dynamic translation/transliteration
    has_tamil = any('\u0b80' <= c <= '\u0bff' for c in clean)
    has_english = any('a' <= c.lower() <= 'z' for c in clean)

    if has_tamil:
        return dynamic_transliterate_tamil(clean)
    elif has_english:
        return dynamic_english_to_tamil(clean)

    return ""





def transliterate_tamil_text(text: str, normalize: bool = True) -> str:
    """
    Translates or transliterates any Tamil text into natural English.
    Used by PDF generators, reports, and export engines to ensure zero blank tokens.

    Args:
        normalize: whether to run normalize_tamil_visual_order() on the input
            first. Leave this True (default) for raw text you haven't already
            normalized. Pass False if the caller already normalized this exact
            text upstream (e.g. at PDF-extraction time) — normalizing twice
            will scramble already-correct text, since the transform is
            directional and not idempotent.
    """
    if not text or text == "-":
        return text or "-"
    raw = str(text)

    # Run the glossary pass on the raw text *before* normalization too.
    # Field values reach this function in two different shapes depending on
    # their source: raw pdfplumber extraction from the affected SRO PDFs
    # (genuinely visual-order, needs normalize_tamil_visual_order to become
    # matchable), vs. LLM-extracted or hand-authored fields that already use
    # correct canonical-order Unicode Tamil (for which running
    # normalize_tamil_visual_order would incorrectly scramble known-good
    # spellings before the glossary ever gets to see them, since that
    # transform assumes its input is always visual-order). Matching on the
    # raw text first catches the canonical-order case; the second pass below
    # (after normalization) catches the genuine visual-order case. Institution
    # names are unambiguous multi-character strings, so running this twice
    # carries no risk of a false match.
    s = _apply_institutional_glossary(raw)
    s = normalize_tamil_visual_order(s) if normalize else s
    if not any('\u0b80' <= c <= '\u0bff' for c in s):
        return s

    # 1. Glossary pass again, now against normalized text (covers real
    #    visual-order OCR input, which only matches after normalization).
    s = _apply_institutional_glossary(s)

    # 2. Transliterate remaining Tamil tokens (input is already normalized above,
    #    so do NOT re-normalize each token here — that would scramble it again).
    def _trans_match(m):
        tok = m.group(0)
        if tok in BANK_AND_INSTITUTION_MAP:
            return BANK_AND_INSTITUTION_MAP[tok]
        if tok in INSTITUTIONAL_LOANWORDS_MAP:
            return INSTITUTIONAL_LOANWORDS_MAP[tok]
        return dynamic_transliterate_tamil(tok)

    s = re.sub(r'[\u0b80-\u0bff]+', _trans_match, s)
    s = re.sub(r'\s+', ' ', s).strip()
    # Defense-in-depth: never let a stray combining mark leak into the output.
    s = _strip_stray_script_marks(s)
    return s


# ---------------------------------------------------------------------------
# Deep Translator Integration for Sentences, Remarks, and Legal Clauses
# ---------------------------------------------------------------------------

_DEEP_TRANS_CACHE: dict[str, str] = {}

def translate_legal_phrase_deeptranslator(text: str, source: str = "ta", target: str = "en") -> str:
    """
    Translates whole sentences, boundaries, and legal remarks using deep_translator / Google GTX
    with high accuracy, while strictly respecting the legal and revenue place glossaries.
    """
    if not text or text == "-":
        return text or "-"

    raw = str(text).strip()
    cache_key = f"{source}->{target}::{raw}"
    if cache_key in _DEEP_TRANS_CACHE:
        return _DEEP_TRANS_CACHE[cache_key]

    # Pre-apply institutional & revenue glossary before translating
    s = _apply_institutional_glossary(raw)

    # Check whole dictionary hit first
    if source == "ta" and target == "en":
        if s in REAL_ESTATE_TERMS:
            return REAL_ESTATE_TERMS[s]
        if s in CANONICAL_PLACES:
            return CANONICAL_PLACES[s]
        if s in COMMON_NAMES:
            return COMMON_NAMES[s]

    # 1. Primary Neural Candidate: Google GTX Neural Engine
    cand_gtx = None
    try:
        import urllib.request, urllib.parse, json
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source}&tl={target}&dt=t&q=" + urllib.parse.quote(s)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=4) as res:
            data = json.loads(res.read().decode("utf-8"))
            if data and data[0]:
                cand_gtx = "".join(chunk[0] for chunk in data[0] if chunk and chunk[0]).strip()
    except Exception as e:
        logger.debug(f"Direct Google GTX failed: {e}")

    # 2. Secondary Neural Candidate: deep_translator (MyMemory / IndicTrans2)
    cand_dt = None
    try:
        from deep_translator import MyMemoryTranslator
        src_code = "tamil india" if source == "ta" else "english india"
        tgt_code = "english india" if target == "en" else "tamil india"
        trans = MyMemoryTranslator(source=src_code, target=tgt_code)
        res = trans.translate(s)
        if res and res.strip() and res.strip().lower() != s.lower():
            cand_dt = res.strip()
    except Exception as e:
        logger.debug(f"deep_translator MyMemory failed: {e}")

    # 3. Local Rule-based & Phonetic Candidate
    cand_local = transliterate_tamil_text(s) if target == "en" else dynamic_english_to_tamil(s)

    # Cross-Verification & Consensus Selection
    # If both neural engines returned candidates, verify quality
    if cand_gtx and cand_dt:
        # If both agree closely or GTX is clean and natural, prioritize verified GTX
        from difflib import SequenceMatcher
        sim = SequenceMatcher(None, cand_gtx.lower(), cand_dt.lower()).ratio()
        if sim >= 0.60:
            translated = cand_gtx
        else:
            # Round-trip verify GTX to ensure it preserves meaning accurately
            try:
                rt_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={target}&tl={source}&dt=t&q=" + urllib.parse.quote(cand_gtx)
                req_rt = urllib.request.Request(rt_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                with urllib.request.urlopen(req_rt, timeout=3) as res_rt:
                    d_rt = json.loads(res_rt.read().decode("utf-8"))
                    rt_text = "".join(c[0] for c in d_rt[0] if c and c[0]).strip() if d_rt and d_rt[0] else ""
                    rt_sim = SequenceMatcher(None, s.lower(), rt_text.lower()).ratio()
                    translated = cand_gtx if rt_sim >= 0.40 else cand_dt
            except Exception:
                translated = cand_gtx
    elif cand_gtx:
        translated = cand_gtx
    elif cand_dt:
        translated = cand_dt
    else:
        translated = cand_local

    # Post-clean: strip any leaked combining marks
    translated = _strip_stray_script_marks(translated)
    _DEEP_TRANS_CACHE[cache_key] = translated
    return translated



