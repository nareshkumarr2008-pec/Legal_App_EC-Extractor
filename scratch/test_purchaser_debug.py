import re
from app.extractors.sale_deed_extractor import SaleDeedExtractor

with open('scratch/ocr_text_2010.txt', encoding='utf-8') as f:
    text = f.read()

ext = SaleDeedExtractor()
res = ext.extract(text)
print("PREV OWNER:", res.get("history_previous_owner", {}).get("value"))
print("MOTHER DEED:", res.get("previous_doc_reference", {}).get("value"))

