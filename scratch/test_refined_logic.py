import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

def clean_str(s):
    if not s: return ""
    s = re.sub(r'[\r\n]+', ' ', str(s))
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip()

def clean_legal_text(raw_text):
    if not raw_text: return ""
    t = re.sub(r'--- PAGE \d+ ---', ' ', str(raw_text))
    t = re.sub(r'\.\.\d+\.\.', ' ', t)
    t = re.sub(r'\b\d{4,5}\s*Rs\.?\b', ' ', t)
    t = re.sub(r'\b(?:FIVE|ONE|TWO)\s+THOUSAND\s+RUPEES\b', ' ', t, flags=re.IGNORECASE)
    t = re.sub(r'(?:STAMP\s+VENDOR|AHMED|MOHOMED|LICENCE\s*NO|MADRAS-\d+|Phone\s*N[oa]|Ph247\d+|Dayalu\s+Nagar)[^,\n]*', ' ', t, flags=re.IGNORECASE)
    t = re.sub(r'[\r\n]+', ' ', t)
    t = re.sub(r'\s{2,}', ' ', t)
    return t.strip()

def clean_poa_name(raw: str) -> str:
    if not raw: return ""
    t = re.sub(r'--- PAGE \d+ ---.*?(?=[A-Z])', ' ', raw, flags=re.DOTALL)
    t = re.sub(r'[\.]{2,}[^\w]*', ' ', t)
    t = clean_str(t)
    
    corp_m = re.search(r'(M/s\.?[A-Za-z0-9\s&\'\(\)\.-]+?(?:Ltd|Limited|Builders|Estates)[^\n,]*)(?:.*?represented\s+by\s+(?:its\s+)?(?:Managing\s+director|MD|Director|Power\s+Agent)?[\s,:]*([A-Za-z\.\s]+))?', t, re.I)
    if corp_m:
        comp = clean_str(corp_m.group(1)).strip(',').strip()
        rep = clean_str(corp_m.group(2)).strip(',').strip() if corp_m.group(2) else ""
        if rep:
            rep = re.split(r'\b(?:having|residing|son|wife|daughter|aged|door|No\b)\b', rep, flags=re.I)[0].strip(',').strip()
            return f"{comp} (Represented by {rep})"
        return comp

    cut = re.split(r'\b(?:Son\s+of|S/o\.?|Wife\s+of|W/o\.?|Daughter\s+of|D/o\.?|aged\s+about|aged\s+\d+|residing\s+at|residing|door\s*no|No\.?\s*\d+|having\s+its)\b', t, flags=re.I)[0]
    cut = clean_str(cut).strip(',').strip()
    cut = re.sub(r'[^A-Za-z0-9\.\s\(\)&/-]', '', cut).strip()
    return cut

def extract_poa_and_mother_deed(text):
    norm_text = text.replace('\r\n', '\n').replace('\r', '\n')
    norm_text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', norm_text)
    
    # 1. Identify POA Agent & POA Document
    poa_name = None
    poa_doc = None
    poa_party = None # "vendor" or "purchaser"

    # Search for POA in Vendor
    poa_v_m = re.search(
        r'(?:represen[td]ed\s+by\s+(?:their|his|her)?\s*(?:duly\s+constituted\s+)?(?:(?:General\s+)?Power\s*of\s*Attorney|power\s*ofattorney)|Power\s+Agent\s+of)\s*[:\s]*'
        r'([^\n\(\)]+?(?:Son\s+of|Wife\s+of|residing|Ltd|Limited|aged)[^\n\(\)]*?)'
        r'(?:\(\s*Vide|\s*Vide|\s*registered\s+as|\s*registered\s+under|\Z)',
        norm_text[:3500],
        re.IGNORECASE
    )
    if not poa_v_m:
        poa_v_m = re.search(
            r'(?:represen[td]ed\s+by\s+(?:their|his|her)?\s*(?:duly\s+constituted\s+)?(?:(?:General\s+)?Power\s*of\s*Attorney|power\s*ofattorney))\s*[:\s]*'
            r'([A-Za-z0-9\s\.,&\'/-]+?)(?=(?:,\s*vide|\s*vide|\s*\(?\s*vide|\s*registered\s+as|\s*registered\s+under|hereinafter|\.\.\d+\.\.|\Z))',
            norm_text[:3500],
            re.IGNORECASE
        )

    # Search for POA in Purchaser
    poa_p_m = re.search(
        r'(?:PURCHASER|CLAIMANT|OTHER\s+PART)[\s\S]{0,300}?(?:by\s+(?:his|her|their)?\s*(?:General\s+)?Power\s*of\s*Attorney\s*(?:Agent)?|Power\s+Agent)\s*[:\s]*'
        r'([^\n\(\)]+?(?:Son\s+of|Wife\s+of|residing|aged)[^\n\(\)]*?)'
        r'(?:\(\s*which|\(\s*Vide|\s*Vide|\s*registered\s+as|\s*registered\s+under|\Z)',
        norm_text[:4000],
        re.IGNORECASE
    )

    if poa_v_m:
        poa_name = clean_poa_name(poa_v_m.group(1))
        poa_party = "Vendor"
        # Find POA doc near vendor POA match
        v_ctx = norm_text[poa_v_m.start():poa_v_m.end() + 350]
        p_doc_m = re.search(r'(?:Document\s*No\.?|Doc\.?\s*No\.?|registered\s+as\s+Document\s*No\.?|Doc\.No\.)\s*[:\s]*(\d{1,5})\s*(?:of|/|\s+of\s+)\s*(\d{2,4})', v_ctx, re.I)
        if p_doc_m:
            dno, dyr = p_doc_m.group(1), p_doc_m.group(2)
            if len(dyr) == 2: dyr = f"19{dyr}" if int(dyr) > 25 else f"20{dyr}"
            sro_m = re.search(r'(?:office\s+of\s+the\s+Sub\s*Registrar\s*of|Sub\s*Registrar\s*of|SRO|Sub\s*Registrar,)\s*([A-Za-z]+)', v_ctx, re.I)
            sro_str = f", SRO {sro_m.group(1).strip()}" if sro_m else ""
            poa_doc = f"Doc No. {dno} of {dyr}{sro_str}"
    elif poa_p_m:
        poa_name = clean_poa_name(poa_p_m.group(1))
        poa_party = "Purchaser"
        p_ctx = norm_text[poa_p_m.start():poa_p_m.end() + 350]
        p_doc_m = re.search(r'(?:Document\s*No\.?|Doc\.?\s*No\.?|registered\s+as\s+Document\s*No\.?|document\s*No\.)\s*[:\s]*(\d{1,5})\s*(?:of|/|\s+of\s+)\s*(\d{2,4})', p_ctx, re.I)
        if p_doc_m:
            dno, dyr = p_doc_m.group(1), p_doc_m.group(2)
            if len(dyr) == 2: dyr = f"19{dyr}" if int(dyr) > 25 else f"20{dyr}"
            sro_m = re.search(r'(?:SRO|Sub\s*Registrar\s*of|Sub\s*Registrar)\s*([A-Za-z]+)', p_ctx, re.I)
            sro_str = f", SRO {sro_m.group(1).strip()}" if sro_m else ""
            poa_doc = f"Doc No. {dno} of {dyr}{sro_str}"

    # Also check if purchaser POA occurred across page boundaries (e.g. 2010 Naagesh deed)
    if not poa_name:
        p_alt = re.search(r'by\s+his\s+General\s+Power\s+of\s+Attorney\s+Agent[\s\S]{0,500}?(Mrs\.?|Mr\.?|Smt\.?|Thiru\.?)\s*([A-Za-z\.\s]+?)(?:,\s*Wife|\s*Wife|,\s*Son|\s*Son)', norm_text[:4000], re.I)
        if p_alt:
            poa_name = clean_poa_name(f"{p_alt.group(1)} {p_alt.group(2)}")
            poa_party = "Purchaser"
            alt_ctx = norm_text[p_alt.start():p_alt.end() + 300]
            alt_doc = re.search(r'document\s*No\.?\s*(\d{1,5})\s*(?:of|/|\s+of\s+)\s*(\d{2,4})', alt_ctx, re.I)
            if alt_doc:
                dno, dyr = alt_doc.group(1), alt_doc.group(2)
                sro_m = re.search(r'SRO\s*([A-Za-z]+)', alt_ctx, re.I)
                sro_str = f", SRO {sro_m.group(1).strip()}" if sro_m else ""
                poa_doc = f"Doc No. {dno} of {dyr}{sro_str}"

    poa_details = None
    if poa_name:
        doc_part = f" (POA Doc No. {poa_doc})" if poa_doc else ""
        poa_details = f"{poa_name}{doc_part}"

    # 2. Extract Mother Deed (Previous Document Reference)
    # MUST EXCLUDE ANY POA DOCUMENT!
    mother_docs = []
    pdr_matches = re.finditer(r'(?:(?:registered\s+as\s+|vide\s+)?(?:Doc\.?\s*No\.?|Document\s*No\.?|ஆவண\s*எண்)\s*[:\s]*(\d{1,5})\s*(?:of|/|\s+of\s+)\s*(\d{2,4}))', norm_text, re.IGNORECASE)
    
    for pm in pdr_matches:
        dno, dyr = pm.group(1), pm.group(2)
        if len(dyr) == 2: dyr = f"19{dyr}" if int(dyr) > 25 else f"20{dyr}"
        
        c_start = max(0, pm.start() - 160)
        c_end = min(len(norm_text), pm.end() + 160)
        ctx = norm_text[c_start:c_end]
        
        # Check if this match is a POA deed!
        is_poa = any(k in ctx.lower() for k in [
            "general power of attorney", "general power", "poa deed", "book 4", "book iv",
            "executed by principal", "deed of power", "power of attorney (executed"
        ])
        # If it matches the POA doc number we already identified, definitely skip!
        if poa_doc and f"{dno} of {dyr}" in poa_doc:
            is_poa = True

        if is_poa:
            continue  # NEVER ADD POA AS MOTHER DEED!

        # Check if it is a title conveyance (Sale deed, Partition, etc.)
        sro_p = re.search(r'(?:in\s+the\s+|at\s+|with\s+)?(?:S\.?R\.?O\.?|Sub[- ]Registrar(?:\s+Office)?)\s*([A-Za-z\s]+?)(?: later| later entered|\.|\n|,|\Z|\))', ctx, re.IGNORECASE)
        sro_str = f" at SRO {clean_str(sro_p.group(1))}" if sro_p else ""
        
        dt_p = re.search(r'(?:dated|on)\s*([0-9./-]+)', ctx, re.IGNORECASE)
        dt_str = f" (Dated {dt_p.group(1)})" if dt_p else ""
        
        entry = f"Doc No. {dno} of {dyr}{dt_str}{sro_str}"
        mother_entry = f"Mother Deed: {entry}"
        if mother_entry not in mother_docs:
            mother_docs.append(mother_entry)

    mother_deed_val = " | ".join(mother_docs) if mother_docs else "Not Detected"

    # 3. Extract Previous Owner with their POA
    prev_owners = []
    
    # Pattern A: "purchased ... from [Owners] represented by their General Power of Attorney Agent [POA Agent]"
    # e.g. 2010 Naagesh deed
    po_a = re.search(
        r'(?:purchased\s+by\s+the\s+Vendor\s+herein[^\n]+?from|having\s+Purchased[^\n]+?from|purchased\s+(?:the\s+[^\n]+?\s+)?from)\s+'
        r'(\([1-9]\)[^\n]+?(?:\([1-9]\)[^\n]+?)+|[0-9]\)[^\n]+?(?:[0-9]\)[^\n]+?)+|[A-Za-z\.\s,\(\)\'’/&]+?)\s+'
        r'(?:represented\s+by\s+(?:their\s+)?(?:General\s+)?Power\s+of\s+Attorney\s+Agent|and\s+Power\s+Agent\s+of)\s+'
        r'([A-Za-z0-9\.\s,\(\)\'’/&:-]+?)(?=,\s*and\s+the\s+same|,\s*in\s+and\s+by|\s*in\s+and\s+by|\.\s|\Z)',
        norm_text,
        re.I
    )
    if po_a:
        owners_part = clean_str(po_a.group(1)).strip(',').strip()
        poa_part = clean_poa_name(po_a.group(2)).strip(',').strip()
        prev_owners.append(f"{owners_part} (Represented by POA: {poa_part})")
    
    # Pattern B: "Purchased ... from [POA Agent] ... and Power Agent of [Owners]"
    # e.g. 2004 deed
    po_b = re.search(
        r'(?:having\s+Purchased[^\n]+?from|purchased\s+from)\s+'
        r'([A-Za-z0-9\.\s,\(\)\'’/&:-]+?),\s*and\s+Power\s+Agent\s+of\s+'
        r'([0-9A-Za-z\.\s,\(\)\'’/&:-]+?)(?=,\s*in\s+and\s+by|\s*in\s+and\s+by|\.\s|\Z)',
        norm_text,
        re.I
    )
    if po_b and not prev_owners:
        poa_agent_name = clean_poa_name(po_b.group(1))
        owners_name = clean_str(po_b.group(2)).strip(',').strip()
        prev_owners.append(f"{owners_name} (Represented by POA: {poa_agent_name})")

    # Pattern C: "originally owned by [Owner], he had purchased ... from [Prior Owner]"
    # e.g. 2010 Shailaja deed
    po_c = re.search(
        r'originally\s+owned\s+by\s+(?:one\s+)?([A-Za-z0-9\.\s,\(\)\'’/&:-]+?)(?:,\s*he\s+had\s+purchased|,\s*who\s+purchased|\.\s|\Z)',
        norm_text,
        re.I
    )
    if po_c:
        c_cand = clean_str(po_c.group(1)).strip(',').strip()
        if len(c_cand) > 3:
            prev_owners.append(c_cand)
            # check if he purchased from someone
            pur_sub = re.search(r'purchased\s+(?:fhe|the)\s+said\s+properties\s+from\s+([A-Za-z0-9\.\s,\(\)\'’/&:-]+?)(?:under\s+the\s+Deed|under\s+a\s+registered|,\s*in\s+and\s+by|\Z)', norm_text, re.I)
            if pur_sub:
                prev_owners.append(f"Purchased from {clean_str(pur_sub.group(1)).strip(',').strip()}")

    # Pattern D: Simple "Purchased from [Owner] on [Date]"
    # e.g. 1995 deed
    if not prev_owners:
        po_d = re.search(r'purchased\s+from\s+(?:one\s+)?([A-Za-z\.\s]+?)\s+on\s+([0-9A-Za-z\s]+?)(?:,\s*and|\.\s|\Z)', norm_text, re.I)
        if po_d:
            prev_owners.append(f"Purchased from {clean_str(po_d.group(1))} on {clean_str(po_d.group(2))}")

    prev_owner_val = " | ".join(prev_owners) if prev_owners else "Not Detected"

    return {
        "poa_agent_details": poa_details,
        "mother_deed": mother_deed_val,
        "previous_owner_with_poa": prev_owner_val
    }

deeds = [
    ('1995 Deed', 'scratch/ocr_text_1995.txt'),
    ('2004 Deed', 'scratch/ocr_text_2004.txt'),
    ('2010 Naagesh Deed', 'scratch/ocr_text_2010.txt'),
    ('2010 Shailaja Deed', 'scratch/ocr_text_8916_2010.txt')
]

for name, path in deeds:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    res = extract_poa_and_mother_deed(text)
    print(f"\n==========================================")
    print(f"DEED: {name}")
    print(f"==========================================")
    print("POA Details:     ", res["poa_agent_details"])
    print("Mother Deed:     ", res["mother_deed"])
    print("Prev Owner w/POA:", res["previous_owner_with_poa"])
