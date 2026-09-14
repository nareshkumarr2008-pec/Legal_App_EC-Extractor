import sys
sys.stdout.reconfigure(encoding='utf-8')
from app.extractors.ec_extractor import ECExtractor

pdf_path = r"C:\Users\nares\.gemini\antigravity-ide\brain\d334da03-d61c-47a1-ba36-7733443c83fd\.user_uploaded\media_1789384674570.pdf"
with open(pdf_path, 'rb') as f:
    pdf_bytes = f.read()

extractor = ECExtractor()
result = extractor.extract(pdf_bytes=pdf_bytes)
entries = result.get('transactions_table', {}).get('value', [])
print(f"Total entries: {len(entries)}")
for e in entries:
    print(f"\n  Sr {e['sr_no']} | Doc: {e['doc_no_year']}")
    print(f"  Executants raw: {e['executants']}")
    print(f"  Claimants raw:  {e['claimants']}")
    bilingual = e.get('executants_bilingual', [])
    print(f"  Executants bilingual ({len(bilingual)}):")
    for p in bilingual:
        print(f"    [{p['index']}] EN: {p['english']}  TA: {p['tamil']}  role: {p['role_english']}")
    cbil = e.get('claimants_bilingual', [])
    print(f"  Claimants bilingual ({len(cbil)}):")
    for p in cbil:
        print(f"    [{p['index']}] EN: {p['english']}  TA: {p['tamil']}")
