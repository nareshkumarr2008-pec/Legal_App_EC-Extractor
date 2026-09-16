import re

deeds = [
    ('1995', 'scratch/ocr_text_1995.txt'),
    ('2004', 'scratch/ocr_text_2004.txt'),
    ('2010', 'scratch/ocr_text_2010.txt'),
]

for label, fpath in deeds:
    with open(fpath, encoding='utf-8') as f:
        text = f.read()

    norm = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    norm = re.sub(r'(\d+)([a-zA-Z]+)', r'\1 \2', norm)

    HEREINAFTER_PAT = r'(?:herein|heiein|herei|here|here\s*in)[\s-]*aft[eo]r'

    p_m = re.search(
        r'(?:TO\s+AND\s+IN\s+FAVOUR\s+OF\s*[:\s]*|in\s+favour\s+of\s*[:\s]*|\bAND\s+(?=(?:Mr|Mrs|Ms|Tmt|Thiru|Smt|Selvi|[A-Z][a-z]+)))'
        r'(.+?)'
        r'(?:,\s*|\s+)' + HEREINAFTER_PAT + r'\s+(?:called|referred\s+to\s+as)\s+(?:the\s+)?[\'\"“\s]*(?:PURCHASER|BUYER|CLAIMANT)',
        norm,
        re.IGNORECASE | re.DOTALL
    )

    if p_m:
        print(f"[{label}] SUCCESS: {p_m.group(1)[:100].replace(chr(10), ' ')}")
    else:
        print(f"[{label}] FAILED")
