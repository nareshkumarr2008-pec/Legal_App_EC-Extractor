import os
import sys
sys.path.insert(0, ".")

from app.extractor import DocumentExtractor
from app.pdf_generator import generate_ocr_pdf_report

def test_pdf():
    extractor = DocumentExtractor()

    # Test 1995
    with open("scratch/ocr_text_1995.txt", "r", encoding="utf-8") as f:
        text_1995 = f.read()

    res_1995 = extractor.extract(text_1995, doc_type="sale_deed", filename="Sale deed_6027_1995.pdf")
    payload_1995 = {
        "filename": "Sale deed_6027_1995.pdf",
        "doc_type": "sale_deed",
        "fields": res_1995.get("fields", {}),
        "checklist": res_1995.get("checklist", []),
        "risk_assessment": res_1995.get("risk_assessment", {}),
        "total_pages": 22
    }
    pdf_bytes_1995 = generate_ocr_pdf_report(payload_1995, lang="both")
    out_1995 = "scratch/test_report_1995.pdf"
    with open(out_1995, "wb") as f:
        f.write(pdf_bytes_1995)
    print(f"Generated 1995 PDF report successfully: {out_1995}, size: {len(pdf_bytes_1995)} bytes")

    # Test 2004
    with open("scratch/ocr_text_2004.txt", "r", encoding="utf-8") as f:
        text_2004 = f.read()

    res_2004 = extractor.extract(text_2004, doc_type="sale_deed", filename="Sale deed_188_2004.pdf")
    payload_2004 = {
        "filename": "Sale deed_188_2004.pdf",
        "doc_type": "sale_deed",
        "fields": res_2004.get("fields", {}),
        "checklist": res_2004.get("checklist", []),
        "risk_assessment": res_2004.get("risk_assessment", {}),
        "total_pages": 14
    }
    pdf_bytes_2004 = generate_ocr_pdf_report(payload_2004, lang="both")
    out_2004 = "scratch/test_report_2004.pdf"
    with open(out_2004, "wb") as f:
        f.write(pdf_bytes_2004)
    print(f"Generated 2004 PDF report successfully: {out_2004}, size: {len(pdf_bytes_2004)} bytes")

    # Test 2010
    with open("scratch/ocr_text_2010.txt", "r", encoding="utf-8") as f:
        text_2010 = f.read()

    res_2010 = extractor.extract(text_2010, doc_type="sale_deed", filename="Sale Deed_3978_2010 - Naagesh.pdf")
    payload_2010 = {
        "filename": "Sale Deed_3978_2010 - Naagesh.pdf",
        "doc_type": "sale_deed",
        "fields": res_2010.get("fields", {}),
        "checklist": res_2010.get("checklist", []),
        "risk_assessment": res_2010.get("risk_assessment", {}),
        "total_pages": 25
    }
    pdf_bytes_2010 = generate_ocr_pdf_report(payload_2010, lang="both")
    out_2010 = "scratch/test_report_2010.pdf"
    with open(out_2010, "wb") as f:
        f.write(pdf_bytes_2010)
    print(f"Generated 2010 PDF report successfully: {out_2010}, size: {len(pdf_bytes_2010)} bytes")

if __name__ == "__main__":
    test_pdf()
