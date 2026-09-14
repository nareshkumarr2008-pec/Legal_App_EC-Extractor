import os
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')
from app.extractors.ec_extractor import ECExtractor

path = r'C:\Users\nares\Downloads\EC (1).pdf'
print(f'Testing PDF 3: {path}', flush=True)

extractor = ECExtractor()
t0 = time.time()
with open(path, 'rb') as f:
    pdf_bytes = f.read()

res = extractor.extract(pdf_bytes=pdf_bytes)
print(f'Extracted in {time.time()-t0:.2f}s', flush=True)
for k in ['sro_office', 'village', 'survey_numbers', 'search_period', 'certificate_date', 'total_transactions', 'form_type']:
    val = res.get(k, {}).get('value') if isinstance(res.get(k), dict) else res.get(k)
    print(f'  {k}: {val}')

txs = res.get('transactions_table', {}).get('value', [])
print(f'Transactions parsed: {len(txs)}')
for t in txs[:5]:
    sr = t.get('sr_no')
    doc = t.get('doc_no_year')
    nat = t.get('nature')
    ex = t.get('executants')
    cl = t.get('claimants')
    print(f'  #{sr}: doc={doc} | nat={nat} | exec={ex} | cl={cl}')
