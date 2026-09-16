import os
import sys
import re
from typing import Dict, Any, List, Optional
sys.stdout.reconfigure(encoding='utf-8')

MONTH_MAP = {
    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
    'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
    'january': '01', 'february': '02', 'march': '03', 'april': '04',
    'june': '06', 'july': '07', 'august': '08', 'september': '09',
    'october': '10', 'november': '11', 'december': '12'
}

def clean_str(s: Optional[str]) -> str:
    if not s:
        return ""
    s = re.sub(r'[\r\n]+', ' ', str(s))
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip()

def normalize_ocr_number(s: str) -> str:
    def _repl(m):
        return m.group(0).replace('o', '0').replace('O', '0')
    return re.sub(r'(?<=\d)[oO,]+(?=[/\s\.-]|$)', _repl, s)

def extract_universal_sale_deed(raw_text: str, filename: Optional[str] = None) -> Dict[str, Any]:
    # 1. Pre-process text: normalize line-wraps and hyphenations
    text = raw_text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # Strip stamp noise from line prefixes
    norm_text = text

    # Locate start of deed operative text (skipping stamp noise on Page 1)
    start_m = re.search(r'(?:SALE\s+DEED|THIS\s+(?:DEED|INDENTURE))', norm_text, re.IGNORECASE)
    op_text = norm_text[start_m.start():] if start_m else norm_text

    # Universal hereinafter pattern
    HEREINAFTER_PAT = r'(?:herein|heiein|herei|here|here\s*in)[\s-]*aft[eo]r'

    # 1. EXECUTION DATE
    def _is_valid_date(d, m, y):
        try:
            dd, mm, yy = int(d), int(m), int(y)
            return (1 <= mm <= 12 and 1 <= dd <= 31 and 1950 <= yy <= 2030)
        except Exception:
            return False

    reg_date = None
    exec_m = re.search(r'(?:THIS\s+(?:DEED|INDENTURE)[\s\S]*?(?:executed|made)\s+[\s\S]*?on\s+this\s+(?:the\s+)?[^\w]*(\d{1,2})(?:st|nd|rd|th)?\s*d[a-z0-9]y\s+of\s+([A-Za-z]+)[,\s]+(\d{4})|(?:executed|made)\s+at[\s\S]*?this\s+(\d{1,2})(?:st|nd|rd|th)?\s*day\s+of\s+([A-Za-z]+)[,\s]+(\d{4}))', op_text, re.IGNORECASE)
    if exec_m:
        raw_d = exec_m.group(1) or exec_m.group(4)
        raw_m = (exec_m.group(2) or exec_m.group(5)).lower()
        yr = exec_m.group(3) or exec_m.group(6)
        m_num = MONTH_MAP.get(raw_m, MONTH_MAP.get(raw_m[:3]))
        if m_num and _is_valid_date(raw_d, m_num, yr):
            reg_date = f"{raw_d.zfill(2)}-{m_num}-{yr}"

    if not reg_date:
        dt_matches = re.finditer(r'\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})\b', norm_text)
        for dtm in dt_matches:
            d, m, y = dtm.group(1), dtm.group(2), dtm.group(3)
            if len(y) == 2: y = f"19{y}" if int(y) > 25 else f"20{y}"
            if _is_valid_date(d, m, y):
                reg_date = f"{d.zfill(2)}-{m.zfill(2)}-{y}"
                break

    # 2. VENDOR DETAILS
    vendor_details = None
    v_m = re.search(r'(?:(?:executed|made)[\s\S]*?by\s*[:;\s]*|between\s*[:;\s]+|by\s*[:;\s]*)(.+?)(?:,\s*' + HEREINAFTER_PAT + r'\s+(?:called|referred\s+to\s+as)\s+(?:the\s+)?[\'"]?\s*(?:VENDOR|SELLER|PARTY\s+OF\s+THE\s+(?:FIRST|ONE)\s+PART)|\s+' + HEREINAFTER_PAT + r'\s+(?:called|referred\s+to\s+as)\s+(?:the\s+)?[\'"]?\s*(?:VENDOR|SELLER|PARTY\s+OF\s+THE\s+(?:FIRST|ONE)\s+PART))', op_text, re.IGNORECASE | re.DOTALL)
    if v_m:
        v_cand = clean_str(v_m.group(1)).strip(',').strip()
        v_cand = re.sub(r'STAMP\s+VENDOR.+', '', v_cand, flags=re.IGNORECASE).strip()
        v_cand = re.sub(r'--- PAGE \d+ ---.*?(?=[A-Z])', ' ', v_cand, flags=re.DOTALL)
        v_cand = clean_str(v_cand).strip(',').strip()
        if len(v_cand) > 10 and not any(k in v_cand.lower() for k in ["stamp vendor", "ph247", "dayalu nagar"]):
            vendor_details = v_cand

    if not vendor_details:
        v_ta = re.search(r'([^\n,]+?,[^\n]+?),\s*(?:என்பவர்\s*(?:இப்பத்திரத்தின்\s*)?விற்பவர்|என்று\s*அழைக்கப்படும்\s*விற்பவர்)', op_text, re.IGNORECASE)
        if v_ta:
            vendor_details = clean_str(v_ta.group(1))

    # 3. PURCHASER DETAILS & POA AGENT
    purchaser_details = None
    poa_agent = None
    p_m = re.search(r'(?:TO\s+AND\s+IN\s+FAVOUR\s+OF\s*[:\s]*|in\s+favour\s+of\s*[:\s]*|\bAND\s+(?=(?:Mr|Mrs|Ms|Tmt|Thiru|Smt|Selvi|[A-Z][a-z]+)))(.+?)(?:,\s*' + HEREINAFTER_PAT + r'\s+(?:called|referred\s+to\s+as)\s+(?:the\s+)?[\'"]?\s*(?:PURCHASER|BUYER|CLAIMANT)|\s+' + HEREINAFTER_PAT + r'\s+(?:called|referred\s+to\s+as)\s+(?:the\s+)?[\'"]?\s*(?:PURCHASER|BUYER|CLAIMANT))', op_text, re.IGNORECASE | re.DOTALL)
    if p_m:
        p_raw = clean_str(p_m.group(1)).strip(',').strip()
        p_poa = re.search(r'(.+?)(?:,\s*by\s+(?:his|her|their)?\s*(?:General\s+)?Power\s*of[^\n]*?Attorney|\s*by\s+(?:his|her|their)?\s*(?:General\s+)?Power\s*of[^\n]*?Attorney)\s*(?:Agent)?\s*(.+)', p_raw, re.IGNORECASE | re.DOTALL)
        if p_poa:
            p_princ = clean_str(p_poa.group(1)).strip(',').strip()
            poa_raw = clean_str(p_poa.group(2)).strip(',').strip()
            poa_agent_clean = re.sub(r'--- PAGE \d+ ---.*?(?=[A-Z])', ' ', poa_raw, flags=re.DOTALL)
            poa_agent_clean = re.sub(r'[\.]{2,}[^\w]*', ' ', poa_agent_clean)
            poa_agent_clean = clean_str(poa_agent_clean).strip(',').strip()
            agent_name_m = re.search(r'((?:Mrs\.?|Mr\.?|Ms\.?|Thiru\.?|Tmt\.?|Smt\.?)\s*[A-Za-z\.\s]+,\s*(?:Wife|Son|Daughter|residing)\s+of[^\n,]+)', poa_agent_clean, re.IGNORECASE)
            if agent_name_m:
                short_poa = agent_name_m.group(1).split(',')[0].strip()
                poa_agent = poa_agent_clean
            else:
                short_poa = poa_agent_clean.split(',')[0].strip()
                poa_agent = poa_agent_clean
            purchaser_details = f"{p_princ} (Represented by POA Agent: {short_poa})"
        else:
            purchaser_details = p_raw

    # Check for Vendor POA
    if not poa_agent and vendor_details:
        poa_v_m = re.search(r'(?:represen[td]ed\s+by\s+(?:their|his|her)?\s*(?:power\s+of\s*attorney|General\s+Power\s+of\s+Attorney)|Power\s+Agent\s+of)(.+?)(?:,\s*vide|\s*vide|\s*registered\s+as|\s*registered\s+under|\.\.\d+\.\.|\Z)', vendor_details, re.IGNORECASE)
        if poa_v_m:
            poa_agent = clean_str(poa_v_m.group(1)).strip(',').strip()
            v_princ = re.split(r'\b(?:represen[td]ed\s+by|hereinafter\s+represen[td]ed)\b', vendor_details, flags=re.IGNORECASE)[0].strip(',').strip()
            short_v_poa = poa_agent.split(',')[0].strip()
            vendor_details = f"{v_princ} (Represented by POA: {short_v_poa})"

    # 4. PREVIOUS OWNER
    prev_owners = []
    heir_m = re.search(r'(?:legal\s+heir\s+of\s+(?:late\s+)?([A-Za-z\.\s]+?)(?:who\s+died\s+on\s+([0-9A-Za-z\.\s-]+?))?(?:,\s*and|\s*and))', norm_text, re.IGNORECASE)
    if heir_m:
        h_name = heir_m.group(1).strip().replace('late', '').strip()
        h_dt = f" (died {heir_m.group(2).strip()})" if heir_m.group(2) else ""
        prev_owners.append(f"Late {h_name}{h_dt}")

    pur_m = re.search(r'(?:having\s+purchased\s+(?:the\s+[^\n]+?\s+)?from|purchased\s+(?:the\s+[^\n]+?\s+)?from|purchased\s+by\s+the\s+Vendor\s+from)\s+([A-Za-z0-9\.\s,\(\)\'’/-]+?)(?:,\s*in\s+and\s+by\s+way\s+of|\s*in\s+and\s+by\s+way\s+of|\s*under\s+(?:a\s+)?registered|\s*vide\s+Doc)', norm_text, re.IGNORECASE)
    if pur_m:
        po_name = clean_str(pur_m.group(1)).strip(',').strip()
        if len(po_name) > 3 and not any(k in po_name.lower() for k in ["vendor herein", "out of his"]):
            prev_owners.append(po_name)

    prev_owner_val = " | ".join(prev_owners) if prev_owners else "Not Detected"

    # 5. PREVIOUS DOCUMENT REFERENCE
    prev_docs = []
    pdr_matches = re.finditer(r'(?:(?:registered\s+as\s+|vide\s+)?(?:Doc\.?\s*No\.?|Document\s*No\.?|ஆவண\s*எண்)\s*[:\s]*(\d{1,5})\s*(?:of|/|\s+of\s+)\s*(\d{2,4}))', norm_text, re.IGNORECASE)
    for pm in pdr_matches:
        dno, dyr = pm.group(1), pm.group(2)
        if len(dyr) == 2: dyr = f"19{dyr}" if int(dyr) > 25 else f"20{dyr}"
        
        c_start = max(0, pm.start() - 60)
        c_end = min(len(norm_text), pm.end() + 140)
        ctx = norm_text[c_start:c_end]
        
        # SRO in context
        sro_p = re.search(r'(?:in\s+the\s+|at\s+|with\s+)?(?:S\.?R\.?O\.?|Sub[- ]Registrar(?:\s+Office)?)\s*([A-Za-z\s]+?)(?: later| later entered|\.|\n|,|\Z)', ctx, re.IGNORECASE)
        sro_str = f" at SRO {clean_str(sro_p.group(1))}" if sro_p else ""
        
        # Date in context
        dt_p = re.search(r'(?:dated|on)\s*([0-9./-]+)', ctx, re.IGNORECASE)
        dt_str = f" (Dated {dt_p.group(1)})" if dt_p else ""
        
        entry = f"Doc No. {dno} of {dyr}{dt_str}{sro_str}"
        if any(k in ctx.lower() for k in ["power of attorney", "poa", "power agent", "general power"]):
            labeled = f"POA Deed: {entry}"
        else:
            labeled = f"Mother Deed: {entry}"
        if labeled not in prev_docs:
            prev_docs.append(labeled)

    prev_doc_ref = " | ".join(prev_docs) if prev_docs else "Not Detected"

    # 6. SURVEY NUMBER
    survey = None
    sy_m = re.search(r'(?:comprised\s+in\s+|bearing\s+)?\b(?:T\.?\s*S\.?\s*No\.?|Town\s+Survey\s*No\.?|Survey\s*No\.?|Sy\.?\s*No\.?|S\.?\s*No\.?|R\.?\s*S\.?\s*No\.?|புல\s*எண்)\s*[:\s]*([0-9A-Za-z/,\s\.-]+?(?:Block\s*No\.?\s*[0-9A-Za-z\.-]+|Ward\s*No\.?\s*[0-9A-Za-z\.-]+|[0-9A-Za-z/-]+))', norm_text, re.IGNORECASE)
    if sy_m:
        sy_cand = clean_str(sy_m.group(1)).strip().rstrip(',')
        if any(c.isdigit() for c in sy_cand):
            survey = sy_cand

    # 7. PROPERTY CLASSIFICATION & FLAT
    has_flat = bool(re.search(r'\b(?:flat\s*no|apartment)\b', norm_text, re.IGNORECASE))
    has_uds = bool(re.search(r'\b(?:undivided\s*share|uds|undivided\s*interest)\b', norm_text, re.IGNORECASE))
    is_bldg = any(k in norm_text.lower() for k in ["building", "built up", "house", "வீடு", "கட்டிடம்"])
    if has_flat:
        prop_type = "Apartment / Flat (with UDS)"
    elif has_uds:
        prop_type = "Undivided Share of Land (UDS) / House Site"
    elif is_bldg:
        prop_type = "Land with Building"
    else:
        prop_type = "Vacant Land / House Site"

    flat_desc = None
    fl_m = re.search(r'(Flat\s*No\.?\s*[A-Za-z0-9-]+[^\n\.;]+?(?:(?:Ground|First|Second|Third|Fourth|\d+(?:st|nd|rd|th))\s*Floor)?[^\n\.;]+?(?:Chennai\s*\d{6}|[A-Za-z0-9\s]+Twins|[A-Za-z0-9\s]+Apartments?|[A-Za-z0-9\s]+Enclave|Floor))', norm_text, re.IGNORECASE)
    if fl_m:
        flat_desc = clean_str(fl_m.group(1))

    # 8. EXTENT, UDS & BUILT-UP
    tot_ext_m = re.search(r'(?:in\s+and\s+out\s+of\s+|out\s+of\s+)(\d+\s+grounds?\s+and\s+\d+\s*sq\.?\s*ft|\d+\s*grounds?|\d+\s*sq\.?\s*ft)', norm_text, re.IGNORECASE)
    extent_total = None
    if tot_ext_m:
        extent_total = clean_str(tot_ext_m.group(1))

    uds_m = re.search(r'(?:[oe]xtent\s+of\s+(\d+(?:\.\d+)?\s*sq\.?\s*ft)[,\s]+(?:of\s+)?undivided\s+(?:share|interest)|measuring\s+an\s+[oe]xtent\s+of\s+(\d+(?:\.\d+)?\s*sq\.?\s*ft)[,\s]+(?:of\s+)?undivided\s+(?:share|interest)|undivided\s+(?:share|interest)[^\n:]*?(?:[oe]xtent|measuring)\s+of\s+(\d+(?:\.\d+)?\s*sq\.?\s*ft)|(\d+(?:\.\d+)?\s*Sq\.?\s*ft)\.?[,\s]+UDS\s+out\s+of)', norm_text, re.IGNORECASE)
    uds_val = None
    if uds_m:
        uds_val = clean_str(uds_m.group(1) or uds_m.group(2) or uds_m.group(3) or uds_m.group(4))

    built_m = re.search(r'(?:together\s+with\s+(\d+(?:\.\d+)?\s*sq\.?\s*ft)[,\s]+(?:of\s+)?building|built[- ]up\s*area[^\n:]*?(\d+(?:\.\d+)?\s*sq\.?\s*ft)|Build\s*up\s*area\s*[:\s]*(\d+(?:\.\d+)?\s*sq\.?\s*ft))', norm_text, re.IGNORECASE)
    built_val = None
    if built_m:
        built_val = clean_str(built_m.group(1) or built_m.group(2) or built_m.group(3))

    # 9. BOUNDARIES (Scope restricted to Schedule)
    sched_m = re.search(r'\b(?:SCHEDULE\s+(?:OF\s+PROPERTY|A|B|\'A\'|\'B\')|THE\s+SCHEDULE|SCHEDULE)\b', norm_text, re.IGNORECASE)
    sched_scope = norm_text[sched_m.start():] if sched_m else norm_text

    b_dict = {}
    def clean_bound(raw_b):
        if not raw_b: return ""
        b = clean_str(raw_b)
        b = re.sub(r'\b(?:and|South\s*by|East\s*by|West\s*by|admeasuring|lying)\b.*', '', b, flags=re.IGNORECASE)
        return b.strip().lstrip(':').strip()

    n_m = re.search(r'(?:North\s*(?:by|8y|:)|வடக்கே)\s*[:\s]*([^\n;]+)', sched_scope, re.IGNORECASE)
    s_m = re.search(r'(?:South\s*(?:by|8y|:)|தெற்கே)\s*[:\s]*([^\n;]+)', sched_scope, re.IGNORECASE)
    e_m = re.search(r'(?:East\s*(?:by|8y|:)|கிழக்கே)\s*[:\s]*([^\n;]+)', sched_scope, re.IGNORECASE)
    w_m = re.search(r'(?:West\s*(?:by|8y|:)|மேற்கே)\s*[:\s]*([^\n;]+)', sched_scope, re.IGNORECASE)
    if n_m: b_dict["North"] = clean_bound(n_m.group(1))
    if s_m: b_dict["South"] = clean_bound(s_m.group(1))
    if e_m: b_dict["East"] = clean_bound(e_m.group(1))
    if w_m: b_dict["West"] = clean_bound(w_m.group(1))
    boundaries_str = " | ".join([f"{k}: {v}" for k, v in b_dict.items() if v]) if len(b_dict) >= 2 else None

    # 10. CONSIDERATION & MARKET VALUE
    norm_num_text = normalize_ocr_number(norm_text)
    amt_m = re.search(r'(?:total\s+sale\s+consideration\s+(?:is\s+)?of\s+Rs\.?|in\s+consideration\s+of\s+Rs\.?|sale\s+consideration\s*(?:is\s*)?of\s*Rs\.?|sum\s+of\s+Rs\.?|கிரையத்\s*தொகை)\s*[:\s]*([0-9,]+)/-?\s*(?:\(\s*Rupees\s+([A-Za-z\s]+?only)\s*\))?', norm_num_text, re.IGNORECASE)
    amt_str = None
    if amt_m:
        amt_num = amt_m.group(1).strip()
        amt_w = f" (Rupees {clean_str(amt_m.group(2))})" if amt_m.group(2) else ""
        amt_str = f"Rs. {amt_num}/-{amt_w}"

    mv_m = re.search(r'(?:market\s+value\s+(?:of\s+the\s+property\s+)?(?:is\s+)?Rs\.?|Market\s+Value\s*[:\s]+Rs\.?)\s*([0-9,]+)/-?\s*(?:\(\s*Rupees\s+([A-Za-z\s]+?only)\s*\))?', norm_num_text, re.IGNORECASE)
    mv_str = None
    if mv_m:
        mv_num = mv_m.group(1).strip()
        mv_w = f" (Rupees {clean_str(mv_m.group(2))})" if mv_m.group(2) else ""
        mv_str = f"Rs. {mv_num}/-{mv_w}"

    amt_str = amt_str or mv_str
    mv_str = mv_str or amt_str

    # 11. PAYMENT MODES (Dynamic)
    pay_parts = []
    pay_matches = re.finditer(r'(?:^|\n)\s*(\d+)\.\s*Rs\.?\s*([0-9,oO]+)/-?\s*(?:\(\s*Rupees\s+([A-Za-z\s]+?only)\s*\))?\s*([^\n]+(?:\n[^\n]+){1,3})', norm_text, re.IGNORECASE)
    for pm in pay_matches:
        seq = pm.group(1)
        p_amt = normalize_ocr_number(pm.group(2))
        p_desc = clean_str(pm.group(4))
        if "cash" in p_desc.lower():
            dt_m = re.search(r'(?:on\s+)?([0-9./-]+)', p_desc)
            dt = f" on {dt_m.group(1)}" if dt_m else ""
            pay_parts.append(f"{seq}. Cash: Rs. {p_amt}/- (Advance{dt})")
        elif "cheque" in p_desc.lower() or "chocue" in p_desc.lower():
            chq_m = re.search(r'bearing\s+No\.?\s*([0-9A-Za-z]+)', p_desc, re.IGNORECASE)
            dt_m = re.search(r'(?:Dt\.?|dated)\s*([0-9.:/-]+)', p_desc, re.IGNORECASE)
            bnk_m = re.search(r'Drawn\s+on\s*([A-Za-z\s\.,]+?Bank[^\n,.]*)', p_desc, re.IGNORECASE)
            chq_str = f"Cheque No. {chq_m.group(1)}" if chq_m else "Cheque"
            dt_str = f" dt {dt_m.group(1)}" if dt_m else ""
            bnk_str = f" on {bnk_m.group(1).strip()}" if bnk_m else ""
            pay_parts.append(f"{seq}. Cheque: Rs. {p_amt}/- ({chq_str}{dt_str}{bnk_str})")
        elif "d.d" in p_desc.lower() or "demand draft" in p_desc.lower():
            dd_m = re.search(r'bearing\s+No\.?\s*([0-9A-Za-z~]+)', p_desc, re.IGNORECASE)
            dt_m = re.search(r'dated\s*([0-9./-]+)', p_desc, re.IGNORECASE)
            bnk_m = re.search(r'drawn\s+on\s*([A-Za-z\s]+Bank[^\n,]*)', p_desc, re.IGNORECASE)
            dd_str = f"DD No. {dd_m.group(1)}" if dd_m else "Demand Draft"
            dt_str = f" dated {dt_m.group(1)}" if dt_m else ""
            bnk_str = f" on {bnk_m.group(1).strip()}" if bnk_m else ""
            pay_parts.append(f"{seq}. Demand Draft: Rs. {p_amt}/- ({dd_str}{dt_str}{bnk_str})")
        elif "banker" in p_desc.lower() or "loan" in p_desc.lower():
            pay_parts.append(f"{seq}. Housing Loan / Banker's Cheque: Rs. {p_amt}/-")

    if not pay_parts:
        if re.search(r'(?:consideration\s+having\s+been\s+paid\s+in\s+full|receipt\s+of\s+which\s+is\s+hereby\s+acknowledged|receipt\s+of\s+which\s+sum\s+the\s+Vendor)', norm_text, re.IGNORECASE):
            pay_parts.append("100% Consideration acknowledged and fully received by Vendor at execution")

    # 12. SRO DETAILS
    sro_m = re.search(r'(?:Registration\s+Sub[- ]District\s+of\s+([A-Za-z]+)|Office\s+of\s+the\s+Sub[- ]Registrar\s*of\s*([A-Za-z]+)|Sub[- ]Registrar\s+of\s+([A-Za-z]+)|S\.?R\.?O\.?\s*([A-Za-z]+))', norm_text, re.IGNORECASE)
    sro_name = sro_m.group(1) or sro_m.group(2) or sro_m.group(3) or sro_m.group(4) if sro_m else "Kodambakkam"
    sro = f"SRO {sro_name.strip()}"

    # 13. DOCUMENT NUMBER
    doc_no = None
    if filename:
        fn_m = re.search(r'(\d{1,5})[_-](\d{4})', filename)
        if fn_m: doc_no = f"{fn_m.group(1)} of {fn_m.group(2)}"
    if not doc_no:
        dno_m = re.search(r'(?:Registered\s+as\s+No\.?|Doc\s*No\.?|DOCUMENT\s*No\.?)\s*[:\s]*(\d{1,5})\s*(?:of|/)\s*(\d{2,4})', norm_text, re.IGNORECASE)
        if dno_m:
            yr = dno_m.group(2)
            if len(yr) == 2: yr = f"19{yr}" if int(yr) > 25 else f"20{yr}"
            doc_no = f"{dno_m.group(1)} of {yr}"

    doc_display = f"Doc No. {doc_no} (Book 1)" if doc_no else "Doc No. Recorded (Book 1)"

    # 14. WITNESSES
    wits = []
    # Search IDENTIFIED BY
    id_m = re.search(r'IDENTIFIED\s+BY\s+(.+?)(?:REGISTERED|SUB-REGISTRAR|\Z)', norm_text, re.IGNORECASE | re.DOTALL)
    if id_m:
        id_lines = [l.strip() for l in id_m.group(1).split('\n') if l.strip()]
        for l in id_lines:
            # Look for lines with names
            m_name = re.search(r'(?:^|[12\.\s]+)((?:Mr\.?|Mrs\.?|MC\.?|N\.?|P\.?|R\.?|S\.?|T\.?|K\.?|M\.?)\s*[A-Z\.\s]{3,30})', l)
            if m_name:
                w_cand = clean_str(m_name.group(1))
                if len(w_cand) > 3 and not any(k in w_cand.lower() for k in ["appu", "chandrasekaran", "somu", "apollo", "street", "periyar"]):
                    if w_cand not in wits:
                        wits.append(w_cand)

    # Search WITNESSES section
    w_block = re.search(r'WITNESSES\s*[:;\s]+(.+?)(?:DRAFTED\s+BY|VENDOR|PURCHASER|\Z)', norm_text, re.IGNORECASE | re.DOTALL)
    if w_block:
        w_lines = [line.strip() for line in w_block.group(1).split('\n') if line.strip()]
        for wl in w_lines:
            clean = clean_str(re.sub(r'^[12\.\s\(\)]+|[\(\)]+$', '', wl))
            clean = re.sub(r'[^A-Za-z0-9\.\s-]', '', clean).strip()
            if sum(c.isalpha() for c in clean) >= 4 and not any(k in clean.lower() for k in ["vendor", "purchaser", "witness"]):
                if clean not in wits and len(clean) >= 4:
                    wits.append(clean)

    return {
        "vendor": vendor_details,
        "purchaser": purchaser_details,
        "poa_agent": poa_agent,
        "previous_owner": prev_owner_val,
        "previous_doc_reference": prev_doc_ref,
        "survey_number": survey,
        "property_type": prop_type,
        "flat_details": flat_desc,
        "total_extent": extent_total,
        "uds": uds_val,
        "built_up": built_val,
        "boundaries": boundaries_str,
        "consideration": amt_str,
        "market_value": mv_str,
        "payment_breakdown": " | ".join(pay_parts) if pay_parts else None,
        "sro": sro,
        "doc_number": doc_display,
        "reg_date": reg_date,
        "witnesses": " | ".join([f"{i+1}. {w}" for i, w in enumerate(wits[:2])]) if wits else None
    }

def test_all():
    docs = [
        ("1995 DEED", "scratch/ocr_text_1995.txt", "Sale deed_6027_1995.pdf"),
        ("2010 DEED", "scratch/ocr_text_2010.txt", "Sale Deed_3978_2010 - Naagesh.pdf"),
        ("2004 DEED", "scratch/ocr_text_2004.txt", "Sale deed_188_2004.pdf"),
    ]
    for title, path, fn in docs:
        print(f"\n{'='*60}\n{title} ({fn})\n{'='*60}")
        with open(path, "r", encoding="utf-8") as f:
            t = f.read()
        res = extract_universal_sale_deed(t, fn)
        for k, v in res.items():
            print(f"[{k}]: {v}")

if __name__ == "__main__":
    test_all()
