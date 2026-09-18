# -*- coding: utf-8 -*-
import sys, os, re
sys.path.insert(0, os.path.abspath("."))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from app.translator import CANONICAL_PLACES, COMMON_NAMES, format_bilingual_entity, format_bilingual_owner

# Test dictionary mapping for the legacy eServices font corruption
ESERVICES_FONT_MAP = [
    # Fixed phrases
    ("தமிழ்நாடு அரசு", "தநா அர"),
    ("வருவாய் மற்றும் பேரிடர் மேலாண்மைத் துறை", "வ வா\x0c ம ேப ட ேமலா ைம ைற"),
    ("வருவாய் மற்றும் பேரிடர் மேலாண்மைத் துறை", "வ வா ம ேப ட ேமலா ைம ைற"),
    ("நில உரிமை விவரங்கள் : இ.எண் 10(1) பிரிவு", " ல உ ைம பர க! : இ.எ 10(1) % &"),
    ("உரிமையாளர்கள் பெயர்", "உ ைமயாள க! ெபய"),
    ("புல எண்ணும் உட்பிரிவும்", "7ல எ 8 உ'% &"),
    ("மின்கையொப்பம்", "+ைகெய:ப"),
    ("அச்சடிக்கப்பட்டது", "அBச1/க:ப'ட"),
    ("பட்டா எண்", "ப'டா எ"),
    ("வருவாய் கிராமம்", "வ வா\x0c -ராம"),
    ("வருவாய் கிராமம்", "வ வா -ராம"),
    ("மாவட்டம்", "மாவ'ட"),
    ("வட்டம்", "வ'ட"),
    ("நன்செய்", "ந+ெச\x0c"),
    ("நன்செய்", "ந+ெச"),
    ("புன்செய்", "7+ெச\x0c"),
    ("புன்செய்", "7+ெச"),
    ("மற்றவை", "ம றைவ"),
    ("பரப்பு", "பர:7"),
    ("தீர்வை", "; ைவ"),
    ("குறிப்பு", "09:7"),
    ("மொத்தம்", "ெமா த"),
]

# Standard Tamil Nadu Revenue District Codes
TN_DISTRICT_CODES = {
    "01": ("Chennai", "சென்னை"),
    "02": ("Tiruvallur", "திருவள்ளூர்"),
    "03": ("Kanchipuram", "காஞ்சிபுரம்"),
    "04": ("Vellore", "வேலூர்"),
    "05": ("Tiruvannamalai", "திருவண்ணாமலை"),
    "06": ("Viluppuram", "விழுப்புரம்"),
    "07": ("Salem", "சேலம்"),
    "08": ("Namakkal", "நாமக்கல்"),
    "09": ("Erode", "ஈரோடு"),
    "10": ("Nilgiris", "நீலகிரி"),
    "11": ("Dindigul", "திண்டுக்கல்"),
    "12": ("Karur", "கரூர்"),
    "13": ("Tiruchirappalli", "திருச்சிராப்பள்ளி"),
    "14": ("Perambalur", "பெரம்பலூர்"),
    "15": ("Ariyalur", "அரியலூர்"),
    "16": ("Cuddalore", "கடலூர்"),
    "17": ("Nagapattinam", "நாகப்பட்டினம்"),
    "18": ("Thanjavur", "தஞ்சாவூர்"),
    "19": ("Pudukkottai", "புதுக்கோட்டை"),
    "20": ("Thiruvarur", "திருவாரூர்"),
    "21": ("Madurai", "மதுரை"),
    "22": ("Theni", "தேனி"),
    "23": ("Virudhunagar", "விருதுநகர்"),
    "24": ("Ramanathapuram", "ராமநாதபுரம்"),
    "25": ("Sivaganga", "சிவகங்கை"),
    "26": ("Tirunelveli", "திருநெல்வேலி"),
    "27": ("Thoothukudi", "தூத்துக்குடி"),
    "28": ("Kanniyakumari", "கன்னியாகுமரி"),
    "29": ("Dharmapuri", "தர்மபுரி"),
    "30": ("Krishnagiri", "கிருஷ்ணகிரி"),
    "31": ("Coimbatore", "கோயம்புத்தூர்"),
    "32": ("Tiruppur", "திருப்பூர்"),
    "33": ("Tenkasi", "தென்காசி"),
    "34": ("Tirupathur", "திருப்பத்தூர்"),
    "35": ("Ranipet", "ராணிப்பேட்டை"),
    "36": ("Chengalpattu", "செங்கல்பட்டு"),
    "37": ("Kallakurichi", "கள்ளக்குறிச்சி"),
    "38": ("Mayiladuthurai", "மயிலாடுதுறை"),
}

# Standard Taluks by (DistrictCode, TalukCode) or names
TN_DISTRICT_TALUK_CODES = {
    ("20", "01"): ("Thiruvarur", "திருவாரூர்"),
    ("20", "02"): ("Nannilam", "நன்னிலம்"),
    ("20", "03"): ("Kudavasal", "குடவாசல்"),
    ("20", "04"): ("Mannargudi", "மன்னார்குடி"),
    ("20", "05"): ("Needamangalam", "நீடாமங்கலம்"),
    ("20", "06"): ("Valangaiman", "வலங்கைமான்"),
    ("20", "07"): ("Muthupettai", "முத்துப்பேட்டை"),
    ("20", "08"): ("Koothanallur", "கூத்தநல்லூர்"),
    ("36", "01"): ("Chengalpattu", "செங்கல்பட்டு"),
    ("36", "02"): ("Kancheepuram", "காஞ்சிபுரம்"),
    ("36", "03"): ("Madurantakam", "மதுராந்தகம்"),
    ("36", "04"): ("Cheyyur", "செய்யூர்"),
    ("36", "05"): ("Tambaram", "தாம்பரம்"),
    ("36", "06"): ("Pallavaram", "பல்லாவரம்"),
    ("36", "07"): ("Vandalur", "வண்டலூர்"),
    ("36", "08"): ("Thiruporur", "திருப்போரூர்"),
}

print("Code tables defined successfully!")
