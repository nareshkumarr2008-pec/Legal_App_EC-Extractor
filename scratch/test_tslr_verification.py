# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')

import pdfplumber
from app.extractors.tslr_extractor import TSLRExtractor

ext = TSLRExtractor()
pdf_path = r"C:\Users\nares\Downloads\TSLR tst 1.pdf"
with pdfplumber.open(pdf_path) as pdf:
    text = pdf.pages[0].extract_text()
    res = ext.extract(text)

print("=== EXTRACTION RESULT FOR TSLR tst 1.pdf ===")
print("Survey Number    :", res["survey_number"]["value"])
print("Old Survey Number:", repr(res["old_survey_number"]["value"]))
print("Old Survey No    :", repr(res["old_survey_no"]["value"]))
print("Owner Name       :", res["owner_name"]["value"])
print("Ward + Block     :", res["ward_block"]["value"])
print("Door No          :", res["municipal_door_no"]["value"])
print("Assessment       :", res["assessment"]["value"])
print("Remarks          :", res["remarks"]["value"])

assert res["old_survey_number"]["value"] == "380/1A1C", f"Expected 380/1A1C, got {res['old_survey_number']['value']}"
print("--> SUCCESS: Old survey number is 380/1A1C!")
