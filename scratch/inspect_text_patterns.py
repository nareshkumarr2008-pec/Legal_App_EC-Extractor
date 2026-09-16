import sys
import os
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pdfplumber

pdf_path = "C:/Users/nares/Downloads/Sale Deed_3978_2010 - Naagesh.pdf"

with pdfplumber.open(pdf_path) as pdf:
    for i, p in enumerate(pdf.pages):
        txt = p.extract_text() or ""
        if "3978" in txt or "7126" in txt or "23,00,000" in txt or "1698" in txt:
            print(f"--- MATCH ON PAGE {i+1} ---")
            for line in txt.splitlines():
                if any(k in line for k in ["3978", "7126", "23,00,000", "1698", "BHUWAN", "22", "11", "2010"]):
                    print("  ", line)
