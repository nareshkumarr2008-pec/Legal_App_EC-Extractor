# -*- coding: utf-8 -*-
import re, sys, os
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')
from app.translator import COMMON_NAMES, dynamic_transliterate_tamil, format_bilingual_owner

def clean_noise(s):
    # Remove TR references, dates, and order numbers
    s = re.sub(r'\b\d{4}/\d+/\d+/\w+.*$', '', s, flags=re.I)
    s = re.sub(r'TR\s*DT[:.\s]+.*$', '', s, flags=re.I)
    s = re.sub(r'DT\.?\s*\d{4}[-/]\d{2}[-/]\d{2}.*$', '', s, flags=re.I)
    s = re.sub(r'\b\d{2}[-/]\d{2}[-/]\d{4}\b.*$', '', s)

    # Specific Tamil and English table noise keywords
    noise = [
        'ரயத்துத் வாரி', 'ரயத்துவாரி', 'ரயத்துத்வாரி', 'ரயத் வாரி', 'ரயத்வாரி',
        'புஞ்சை', 'நஞ்சை', 'மனை', 'கட்டிடம்', 'சர்க்கார்', 'புறம்போக்கு',
        'Municipal', 'Govt', 'Rs.', 'Paise', 'Block', 'Adangal', 'UDS', 'Details',
        'Remarks', 'குறிப்பு', 'Extent', 'Survey', 'Field', 'Assessment'
    ]
    for w in noise:
        s = s.replace(w, ' ')
    
    s = re.sub(r'\b(Block|DT|TR|Name|Selaiyur|Tambaram|Chengalpattu)\b', ' ', s, flags=re.I)
    # Remove numbers and punctuation
    s = re.sub(r'[-0-9\.:=/|]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def is_valid_tamil_name_part(s):
    """Check if string is a valid Tamil name word (not noise, not numbers, not table labels)."""
    if not s:
        return False
    # Must contain at least one Tamil character
    if not re.search(r'[\u0b80-\u0bff]', s):
        return False
    # Must not contain TR or date
    if re.search(r'(?:\d{4}|DT|TR|Block|https)', s, re.I):
        return False
    # Must not be pure noise keyword
    noise_exact = {
        'ரயத்துவாரி', 'ரயத்துத் வாரி', 'ரயத் வாரி', 'புஞ்சை', 'நஞ்சை', 'மனை', 'கட்டிடம்',
        'சர்க்கார்', 'புறம்போக்கு', 'குறிப்பு', 'வட்டம்', 'மாவட்டம்', 'நகரம்', 'வார்டு'
    }
    if s in noise_exact:
        return False
    return True

def extract_tslr_owner_from_lines(lines):
    # Check if Government / Poramboke
    all_text = " ".join(lines)
    if re.search(r'சர்க்கார்|புறம்போக்கு|Government\s*Poramboke|Poramboke', all_text, re.IGNORECASE):
        return "Not Recorded (-) (பதிவு செய்யப்படவில்லை)"

    # Look for kinship in lines
    kinship_idx = -1
    for idx, line in enumerate(lines):
        if any(k in line for k in ["மகன்", "மகள்", "மனைவி", "கணவர்", "Son of", "D/o", "W/o", "S/o"]):
            kinship_idx = idx
            break

    if kinship_idx != -1:
        kinship_line = clean_noise(lines[kinship_idx])
        
        # Check kinship keyword
        m_rel = re.search(r'(மகன்|மகள்|மனைவி|கணவர்)', kinship_line)
        if m_rel:
            rel_word = m_rel.group(1)
            before_rel = kinship_line[:m_rel.start()].strip()
            after_rel = kinship_line[m_rel.end():].strip()

            # 1. If before_rel is empty or too short (< 2 Tamil chars), look at preceding lines
            father_part = before_rel
            if len(re.findall(r'[\u0b80-\u0bff]', father_part)) < 2:
                # Look backwards for preceding name
                for p_idx in range(kinship_idx - 1, max(-1, kinship_idx - 3), -1):
                    cand = clean_noise(lines[p_idx])
                    if is_valid_tamil_name_part(cand):
                        father_part = cand + (" " + father_part if father_part else "")
                        if len(re.findall(r'[\u0b80-\u0bff]', cand)) >= 3:
                            break

            # 2. If after_rel is empty or only an initial (length <= 2), look at succeeding lines
            person_part = after_rel
            # Initial like "நா" has 1 Tamil vowel-consonant (length 1 or 2). A full name has >= 3 chars.
            if len(re.findall(r'[\u0b80-\u0bff]', person_part)) <= 2:
                # Look forwards for succeeding name
                for s_idx in range(kinship_idx + 1, min(len(lines), kinship_idx + 3)):
                    cand = clean_noise(lines[s_idx])
                    if is_valid_tamil_name_part(cand):
                        person_part = (person_part + " " if person_part else "") + cand
                        if len(re.findall(r'[\u0b80-\u0bff]', cand)) >= 3:
                            break

            full_tamil = f"{father_part} {rel_word} {person_part}".strip()
            full_tamil = re.sub(r'\s+', ' ', full_tamil)
            return full_tamil

    # Fallback to general line search
    return None

test_cases = [
    (
        "TSLR Sample with split lines (70, 71, 72)",
        [
            "23 -",
            "23 ரயத்துவாரி புஞ்சை - 0- 0.00 0 2 64.0 - 0.00 -",
            "நாராயணன்",
            "மகன் நா",
            "கோவிந்தராஜூ",
            "2025/0153/35/005324TR",
            "DT. 2025-08-31 TR DT:"
        ]
    ),
    (
        "TSLR User Screenshot with merged row",
        [
            "23 -",
            "நாராயணன்",
            "1 Block- 73 0 23 ரயத்துத் வாரி புஞ்சை - 0- 0.00 0 2 64.0 - 0.00 - மகன் நா DT. 2025-08-31 TR DT:",
            "கோவிந்தராஜூ",
            "2025/0153/35/005324TR"
        ]
    ),
    (
        "Single line full name",
        [
            "Block 01",
            "ரயத்துவாரி மனை",
            "ராமசாமி மகன் ஆர் சுப்பிரமணியன்",
            "2024/0153/TR"
        ]
    )
]

for name, sample_lines in test_cases:
    print(f"=== {name} ===")
    extracted_raw = extract_tslr_owner_from_lines(sample_lines)
    print("Extracted Raw:", extracted_raw)
