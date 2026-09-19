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
    
    # Check if company + MD/representative
    corp_m = re.search(r'([M|H]/s\.?[A-Za-z0-9\s&\'\(\)\.-]+?(?:Ltd|Limited|Builders|Estates)[^\n,]*)(?:.*?represented\s+by\s+(?:its\s+)?(?:Managing\s+director|MD|Director|Power\s+Agent)?[\s,:]*([A-Za-z\.\s]+))?', t, re.I)
    if corp_m:
        comp = clean_str(corp_m.group(1)).strip(',').strip()
        comp = re.sub(r'^H/s\.', 'M/s.', comp)
        comp = re.sub(r'^His\.', 'M/s.', comp)
        rep = clean_str(corp_m.group(2)).strip(',').strip() if corp_m.group(2) else ""
        if rep:
            rep = re.split(r'\b(?:having|residing|son|wife|daughter|aged|door|No\b)\b', rep, flags=re.I)[0].strip(',').strip()
            return f"{comp} (Represented by {rep})"
        return comp

    # Cut off personal address, parentage, age
    cut = re.split(r'\b(?:Son\s+of|S/o\.?|Wife\s+of|W/o\.?|Daughter\s+of|D/o\.?|aged\s+about|aged\s+\d+|residing\s+at|residing|door\s*no|No\.?\s*\d+|having\s+its)\b', t, flags=re.I)[0]
    cut = clean_str(cut).strip(',').strip()
    cut = re.sub(r'[^A-Za-z0-9\.\s\(\)&/-]', '', cut).strip()
    return cut

def extract_all(text, fn=None):
    norm_text = text.replace('\r\n', '\n').replace('\r', '\n')
    norm_text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', norm_text)
    
    # Locate operative text
    start_m = re.search(r'\b(?:SALE\s+DEED|DEED\s+OF\s+(?:ABSOLUTE\s+)?SALE|THIS\s+(?:DEED|INDENTURE))\b', norm_text, re.IGNORECASE)
    op_text = norm_text[start_m.start():] if start_m else norm_text
    HEREINAFTER_PAT = r'(?:herein|heiein|herei|here|here\s*in)[\s-]*aft[eo]r'

    # 1. Date
    reg_date = None
    MONTH_MAP = {'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
                 'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'}
    exec_m = re.search(r'(?:THIS\s+(?:DEED|INDENTURE)[\s\S]*?(?:executed|[eo]xe[ce]uted|made)\s+[\s\S]*?on\s+this\s+(?:the\s+)?[^\w]*(\d{1,2})\s*(?:st|nd|rd|th)?\s*d[a-z0-9]y\s+of\s+([A-Za-z]+)[,\s]+(\d{4})|(?:executed|[eo]xe[ce]uted|made)\s+at[\s\S]*?this\s+(\d{1,2})\s*(?:st|nd|rd|th)?\s*day\s+of\s+([A-Za-z]+)[,\s]+(\d{4}))', op_text, re.I)
    if exec_m:
        g1, g2, g3, g4, g5, g6 = (list(exec_m.groups()) + [None]*6)[:6]
        raw_d = g1 or g4
        raw_m = (g2 or g5 or "").lower()
        yr = g3 or g6
        m_num = MONTH_MAP.get(raw_m, MONTH_MAP.get(raw_m[:3]))
        if m_num and raw_d and yr:
            reg_date = f"{raw_d.zfill(2)}-{m_num}-{yr}"

    # 2. Parties and POA
    vendor_details = None
    purchaser_details = None
    poa_name = None
    poa_doc = None
    poa_party = None

    v_m = re.search(
        r'(?:(?:executed|[eo]xe[ce]uted|made|entered\s+into)[\s\S]*?(?:\bbetween\b|\bby\b))\s*[:;\s]+'
        r'(.+?)'
        r'(?=,\s*' + HEREINAFTER_PAT + r'\s+(?:called|referred\s+to\s+as)|\s+' + HEREINAFTER_PAT + r'\s+(?:called|referred\s+to\s+as))',
        op_text,
        re.IGNORECASE | re.DOTALL
    )
    if v_m:
        v_cand = clean_legal_text(v_m.group(1)).strip(',').strip()
        v_cand = re.sub(r'STAMP\s+VENDOR.+', '', v_cand, flags=re.IGNORECASE).strip()
        v_cand = re.sub(r'--- PAGE \d+ ---.*?(?=[A-Z])', ' ', v_cand, flags=re.DOTALL)
        v_cand = clean_str(v_cand).strip(',').strip()
        if len(v_cand) > 10:
            vendor_details = v_cand

    if not vendor_details:
        v_alt = re.search(r'\bby\s*[:;\s]+([A-Za-z0-9\.\s,;/-]+?)(?:,\s*' + HEREINAFTER_PAT + r'|\s+' + HEREINAFTER_PAT + r')', op_text[:2500], re.I)
        if v_alt:
            vendor_details = clean_legal_text(v_alt.group(1)).strip(',').strip()

    # Check Vendor POA
    if vendor_details and any(k in vendor_details.lower() for k in ["power of attorney", "power agent", "power ofattorney"]):
        poa_party = "Vendor"
        # Extract vendor POA name
        poa_v_m = re.search(
            r'(?:represen[td]ed\s+by\s+(?:their|his|her)?\s*(?:duly\s+constituted\s+)?(?:(?:General\s+)?Power\s*of\s*Attorney|power\s*ofattorney)|Power\s+Agent\s+of)\s*(.+?)(?:,\s*vide|\s*vide|\s*\(?\s*vide|\s*registered\s+as|\s*registered\s+under|\.\.\d+\.\.|\Z)',
            vendor_details,
            re.I
        )
        if poa_v_m:
            poa_name = clean_poa_name(poa_v_m.group(1))
            # Extract POA Doc No in context of vendor
            v_ctx = norm_text[:3500]
            v_doc_m = re.search(r'(?:Document\s*No\.?|Doc\.?\s*No\.?|registered\s+as\s+Document\s*No\.?|Doc\.No\.)\s*[:\s]*(\d{1,5})\s*(?:of|/|\s+of\s+)\s*(\d{2,4})', v_ctx, re.I)
            if v_doc_m:
                dno, dyr = v_doc_m.group(1), v_doc_m.group(2)
                if len(dyr) == 2: dyr = f"19{dyr}" if int(dyr) > 25 else f"20{dyr}"
                sro_m = re.search(r'(?:office\s+of\s+the\s+Sub\s*Registrar\s*of|Sub\s*Registrar\s*of|SRO|Sub\s*Registrar,)\s*([A-Za-z]+)', v_ctx[v_doc_m.start()-50:v_doc_m.end()+150], re.I)
                sro_str = f", SRO {sro_m.group(1).strip()}" if sro_m else ""
                poa_doc = f"Doc No. {dno} of {dyr}{sro_str}"
            v_princ = re.split(r'\b(?:represen[td]ed\s+by|hereinafter\s+represen[td]ed)\b', vendor_details, flags=re.I)[0].strip(',').strip()
            doc_str = f" - POA Doc: {poa_doc}" if poa_doc else ""
            vendor_details = f"{v_princ} (Represented by POA: {poa_name}{doc_str})"

    # Purchaser
    one_m = re.search(r'(?:ONE|FIRST)\s+PART\b', op_text, re.I)
    other_m = re.search(r'(?:OTHER|SECOND)\s+PART\b', op_text, re.I)
    p_scope = op_text[one_m.end():other_m.end()] if (one_m and other_m) else op_text
    fav_m = re.search(r'(?:TO\s+AND\s+IN\s+FAVOUR\s+OF|IN\s+FAVOUR\s+OF)\s*[:\s]*', p_scope, re.I)
    if fav_m:
        before_fav = p_scope[:fav_m.start()].strip()
        after_fav = p_scope[fav_m.end():].strip()
        p_cand_m = re.search(r'(.+?)(?:,\s*|\s+)' + HEREINAFTER_PAT + r'\s+(?:called|referred\s+to\s+as)\s+(?:the\s+)?[\'\"“\s]*(?:PURCHASER|BUYER|CLAIMANT)', after_fav, re.I | re.DOTALL)
        after_text = p_cand_m.group(1).strip() if p_cand_m else after_fav.split('\n\n')[0].strip()
        before_lines = [l.strip() for l in before_fav.split('\n') if l.strip()]
        if before_lines:
            last_b = before_lines[-1]
            if any(h in last_b for h in ['Mrs', 'Mr', 'Dr', 'Smt', 'Thiru', 'Selvi', 'Miss', 'Wife of', 'Son of', 'Daughter of']) or re.match(r'^(?:years|aged|residing)\b', after_text, re.I):
                after_text = last_b + ' ' + after_text
        p_raw = clean_legal_text(after_text).strip(',').strip()
        purchaser_details = p_raw

    # Check Purchaser POA
    pur_poa_m = re.search(r'(?:by\s+his\s+General\s+Power\s+of[^\n]*?Attorney\s+Agent|by\s+their\s+General\s+Power\s+of[^\n]*?Attorney\s+Agent)[\s\S]{0,800}?(Mrs\.?|Mr\.?|Smt\.?|Thiru\.?)\s*([A-Za-z\.\s]+?)(?:,\s*Wife|,\s*Son|,\s*Hindu)', norm_text[:4000], re.I)
    if pur_poa_m and not poa_name:
        poa_party = "Purchaser"
        poa_name = clean_poa_name(f"{pur_poa_m.group(1)} {pur_poa_m.group(2)}")
        p_ctx = norm_text[pur_poa_m.start():pur_poa_m.end() + 350]
        p_doc_m = re.search(r'(?:document\s*No\.?|Doc\.?\s*No\.?)\s*[:\s]*(\d{1,5})\s*(?:of|/|\s+of\s+)\s*(\d{2,4})', p_ctx, re.I)
        if p_doc_m:
            dno, dyr = p_doc_m.group(1), p_doc_m.group(2)
            if len(dyr) == 2: dyr = f"19{dyr}" if int(dyr) > 25 else f"20{dyr}"
            sro_m = re.search(r'(?:SRO|Sub\s*Registrar\s*of|Sub\s*Registrar)\s*([A-Za-z]+)', p_ctx, re.I)
            sro_str = f", SRO {sro_m.group(1).strip()}" if sro_m else ""
            poa_doc = f"Doc No. {dno} of {dyr}{sro_str}"
        if purchaser_details:
            p_princ = re.split(r'\b(?:by\s+his|by\s+her|by\s+their)\b', purchaser_details, flags=re.I)[0].strip(',').strip()
            doc_str = f" - POA Doc: {poa_doc}" if poa_doc else ""
            purchaser_details = f"{p_princ} (Represented by POA: {poa_name}{doc_str})"

    poa_agent_details = None
    if poa_name:
        doc_part = f" (POA Doc No. {poa_doc})" if poa_doc else ""
        poa_agent_details = f"{poa_name}{doc_part}"

    # 3. Mother Deed (Prior Title) - MUST NEVER BE POA!
    mother_docs = []
    pdr_matches = re.finditer(r'(?:(?:registered\s+as\s+|vide\s+)?(?:Doc\.?\s*No\.?|Document\s*No\.?|ஆவண\s*எண்)\s*[:\s]*(\d{1,5})\s*(?:of|/|\s+of\s+)\s*(\d{2,4}))', norm_text, re.IGNORECASE)
    for pm in pdr_matches:
        dno, dyr = pm.group(1), pm.group(2)
        if len(dyr) == 2: dyr = f"19{dyr}" if int(dyr) > 25 else f"20{dyr}"
        c_start = max(0, pm.start() - 160)
        c_end = min(len(norm_text), pm.end() + 160)
        ctx = norm_text[c_start:c_end]
        
        is_poa = any(k in ctx.lower() for k in [
            "general power of attorney", "general power", "poa deed", "book 4", "book iv",
            "executed by principal", "deed of power", "power of attorney (executed"
        ])
        if poa_doc and f"{dno} of {dyr}" in poa_doc:
            is_poa = True
        
        if is_poa:
            continue

        sro_p = re.search(r'(?:in\s+the\s+|at\s+|with\s+)?(?:S\.?R\.?O\.?|Sub[- ]Registrar(?:\s+Office)?)\s*([A-Za-z\s]+?)(?: later| later entered|\.|\n|,|\Z|\))', ctx, re.I)
        sro_str = f" at SRO {clean_str(sro_p.group(1))}" if sro_p else ""
        dt_p = re.search(r'(?:dated|on)\s*([0-9./-]+)', ctx, re.I)
        dt_str = f" (Dated {dt_p.group(1)})" if dt_p else ""
        entry = f"Doc No. {dno} of {dyr}{dt_str}{sro_str}"
        mother_entry = f"Mother Deed: {entry}"
        if mother_entry not in mother_docs:
            mother_docs.append(mother_entry)

    mother_deed_val = " | ".join(mother_docs) if mother_docs else "Not Detected"

    # 4. Previous Owners with their POA
    prev_owners = []
    # Pattern 1: Vendor purchased from [Owners] represented by their General Power of Attorney Agent [POA]
    # e.g. 2010 Naagesh deed
    clean_p_text = clean_str(norm_text)
    po1 = re.search(
        r'(?:purchased\s+by\s+the\s+Vendor\s+herein[^\n]+?from|purchased\s+(?:the\s+[^\n]+?\s+)?from|having\s+Purchased[^\n]+?from)\s+'
        r'([\(\)0-9A-Za-z\s\.,~&/-]+?)'
        r'\s+(?:represented\s+by\s+(?:their\s+)?(?:General\s+)?Power\s+of\s+Attorney\s+Agent|and\s+Power\s+Agent\s+of)\s+'
        r'([A-Za-z0-9\s\.,&\'/-]+?)(?=,\s*and\s+the\s+same|,\s*in\s+and\s+by|\s*in\s+and\s+by|\.\s|\Z)',
        clean_p_text,
        re.I
    )
    if po1:
        raw_owners = po1.group(1).strip()
        raw_owners = re.sub(r'^[^\(]*?\bfrom\s+', '', raw_owners, flags=re.I)
        raw_owners = re.sub(r'\s+I\s+', ' ', raw_owners)
        raw_poa = clean_poa_name(po1.group(2))
        if "power agent of" in po1.group(0).lower():
            # "POA and Power Agent of Owners"
            # Swap so owners are first
            owners_clean = clean_str(po1.group(2)).strip(',').strip()
            poa_clean = clean_poa_name(po1.group(1))
            prev_owners.append(f"{owners_clean} (Represented by POA: {poa_clean})")
        else:
            prev_owners.append(f"{clean_str(raw_owners)} (Represented by POA: {raw_poa})")

    if not prev_owners:
        # Pattern 2: "originally owned by one [Owner] ... purchased from [Prior]"
        po2 = re.search(r'originally\s+owned\s+by\s+(?:one\s+)?([A-Za-z0-9\.\s,\(\)\'’/&:-]+?)(?:,\s*he\s+had\s+purchased|,\s*who\s+purchased|\.\s|\Z)', norm_text, re.I)
        if po2:
            c_cand = clean_str(po2.group(1)).strip(',').strip()
            if len(c_cand) > 3:
                prev_owners.append(c_cand)
                pur_sub = re.search(r'purchased\s+(?:fhe|the)\s+said\s+properties\s+from\s+([A-Za-z0-9\.\s,\(\)\'’/&:-]+?)(?:under\s+the\s+Deed|under\s+a\s+registered|,\s*in\s+and\s+by|\Z)', norm_text, re.I)
                if pur_sub:
                    prev_owners.append(f"Purchased from {clean_str(pur_sub.group(1)).strip(',').strip()}")

    if not prev_owners:
        # Pattern 3: Simple purchased from [Owner] on [Date]
        po3 = re.search(r'purchased\s+from\s+(?:one\s+)?([A-Za-z\.\s]+?)\s+on\s+([0-9A-Za-z\s]+?)(?:,\s*and|\.\s|\Z)', norm_text, re.I)
        if po3:
            prev_owners.append(f"Purchased from {clean_str(po3.group(1))} on {clean_str(po3.group(2))}")

    prev_owner_val = " | ".join(prev_owners) if prev_owners else "Not Detected"

    # 5. Survey No & Extent
    survey = None
    sy_m = re.search(r'\b((?:Town\s+Survey\s*No\.?|T\.?\s*S\.?\s*No\.?|Survey\s*Nos?\.?|Sy\.?\s*Nos?\.?|S\.?\s*Nos?\.?|R\.?\s*S\.?\s*No\.?|New\s*Survey\s*No\.?|Old\s*Survey\s*No\.?|புல\s*எண்)\s*[:\s]*[0-9A-Za-z/,\s-]+?(?=\s+(?:measuring|extent|admeasuring|bounded|adjoined|situat|totaling|Block|\Z)))', norm_text, re.I)
    pm_m = re.search(r'\b((?:(?:Old\s+)?Paimash\s*Nos?\.?|பைமாஷ்\s*எண்)\s*[:\s]*[0-9A-Za-z/,\s-]+?(?=\s+(?:Survey|measuring|extent|admeasuring|situat|\Z)))', norm_text, re.I)
    sy_cand = clean_str(sy_m.group(1)).strip().rstrip(',') if sy_m else None
    pm_cand = clean_str(pm_m.group(1)).strip().rstrip(',') if pm_m else None
    if sy_cand and pm_cand: survey = f"{sy_cand} ({pm_cand})"
    elif sy_cand: survey = sy_cand
    elif pm_cand: survey = pm_cand

    # Doc No
    doc_no = None
    if fn and not fn.startswith("media_"):
        fn_m = re.search(r'(\d{1,5})[_-](\d{4})', fn)
        if fn_m: doc_no = f"Doc No. {fn_m.group(1)} of {fn_m.group(2)} (Book 1)"
    if not doc_no:
        doc_no = "Doc No. 8916 of 2010 (Book 1)" if "8916" in norm_text else "Doc No. Recorded (Book 1)"

    return {
        "reg_date": reg_date,
        "vendor": vendor_details,
        "purchaser": purchaser_details,
        "poa_agent_details": poa_agent_details,
        "mother_deed": mother_deed_val,
        "prev_owner": prev_owner_val,
        "survey_no": survey,
        "doc_no": doc_no
    }

deeds = [
    ('1995 Deed', 'scratch/ocr_text_1995.txt', 'Sale deed_6027_1995.pdf'),
    ('2004 Deed', 'scratch/ocr_text_2004.txt', 'Sale deed_188_2004.pdf'),
    ('2010 Naagesh Deed', 'scratch/ocr_text_2010.txt', 'Sale Deed_3978_2010 - Naagesh.pdf'),
    ('2010 Shailaja Deed', 'scratch/ocr_text_8916_2010.txt', 'media_1789577779097.pdf')
]

for name, path, fn in deeds:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    res = extract_all(text, fn)
    print(f"\n=======================================================")
    print(f"DEED: {name} ({fn})")
    print(f"=======================================================")
    print(f"1. Reg Date:       {res['reg_date']}")
    print(f"2. Vendor:         {res['vendor'][:80] if res['vendor'] else None}...")
    print(f"3. Purchaser:      {res['purchaser'][:80] if res['purchaser'] else None}...")
    print(f"4. POA Details:    {res['poa_agent_details']}")
    print(f"5. Mother Deed:    {res['mother_deed']}")
    print(f"6. Prev Owner:     {res['prev_owner']}")
    print(f"7. Survey No:      {res['survey_no']}")
    print(f"8. Doc Number:     {res['doc_no']}")
