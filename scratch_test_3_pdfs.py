# -*- coding: utf-8 -*-
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
from app.extractors.ec_extractor import ECExtractor

folder = r'C:\Users\nares\Downloads'
files = [
    ('PDF 1 (6 pages)', 'Paid EC for the period from  01.01.1975 to 21.05.2025.pdf'),
    ('PDF 2 (16 pages)', 'EC -3- 01.01.1975 to 24.06.2024.pdf'),
    ('PDF 3 (25 pages)', 'EC (1).pdf')
]

extractor = ECExtractor()

for label, filename in files:
    print('=' * 60)
    print(f'Testing {label}: {filename}')
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        print(f'File not found: {path}')
        continue

    with open(path, 'rb') as f:
        pdf_bytes = f.read()

    t0 = time.time()
    try:
        res = extractor.extract(pdf_bytes=pdf_bytes)
        dur = time.time() - t0
        print(f'Extracted in {dur:.2f}s')
        for k in ['sro_office', 'village', 'survey_numbers', 'search_period', 'certificate_date', 'total_transactions', 'form_type']:
            val = res.get(k, {}).get('value') if isinstance(res.get(k), dict) else res.get(k)
            print(f'  {k}: {val}')
        txs = res.get('transactions_table', {}).get('value', [])
        print(f'  Transactions parsed: {len(txs)}')
        for t in txs[:5]:
            print(f"    #{t.get('sr_no')}: doc={t.get('doc_no_year')} | nat={t.get('nature')} | exec={t.get('executants')[:25] if t.get('executants') else ''} | claim={t.get('claimants')[:25] if t.get('claimants') else ''}")
        if len(txs) > 5:
            print(f"    ... and {len(txs) - 5} more transactions")
    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()

print('=' * 60)
