import re
from typing import Optional

def clean_str(s: Optional[str]) -> str:
    if not s: return ""
    s = re.sub(r'[\r\n]+', ' ', str(s))
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip()

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

print("Testing clean_poa_name:")
print("1:", clean_poa_name("Mr.E.GOPI Son of Mr.E.Bakthavatchalam, residing at No 12A, Second Cross Street, Krishnapuram, Thirunindravur, Poonamallee Taluk, Thiruvallur District"))
print("2:", clean_poa_name("Mrs.V.M.BHUWANEESVARI, Wife of Mr~M.B.Naagesh, Hindu, aged about 3S years, residing at No.6/2, Sri Ramar Street, Devaraj Nagar, Dasarathapuram, Saligramam, Chennai 600093"))
print("3:", clean_poa_name("M/s.Apollo Estates & Builders Privated Ltd.,hereafter represented by its Managing director, Mr.Jamal Asan Aliyar, having its registered office at Gee Gee Plaza"))
