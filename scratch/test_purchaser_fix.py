import re

def extract_purchaser(txt):
    HEREINAFTER_PAT = r'(?:herein|heiein|herei|here|here\s*in)[\s-]*aft[eo]r'
    
    # 1. Scope to text between ONE PART and OTHER PART, or from ONE PART onwards
    one_m = re.search(r'(?:ONE|FIRST)\s+PART\b', txt, re.I)
    other_m = re.search(r'(?:OTHER|SECOND)\s+PART\b', txt, re.I)
    
    scope = txt[one_m.end():other_m.end()] if (one_m and other_m) else txt
    
    # Check for TO AND IN FAVOUR OF
    fav_m = re.search(r'(?:TO\s+AND\s+IN\s+FAVOUR\s+OF|IN\s+FAVOUR\s+OF)\s*[:\s]*', scope, re.I)
    if fav_m:
        before_fav = scope[:fav_m.start()].strip()
        after_fav = scope[fav_m.end():].strip()
        
        # Candidate text after FAV up to hereinafter called the PURCHASER
        p_cand_m = re.search(r'(.+?)(?:,\s*|\s+)' + HEREINAFTER_PAT + r'\s+(?:called|referred\s+to\s+as)\s+(?:the\s+)?[\'\"“\s]*(?:PURCHASER|BUYER|CLAIMANT)', after_fav, re.I | re.DOTALL)
        after_text = p_cand_m.group(1).strip() if p_cand_m else after_fav.split('\n\n')[0].strip()
        
        # Check if the line right before FAV contains the person's name/honorific (e.g. Mrs SHAIALAJA SANKAR)
        before_lines = [l.strip() for l in before_fav.split('\n') if l.strip()]
        if before_lines:
            last_b = before_lines[-1]
            if any(h in last_b for h in ['Mrs', 'Mr', 'Dr', 'Smt', 'Thiru', 'Selvi', 'Miss', 'Wife of', 'Son of', 'Daughter of']) or re.match(r'^(?:years|aged|residing)\b', after_text, re.I):
                after_text = last_b + ' ' + after_text
                
        # Clean up lines
        cleaned = re.sub(r'[\r\n]+', ' ', after_text).strip()
        return cleaned
    return None

for fn in ['ocr_text_1995.txt', 'ocr_text_2004.txt', 'ocr_text_2010.txt', 'ocr_text_8916_2010.txt']:
    p = 'scratch/' + fn
    with open(p, 'r', encoding='utf-8') as f:
        txt = f.read()
    print('===', fn, '===')
    res = extract_purchaser(txt)
    print('Purchaser:', res[:120] if res else 'None')
