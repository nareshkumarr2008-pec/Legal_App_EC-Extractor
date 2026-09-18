import sys
import os
from app.extractors.patta_extractor import PattaExtractor
from app.extractors.tslr_extractor import TSLRExtractor
from app.pdf_generator import generate_ocr_pdf_report

def test_reports():
    print("Testing Patta PDF report generation...")
    pe = PattaExtractor()
    sample_patta_text = """
    தமிழ்நாடு அரசு
    வருவாய் மற்றும் பேரிடர் மேலாண்மைத் துறை
    நில உரிமை விவரங்கள் : இ.எண் 10(1) பிரிவு
    மாவட்டம் : செங்கல்பட்டு    வட்டம் : தாம்பரம்
    வருவாய் கிராமம் : செம்பாக்கம்    பட்டா எண் : 242
    உரிமையாளர்கள் பெயர் :
    சின்னக்கண்ணு மகன் ரங்கநாதன்
    புல எண் : 128/7
    ரயத்துவாரி மனை
    பரப்பு : 0.00.06 ஹெக்
    தீர்வை : ரூ. 2.00
    22/01/2024 at 05:47:27 PM
    Kavitha S (Tahsildar)
    S/NA/35/05/128/00242/20878
    15-09-2026 at 08:42:26 AM
    """
    p_fields = pe.extract(sample_patta_text)
    p_chk = pe.evaluate_checklist(p_fields, sample_patta_text)
    p_payload = {
        "doc_type": "patta",
        "filename": "patta tst 1.pdf",
        "page_count": 2,
        "fields": p_fields,
        "extraction": {
            "fields": p_fields,
            "checklist": p_chk
        }
    }
    p_pdf = generate_ocr_pdf_report(p_payload, lang="both")
    with open("scratch/test_patta_out.pdf", "wb") as f:
        f.write(p_pdf)
    print(f"Patta PDF generated: {len(p_pdf)} bytes")

    print("\nTesting TSLR PDF report generation...")
    te = TSLRExtractor()
    sample_tslr_text = """
    District : Chengalpattu Taluk : Tambaram Town : Tambaram Ward : Ward-CTambaram
    URB/35/05/003/003/0027/2/0
    Sl.No 1
    2/0
    357/A,B-/358/A,B-359A,361/364/366/368/1,2-3691-2,370/1-357/1A-1B/358/1A1B,393/394/395/396/397
    Ward-CTambaram, Block 0027
    Door No : -
    Name : -
    Government (சர்க்கார் / அரசு)
    Government Poramboke (புறம்போக்கு)
    30 Hectare, 14 Are(s), 5.0 Sq.Meter(s)
    Municipal=-, Govt=0.00
    TR DT: 21-01-2020
    SARAVANNAN V — Tahsildar
    21-01-2020
    16-09-2026 at 08:05:24 AM
    """
    t_fields = te.extract(sample_tslr_text)
    t_chk = te.evaluate_checklist(t_fields, sample_tslr_text)
    t_payload = {
        "doc_type": "tslr",
        "filename": "TSLR tst 2.pdf",
        "page_count": 2,
        "fields": t_fields,
        "extraction": {
            "fields": t_fields,
            "checklist": t_chk
        }
    }
    t_pdf = generate_ocr_pdf_report(t_payload, lang="both")
    with open("scratch/test_tslr_out.pdf", "wb") as f:
        f.write(t_pdf)
    print(f"TSLR PDF generated: {len(t_pdf)} bytes")

if __name__ == "__main__":
    test_reports()
