import sys, os
sys.stdout.reconfigure(encoding='utf-8')
import pdfplumber

f1 = r'C:\Users\nares\.gemini\antigravity-ide\brain\3e9977d8-8e3e-4809-8f0a-b5f029072d75\.user_uploaded\media_1789732668395.pdf'
f2 = r'C:\Users\nares\.gemini\antigravity-ide\brain\3e9977d8-8e3e-4809-8f0a-b5f029072d75\.user_uploaded\media_1789732679709.pdf'

for fname, path in [("PDF 1", f1), ("PDF 2", f2)]:
    print(f"\n==================== {fname} ====================")
    with pdfplumber.open(path) as p:
        print(f"Pages: {len(p.pages)}")
        for idx, page in enumerate(p.pages):
            print(f"--- Page {idx+1} ---")
            txt = page.extract_text() or ""
            print(txt[:1000])
