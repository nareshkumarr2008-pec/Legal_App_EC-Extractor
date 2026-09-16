import re

with open('scratch/ocr_text_8916_2010.txt', 'r', encoding='utf-8') as f:
    txt = f.read()

print('=== 1. CONSIDERATION ===')
amt_m = re.search(
    r'\b(?:SALE\s+DEED\s+FOR\s+Rs\.?|total\s+sale\s+consideration\s+(?:is\s+)?of\s+Rs\.?|in\s+consideration\s+of\s+Rs\.?|sale\s+consideration\s*(?:is\s*)?of\s*Rs\.?|sum\s+of\s+Rs\.?|கிரையத்\s*தொகை)\s*[:\s]*([0-9,]+)(?:/-?|-00|\.00)?\s*(?:\(\s*Rupees\s+([A-Za-z\s]+?only)\s*\))?',
    txt,
    re.I
)
if amt_m:
    amt_num = amt_m.group(1).strip()
    amt_w = f" (Rupees {amt_m.group(2).strip()})" if amt_m.group(2) else ""
    print(f"Matched Consideration: Rs. {amt_num}/-{amt_w}")
else:
    print("Consideration NOT matched!")

print('\n=== 2. DOCUMENT NUMBER & BOOK 4 FILTER ===')
# Find all doc number occurrences with context
doc_candidates = []
for dm in re.finditer(r'(?:DOCUMENT|Doc(?:ument)?|DCCUMEN,?)[\s\S]{0,40}?(?:No\.?)\s*[:\s]*([0-9A-Za-z\.]+)\s*(?:[\.,\s]*(?:Year|of|oF)\s*(\d{4})|(?:\s*Year\s*(\d{4})))?', txt, re.I):
    raw_num = dm.group(1).replace('l', '1').replace('b', '6').replace('o', '0').replace('O', '0').strip()
    yr = dm.group(2) or dm.group(3)
    c_start = max(0, dm.start() - 60)
    c_end = min(len(txt), dm.end() + 60)
    ctx = txt[c_start:c_end]
    is_book4 = bool(re.search(r'\b(?:Book\s*4|Book\s*IV)\b', ctx, re.I))
    doc_candidates.append({
        'num': raw_num,
        'year': yr,
        'is_book4': is_book4,
        'ctx': ctx.replace('\n', ' ')
    })

print("Found doc candidates:")
for dc in doc_candidates:
    print(dc)

# Filter out Book 4
valid_deed_candidates = [c for c in doc_candidates if not c['is_book4'] and re.search(r'\d+', c['num'])]
print("Valid Sale Deed candidates (non-Book 4):")
for v in valid_deed_candidates:
    clean_digits = re.sub(r'\D', '', v['num'])
    print(f"Num: {v['num']} -> Digits: {clean_digits}, Year: {v['year']}")

print('\n=== 3. SURVEY & PAIMASH NUMBERS ===')
sy_m = re.search(r'\b((?:Survey\s*Nos?\.?|Sy\.?\s*Nos?\.?|S\.?\s*Nos?\.?|புல\s*எண்)\s*[:\s]*([0-9A-Za-z/,\s-]+?)(?=\s+(?:measuring|extent|admeasuring|bounded|adjoined|situat|totaling|\Z)))', txt, re.I)
pm_m = re.search(r'\b((?:(?:Old\s+)?Paimash\s*Nos?\.?|பைமாஷ்\s*எண்)\s*[:\s]*([0-9A-Za-z/,\s-]+?)(?=\s+(?:Survey|measuring|extent|admeasuring|situat|\Z)))', txt, re.I)
sy_val = sy_m.group(0).strip().rstrip(',') if sy_m else None
pm_val = pm_m.group(0).strip().rstrip(',') if pm_m else None
print("Survey Match:", sy_val)
print("Paimash Match:", pm_val)
combined_survey = f"{sy_val} ({pm_val})" if (sy_val and pm_val) else (sy_val or pm_val)
print("Combined Survey:", combined_survey)

print('\n=== 4. TOTAL LAND EXTENT ===')
tot_m = re.search(r'(?:totaling\s+(?:in\s+all\s*)?|total\s+extent\s*(?:is\s*)?of\s*)([0-9\.\s,]+(?:Acres?|Cents?|sq\.?\s*ft|grounds?)(?:\s*(?:and|,)?\s*[0-9\.\s]+(?:Acres?|Cents?|sq\.?\s*ft|grounds?))*)', txt, re.I)
if tot_m:
    print("Matched Total Extent:", tot_m.group(1).strip())

print('\n=== 5. PREVIOUS OWNER & HISTORY ===')
# Recital: originally owned by one Mr.A.K.Munusamy Naidu Son of Mr.A.Kannan Naidu, he had purchased the said properties from Mr.Srinivasa Iyangar
orig_m = re.search(r'(?:originally\s+owned\s+by\s+(?:one\s+)?|belonged\s+to\s+)([A-Za-z0-9\.\s,\(\)\'’/&:-]+?)(?:,\s*he\s+had\s+purchased|,\s*who\s+purchased|,\s*and\s+thereafter|\.\s|\Z)', txt, re.I)
pur_m = re.search(r'(?:purchased\s+(?:fhe|the)\s+said\s+properties\s+from|having\s+purchased\s+from|purchased\s+from)\s+([A-Za-z0-9\.\s,\(\)\'’/&:-]+?)(?:,\s*under|\s*under|\s*and\s+others|\s*vide|\Z)', txt, re.I)
po_parts = []
if orig_m:
    po_parts.append(orig_m.group(1).strip().rstrip(','))
if pur_m:
    po_parts.append(f"Purchased from {pur_m.group(1).strip().rstrip(',')}")
print("Previous Owner / History:", " | ".join(po_parts))

print('\n=== 6. PROPERTY CLASSIFICATION ===')
class_m = re.search(r'\b(agricultural|agriculatral|agri|நஞ்சை|புஞ்சை|தோட்டம்|wet\s*land|dry\s*land|house\s*site|residential)\s*(?:land|property|site)?\b', txt, re.I)
if class_m:
    print("Matched Classification:", class_m.group(0))
