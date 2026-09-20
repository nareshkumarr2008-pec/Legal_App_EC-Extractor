import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

import re
from app.translator import format_bilingual_owner, COMMON_NAMES, dynamic_transliterate_tamil

def parse_patta_universal(text: str):
    clean_text = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = [l.strip() for l in clean_text.splitlines() if l.strip()]

    is_natham = bool(re.search(r'நத்தம்\s*பட்டா|நத்தம்\s*நில|நத்தம்\s*அடங்கல்|நத்தம்\s*புல', clean_text, re.I))

    # 1. Patta Number
    patta_no = None
    m_p = re.search(r'(?:பட்டா\s*(?:எண்|எ[ணனஏ]+|ஏன்|no|number)?)\s*[:\-\s]+(\d{1,7})\b', clean_text, re.IGNORECASE)
    if m_p:
        patta_no = m_p.group(1).strip()

    # 2. District, Taluk, Village
    raw_dist, raw_taluk, raw_village = None, None, None
    for l in lines[:30]:
        m_d = re.search(r'(?:(?:வருவாய்\s*)?மாவட்டம்|district)\s*[:\-\s]+([^\n|:]+?)(?=\s*(?:[|]|\b(?:வட்டம்|கிராமம்|பட்டா|taluk|village)\b)|$)', l, re.I)
        if m_d:
            cand = m_d.group(1).strip()
            cand = re.sub(r'ட்+$', '', cand)
            if cand and len(cand) >= 2:
                raw_dist = cand
        m_t = re.search(r'(?<!மா)(?:வட்டம்|taluk)\s*[:\-\s]+([^\n|:]+?)(?=\s*(?:[|]|\b(?:மாவட்டம்|கிராமம்|பட்டா|district|village)\b)|$)', l, re.I)
        if m_t:
            cand = m_t.group(1).strip()
            if cand and len(cand) >= 2:
                raw_taluk = cand
        m_v = re.search(r'(?:வருவாய்\s*)?கிராம(?:ம்|த்தின்)?\s*(?:எண்\s*(?:மற்றும்|&)\s*பெயர்|பெயர்|எண்)?\s*[:\-\s]+([^\n|:]+?)(?=\s*(?:[|]|\b(?:வட்டம்|மாவட்டம்|பட்டா|taluk|district)\b)|$)', l, re.I)
        if m_v:
            cand = m_v.group(1).strip()
            cand = re.sub(r'^\d+\s*[-/.:\s]*', '', cand).strip()
            if cand and len(cand) >= 2:
                raw_village = cand

    # 3. Owner & Kinship
    owner_lines = []
    in_owner = False
    for l in lines:
        if any(k in l.lower() for k in ["உரிமையாளர்கள் பெயர்", "உரிமையாளர் பெயர்", "owners name", "pattadhar name"]):
            in_owner = True
            post = re.sub(r'^(?:(?:உரிமையாளர்கள்?\s*பெயர்|owners?\s*name)[^\w\d]*)+', '', l, flags=re.IGNORECASE).strip()
            if len(post) >= 3:
                owner_lines.append(post)
            continue
        if in_owner:
            if any(k in l.lower() for k in ["survey", "s.no", "புல எண்", "நத்தம் புல எண்", "வ.எண்", "நன்செய்", "நஞ்சை", "புன்செய்", "digital signature", "10(1)", "மாவட்டம்", "வட்டம்"]):
                break
            clean_item = re.sub(r'^\d+[\.\s\-]*$', '', l).strip()
            if clean_item and len(clean_item) >= 3:
                owner_lines.append(clean_item)
            if len(owner_lines) >= 8:
                break

    raw_owner_str = "\n".join(owner_lines).strip()
    formatted_owners = []
    for ol in owner_lines:
        ol_clean = re.sub(r'^\d+[\.\)\s\-]+', '', ol).strip()
        ol_clean = re.sub(r'[\s\-]+$', '', ol_clean).strip()
        m_kin = re.search(r'(.+?)\s+(மகன்|மகள்|மனைவி|கணவர்)\s+(.+)', ol_clean)
        if m_kin:
            f_ta = m_kin.group(1).strip()
            rel_ta = m_kin.group(2).strip()
            o_ta = m_kin.group(3).strip()
            rel_en = "S/o" if rel_ta == "மகன்" else ("W/o" if rel_ta == "மனைவி" else ("D/o" if rel_ta == "மகள்" else "H/o"))
            f_en = COMMON_NAMES.get(f_ta.lower(), dynamic_transliterate_tamil(f_ta)).title()
            o_en = COMMON_NAMES.get(o_ta.lower(), dynamic_transliterate_tamil(o_ta)).title()
            formatted_owners.append(f"{o_en}, {rel_en} {f_en} ({f_ta} {rel_ta} {o_ta})")
            continue
        m_spo = re.search(r'(.+?)\s+(?:த/பெ|க/பெ|ம/பெ)\s+(.+)', ol_clean)
        if m_spo:
            o_ta = m_spo.group(1).strip()
            f_ta = m_spo.group(2).strip()
            o_en = COMMON_NAMES.get(o_ta.lower(), dynamic_transliterate_tamil(o_ta)).title()
            f_en = COMMON_NAMES.get(f_ta.lower(), dynamic_transliterate_tamil(f_ta)).title()
            formatted_owners.append(f"{o_en}, S/o {f_en} ({o_ta} த/பெ {f_ta})")
            continue
        formatted_owners.append(format_bilingual_owner(ol_clean))

    bilingual_owner = "\n".join(formatted_owners) if formatted_owners else format_bilingual_owner(raw_owner_str)

    # 4. Schedule / Cadastral Table
    detected_surveys = []
    schedule = []
    extent_summary_str = ""
    extent_details_val = ""
    nature_of_land = "Rayathuvari Manai (Residential Plot) — ரயத்துவாரி மனை" if is_natham else "Nanjai (Wet Land) — நன்செய்"
    total_tax_str = "Rs. 0.00"

    if is_natham:
        # Natham Patta Row Parsing
        # Looks for: Survey Subdiv [OldSurvey]
        # e.g. "128 11 128--" or "128 11"
        m_nsno = re.search(r'(?:நத்தம்\s*புல\s*எண்|உட்பிரிவு\s*எண்)[\s\S]{0,100}?\b(\d{1,4})\s+(\d{1,4}[A-Za-z]?)(?:\s+(\d{1,4}[A-Za-z\-]*)?)?', clean_text)
        if m_nsno:
            s_no = m_nsno.group(1).strip()
            sub_no = m_nsno.group(2).strip()
            old_sno = m_nsno.group(3).strip() if m_nsno.group(3) else None
            if old_sno:
                old_sno = re.sub(r'[\-\s]+$', '', old_sno)
            comb_sno = f"{s_no}/{sub_no}"
            detected_surveys.append(comb_sno)

            # Extent & Tax in Natham: "0 - 0.51 2.00" or "0 - 0.51"
            m_next = re.search(r'(\d{1,2})\s*-\s*(\d{1,2}(?:\.\d{1,2})?|\d{1,2}\s*-\s*\d{1,2})(?:\s+(\d{1,3}(?:\.\d{2})?))?', clean_text)
            if m_next:
                raw_ext = f"{m_next.group(1)} - {m_next.group(2)}"
                raw_sub_ext = m_next.group(2).replace(' ', '')
                if '.' in raw_sub_ext:
                    ar_val = float(raw_sub_ext)
                else:
                    ar_val = float(raw_sub_ext) / 100.0 if float(raw_sub_ext) > 5 else float(raw_sub_ext)
                
                # In Tamil Nadu Hec-Are-Sq.M, 0 - 0.51 means 0.51 Ares = 51 Sq.Meters
                sqm = round(ar_val * 100.0) if ar_val < 10 else round(ar_val)
                sqft = round(sqm * 10.7639)
                grounds = round(sqft / 2400.0, 2)
                acres = round(sqft / 43560.0, 3)

                raw_tax = m_next.group(3)
                tax_str = f"Rs. {float(raw_tax):.2f}" if raw_tax else "Rs. 2.00"
                total_tax_str = tax_str

                extent_summary_str = f"{ar_val} Ares ({sqft:,} Sq.Ft / {sqm} Sq.M)"
                extent_details_val = (
                    f"{comb_sno}: {raw_ext} ({ar_val} Ares / {sqft:,} Sq.Ft / {sqm} Sq.M / {grounds} Grounds) — Tax: {tax_str}\n"
                    f"Total Extent: {ar_val} Ares ({sqft:,} Sq.Ft / {sqm} Sq.M / {grounds} Grounds / {acres} Acres) — Total Tax: {tax_str}"
                )

                schedule.append({
                    "sl": "1",
                    "survey_no": comb_sno,
                    "old_survey_no": old_sno or s_no,
                    "land_type": "ரயத்துவாரி மனை (Residential Site / Manai)",
                    "extent_ha": raw_ext,
                    "extent_ares": f"{ar_val} Ares",
                    "sq_meters": f"{sqm} Sq.M",
                    "sq_feet": f"{sqft:,} Sq.Ft",
                    "tax": tax_str
                })

    return {
        "is_natham": is_natham,
        "patta_number": patta_no,
        "district": raw_dist,
        "taluk": raw_taluk,
        "village": raw_village,
        "owner_name": bilingual_owner,
        "survey_numbers": ", ".join(detected_surveys),
        "extent_summary": extent_summary_str,
        "extent_details": extent_details_val,
        "nature_of_land": nature_of_land,
        "total_tax": total_tax_str,
        "schedule": schedule
    }

# Test on the user's Natham Patta text
user_ocr = """தமிழ்நாடு அரசு
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

res = parse_patta_universal(user_ocr)
print("--- RESULTS FOR USER NATHAM PATTA ---")
for k, v in res.items():
    print(f"{k}: {v}")
