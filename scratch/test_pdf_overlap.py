import sys
import os
sys.path.insert(0, os.path.abspath("."))

from app.pdf_generator import generate_ocr_pdf_report
from app.extractors.sale_deed_extractor import SaleDeedExtractor
import json

sample_data = {
    "filename": "Sale_Deed_3978_2010.pdf",
    "doc_type": "sale_deed",
    "page_count": 35,
    "fields": {
        "vendor_details": {
            "label": "Vendor / Executant Details (விற்பவர் விவரம்)",
            "value": "Mr. N. MUTHUKARUPPAN, Son of late M.N. Gopal, residing at No. 6/2, Sri Ramar Street, Devaraj Nagar, Saligramam, Chennai - 600093 (Represented by their Power of Attorney Agent Mr.JAMAL ASAN ALIYAR, Managing Director of M/s. Apollo Estates & Builders (P) Ltd)",
            "confidence": 0.98
        },
        "previous_doc_reference": {
            "label": "முந்தைய மூல ஆவணக் குறிப்பு (Mother Deed Reference)",
            "value": "Doc No. 7126 of 1995 (Dated 14.12.1995) at SRO Kodambakkam in Book 1, Volume 123, Pages from 45 to 60",
            "confidence": 0.94
        },
        "survey_number": {
            "label": "புல எண் (Survey Number / S No)",
            "value": "new survey No.78 of Block No.1",
            "confidence": 0.95
        }
    }
}

for l in ["en", "ta", "both"]:
    try:
        pdf_bytes = generate_ocr_pdf_report(sample_data, lang=l)
        out_path = f"scratch/test_report_{l}.pdf"
        with open(out_path, "wb") as f:
            f.write(pdf_bytes)
        print(f"Generated {out_path}: {len(pdf_bytes)} bytes")
    except Exception as e:
        print(f"Failed for lang {l}: {e}")
        import traceback
        traceback.print_exc()
