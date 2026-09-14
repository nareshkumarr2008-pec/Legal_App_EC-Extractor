# -*- coding: utf-8 -*-
"""
Automated unit tests for the 10 real estate document categories,
strict field extraction, cross-check matrix, and inheritance track.
"""

import unittest
from fastapi.testclient import TestClient
from app.server import app
from app.samples import DOCUMENT_CATEGORIES, SAMPLE_DOCUMENTS, MULTI_DOC_BUNDLES
from app.extractor import DocumentExtractor
from app.cross_checker import CrossVerificationEngine

class TestPropertyDocumentOCR(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.extractor = DocumentExtractor()
        self.cross_engine = CrossVerificationEngine()

    def test_categories_integrity(self):
        """Verify document categories requested by user are registered."""
        expected_10 = [
            "sale_deed", "patta", "parent_docs", "ec", "building_plan",
            "rera", "tax_eb", "layout_approval", "death_legal_heir", "loan_docs"
        ]
        cat_ids = [c["id"] for c in DOCUMENT_CATEGORIES]
        self.assertGreaterEqual(len(cat_ids), 10)
        for expected in expected_10:
            self.assertIn(expected, cat_ids)

    def test_deep_sale_deed_extraction(self):
        """Verify strict extraction of Sale deed: Vendor, Purchaser, Schedule, Boundary, SRO."""
        sample = SAMPLE_DOCUMENTS["sale_deed"]
        extracted = self.extractor.extract(sample["raw_text"], doc_type="sale_deed")
        fields = extracted["fields"]

        self.assertIn("vendor_details", fields)
        self.assertIn("purchaser_details", fields)
        self.assertIn("schedule_property_type", fields)
        self.assertIn("survey_number", fields)
        self.assertIn("land_extent", fields)
        self.assertTrue("boundaries" in fields or "boundary" in fields)
        self.assertIn("sro_details", fields)
        self.assertIn("RAJENDRAN", fields["vendor_details"]["value"])

    def test_dynamic_ec_header_extraction(self):
        """Verify zero-fallback dynamic extraction of EC header fields."""
        sample_text = """OAT
Certificate of Encumbrance on Property
சொத்துதொடர்பானவில்லங்கச் சான்று
S.R.O/சா.ப.அ: Chengleput JointI
Date / நாள்: 04-Sep-2026
Village /கிராமம்:Alappakkam
SurveyDetails /சர்வேவிவரம்: 35
Data Availability Period for Village: Alappakkam
Chengleput Joint I Sub Registrar Office: From 01-Jan-2003 To 03-Sep-2026
Search Period/தடுதல் காலம்: 01-Jan-2003 - 03-Sep-2026
"""
        extracted = self.extractor.extract(sample_text, doc_type="ec")
        fields = extracted["fields"]

        self.assertEqual(fields["survey_searched"]["value"], "35")
        self.assertEqual(fields["search_period"]["value"], "01-Jan-2003 to 03-Sep-2026")
        self.assertEqual(fields["sro_available_from"]["value"], "From 01-Jan-2003 To 03-Sep-2026")
        self.assertEqual(fields["village"]["value"], "Alappakkam (அலப்பாக்கம்)")
        self.assertEqual(fields["district"]["value"], "Chengalpattu (செங்கல்பட்டு)")

    def test_cross_verification_standard_bundle(self):
        """Verify standard cross-check matrix passes all 7 checks on genuine bundle."""
        bundle = MULTI_DOC_BUNDLES["standard_sale_bundle"]["documents"]
        matrix_res = self.cross_engine.run_standard_cross_check(bundle)

        self.assertEqual(matrix_res["overall_status"], "PASS")
        self.assertEqual(matrix_res["red_flags_count"], 0)
        self.assertEqual(matrix_res["checks_passed"], 7)

    def test_poramboke_fraud_detection(self):
        """Verify Poramboke Fraud bundle triggers Critical Alert."""
        fraud_bundle = MULTI_DOC_BUNDLES["fraud_alert_bundle"]["documents"]
        matrix_res = self.cross_engine.run_standard_cross_check(fraud_bundle)

        self.assertEqual(matrix_res["overall_status"], "ACTION REQUIRED")
        self.assertGreaterEqual(matrix_res["red_flags_count"], 1)

    def test_inheritance_track_verification(self):
        """Verify Death Certificate & Legal Heir Certificate (Varisu) verification track."""
        bundle = MULTI_DOC_BUNDLES["inherited_property_bundle"]["inheritance_data"]
        inh_res = self.cross_engine.run_inheritance_track_check(bundle)

        self.assertEqual(inh_res["overall_status"], "PASS")
        self.assertTrue(inh_res["hard_gate_passed"])
        self.assertEqual(inh_res["total_heirs_count"], 4)
        self.assertEqual(inh_res["accounted_heirs_count"], 4)

    def test_api_bundles_endpoint(self):
        """Test /api/bundles and /api/bundle/{id}."""
        res = self.client.get("/api/bundles")
        self.assertEqual(res.status_code, 200)

        b_res = self.client.get("/api/bundle/standard_sale_bundle")
        self.assertEqual(b_res.status_code, 200)
        b_data = b_res.json()
        self.assertEqual(b_data["cross_check"]["overall_status"], "PASS")

    def test_tslr_canonical_fields(self):
        """Verify TSLR exact canonical fields extraction."""
        sample = SAMPLE_DOCUMENTS["tslr"]
        extracted = self.extractor.extract(sample["raw_text"], doc_type="tslr")
        fields = extracted["fields"]

        self.assertIn("district", fields)
        self.assertIn("taluk", fields)
        self.assertIn("town_village", fields)
        self.assertEqual(fields["town_village"]["label"], "Town")
        self.assertIn("ward", fields)
        self.assertIn("owner_name", fields)
        self.assertEqual(fields["owner_name"]["label"], "Name")
        self.assertIn("survey_number", fields)
        self.assertIn("extent", fields)
        self.assertIn("ward_block", fields)
        self.assertIn("land_classification", fields)
        self.assertIn("current_land_use", fields)
        self.assertIn("tenure_type", fields)
        self.assertIn("assessment", fields)
        self.assertIn("remarks", fields)

    def test_tamil_tslr_extraction(self):
        """Verify 100% extraction for Tamil TSLR document with zero OCR label noise."""
        tamil_tslr_text = """தமிழ்நாடு அரசு
வருவாய்த் துறை
நகர நில அளவை பதிவேடு சான்று
EXTRACT FROM THE TOWN SURVEY LAND REGISTER

மாவட்டம் / District : விழுப்புரம்
வட்டம் / Taluk : விழுப்புரம்
நகரம் / Town : வடமங்கலம்
வார்டு / Ward : -

வ.எண் | தொகுதி | நகர சர்வே எண் | உட்பிரிவு | பழைய சர்வே எண் | நில வகைப்பாடு | தற்போதைய பயன்பாடு | உரிமை வகை | பரப்பளவு (ஹெக் - ஏர் - ச.மீ) | தீர்வை (முனிசிபல் - அரசு) | பெயர் / Name | குறிப்பு
1 | 01 | 35 | 2 | 249/3A | ரயத்துவாரி மனை | கட்டிடம் | ரயத்துவாரி | 0.00 0 04 50.0 | - 1 | / Name : GANESAN R (Tamil: / னமெ : கணேஸன் ர) | 2023/0153/02/047290TR DT. 2023-11-30
"""
        extracted = self.extractor.extract(tamil_tslr_text, doc_type="tslr")
        fields = extracted["fields"]

        self.assertIn("Villupuram", fields["district"]["value"])
        self.assertIn("விழுப்புரம்", fields["district"]["value"])
        self.assertIn("Villupuram", fields["taluk"]["value"])
        self.assertIn("Vadamangalam", fields["town_village"]["value"])
        self.assertEqual(fields["ward"]["value"], "-")
        self.assertIn("GANESAN R", fields["owner_name"]["value"])
        self.assertNotIn("/ Name", fields["owner_name"]["value"])
        self.assertNotIn("/ னமெ", fields["owner_name"]["value"])
        self.assertIn("35/2", fields["survey_number"]["value"])
        self.assertIn("249/3A", fields["survey_number"]["value"])
        self.assertIn("04 Are(s), 50.0 Sq.Meter(s)", fields["extent"]["value"])
        self.assertEqual(fields["ward_block"]["value"], "Block 01")
        self.assertEqual(fields["land_classification"]["value"], "Ryotwari House-site (Manai)")
        self.assertEqual(fields["current_land_use"]["value"], "Building --> Non-agricultural")
        self.assertEqual(fields["tenure_type"]["value"], "Ryotwari")
        self.assertEqual(fields["assessment"]["value"], "Municipal=-, Govt=1")
        self.assertEqual(fields["remarks"]["value"], "2023/0153/02/047290TR DT. 2023-11-30")

    def test_ec_table_values_ordering_and_separation(self):
        """Verify strict ordering and non-duplicated executant/claimant separation in EC tables."""
        sample = SAMPLE_DOCUMENTS["ec"]
        extracted = self.extractor.extract(sample["raw_text"], doc_type="ec")
        tx_list = extracted["fields"]["transactions_table"]["value"]

        self.assertEqual(len(tx_list), 4)
        
        # Entry 1: Sale deed
        self.assertEqual(tx_list[0]["doc_no"], "1820/2008")
        self.assertEqual(tx_list[0]["executants"], "Classic Foundations Pvt Ltd")
        self.assertEqual(tx_list[0]["claimants"], "K. Rajendran")
        self.assertEqual(tx_list[0]["consideration"], "Rs. 32,00,000/-")
        self.assertEqual(tx_list[0]["pr_number"], "450/1995")

        # Entry 2: MODT - State Bank of India
        self.assertEqual(tx_list[1]["doc_no"], "2910/2012")
        self.assertEqual(tx_list[1]["executants"], "K. Rajendran")
        self.assertEqual(tx_list[1]["claimants"], "State Bank of India")
        self.assertEqual(tx_list[1]["consideration"], "Rs. 25,00,000/-")
        self.assertEqual(tx_list[1]["pr_number"], "1820/2008")

        # Entry 3: Receipt - Discharge
        self.assertEqual(tx_list[2]["doc_no"], "640/2018")
        self.assertEqual(tx_list[2]["executants"], "State Bank of India")
        self.assertEqual(tx_list[2]["claimants"], "K. Rajendran")
        self.assertEqual(tx_list[2]["consideration"], "Rs. 25,00,000/-")

        # Entry 4: Sale deed to Lakshmi Priya
        self.assertEqual(tx_list[3]["doc_no"], "4521/2023")
        self.assertEqual(tx_list[3]["executants"], "K. Rajendran")
        self.assertEqual(tx_list[3]["claimants"], "S. Lakshmi Priya")
        self.assertEqual(tx_list[3]["consideration"], "Rs. 75,00,000/-")

    def test_tamil_ec_table_extraction(self):
        """Verify 100% accurate segmentation and label-anchored separation for Tamil EC."""
        tamil_ec_text = """தமிழ்நாடு அரசு - பதிவுத்துறை
சொத்து தொடர்பான வில்லங்கச் சான்று
FORM NO. 15 (படிவம் எண் 15)
சார்பதிவாளர் அலுவலகம்: ஆலந்தூர் (Alandur)
நாள்: 01-Sep-2026
கிராமம்: நங்கநல்லூர் (Nanganallur)
சர்வே எண்: 120/1A
தேடுதல் காலம்: 01-Jan-2005 முதல் 31-Aug-2026 வரை

105/2006
12/03/2006
12/03/2006
12/03/2006
கிரைய ஆவணம் (Conveyance)
எழுதிக்கொடுத்தவர்:
1. வி. குப்பராஜ் (V. Kuppa Raj)
2. வி. ஜெயலட்சுமி (V. Jayalakshmi)
எழுதிவாங்கியவர்:
1. எம். புகழேந்தி (M. Pugazhendhi)
கைமாற்றுத் தொகை: Rs. 42,50,000/-
சந்தை மதிப்பு: Rs. 45,00,000/-
முந்தைய ஆவண எண்: 890/1998
சொத்தின் வகைப்பாடு: மனை மற்றும் கட்டிடம்
சொத்தின் விஸ்தீர்ணம்: 2400 சதுர அடி
எல்லை விவரங்கள்: வடக்கில் 24 அடி ரோடு, தெற்கில் சபாபதி மனை, கிழக்கில் மனை எண் 12, மேற்கில் மனை எண் 10

1560/2011
05-08-2011
05-08-2011
05-08-2011
அடமான ஆவணம் (MODT)
அடமானம் வைத்தவர்:
1. எம். புகழேந்தி
அடமானம் பெற்றவர்:
1. ஸ்டேட் பேங்க் ஆப் இந்தியா (State Bank of India)
கைமாற்றுத் தொகை: Rs. 30,00,000/-
சந்தை மதிப்பு: Rs. 30,00,000/-
முந்தைய ஆவண எண்: 105/2006

420/2017
20-11-2017
20-11-2017
20-11-2017
அடமான விடுதலை ரசீது (Mortgage Discharge Receipt)
விடுதலை செய்தவர்:
1. ஸ்டேட் பேங்க் ஆப் இந்தியா
பெறுபவர்:
1. எம். புகழேந்தி
கைமாற்றுத் தொகை: Rs. 30,00,000/-
முந்தைய ஆவண எண்: 1560/2011
"""
        extracted = self.extractor.extract(tamil_ec_text, doc_type="ec")
        tx_list = extracted["fields"]["transactions_table"]["value"]

        # Exactly 3 entries - no false splits on PR numbers
        self.assertEqual(len(tx_list), 3)

        self.assertEqual(tx_list[0]["doc_no"], "105/2006")
        self.assertEqual(tx_list[0]["date"], "12-Mar-2006")
        self.assertIn("V. Kuppa Raj", tx_list[0]["executants"])
        self.assertIn("V. Jayalakshmi", tx_list[0]["executants"])
        self.assertEqual(tx_list[0]["claimants"], "M. Pugazhendhi")
        self.assertEqual(tx_list[0]["consideration"], "Rs. 42,50,000/-")
        self.assertEqual(tx_list[0]["pr_number"], "890/1998")

        self.assertEqual(tx_list[1]["doc_no"], "1560/2011")
        self.assertEqual(tx_list[1]["date"], "05-Aug-2011")
        self.assertEqual(tx_list[1]["executants"], "M. Pugazhendhi")
        self.assertEqual(tx_list[1]["claimants"], "State Bank of India")
        self.assertEqual(tx_list[1]["consideration"], "Rs. 30,00,000/-")
        self.assertEqual(tx_list[1]["pr_number"], "105/2006")

        self.assertEqual(tx_list[2]["doc_no"], "420/2017")
        self.assertEqual(tx_list[2]["date"], "20-Nov-2017")
        self.assertEqual(tx_list[2]["executants"], "State Bank of India")
        self.assertEqual(tx_list[2]["claimants"], "M. Pugazhendhi")
        self.assertEqual(tx_list[2]["consideration"], "Rs. 30,00,000/-")
        self.assertEqual(tx_list[2]["pr_number"], "1560/2011")

    def test_ec_pdf_report_generation(self):
        """Verify EC PDF Report generates cleanly with zero tofu issues."""
        from app.pdf_generator import generate_ocr_pdf_report
        sample = SAMPLE_DOCUMENTS["ec"]
        extracted = self.extractor.extract(sample["raw_text"], doc_type="ec")
        data = {
            "filename": "Sample_EC.pdf",
            "doc_type": "ec",
            "total_pages": 1,
            "extraction": extracted
        }
        pdf_bytes = generate_ocr_pdf_report(data)
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_extraction_validator_and_safeguards(self):
        """Verify deterministic safeguards for Survey No, DPDP Masked Aadhaar, and Poramboke."""
        from app.validator import ExtractionValidator

        # 1. Survey & Subdivision Validation
        ocr_stream = "Property situated at Survey No. 142/2B, Alappakkam Village"
        res_valid = ExtractionValidator.validate_survey_and_subdivision("142/2B", ocr_stream)
        self.assertTrue(res_valid["valid"])
        self.assertFalse(res_valid["needs_review"])

        res_diverged = ExtractionValidator.validate_survey_and_subdivision("142/28", ocr_stream)
        self.assertFalse(res_diverged["valid"])
        self.assertTrue(res_diverged["needs_review"])
        self.assertEqual(res_diverged["suggested_value"], "142/2B")

        # 2. DPDP Masked Aadhaar enforcement
        masked_1 = ExtractionValidator.enforce_dpdp_masking("1234 5678 9012")
        self.assertEqual(masked_1, "XXXX-XXXX-9012")

        masked_2 = ExtractionValidator.enforce_dpdp_masking("XXXX-XXXX-4567")
        self.assertEqual(masked_2, "XXXX-XXXX-4567")

        # 3. Poramboke Detection
        is_p1, p_desc1 = ExtractionValidator.check_poramboke_status("Government Poramboke Waterbody")
        self.assertTrue(is_p1)
        self.assertIn("Poramboke", p_desc1)

        is_p2, p_desc2 = ExtractionValidator.check_poramboke_status("Ryotwari Patta Land")
        self.assertFalse(is_p2)
        self.assertIn("Private", p_desc2)

        # 4. Extent Normalization
        sqft_cents = ExtractionValidator.normalize_extent_to_sqft("5.25 Cents")
        self.assertAlmostEqual(sqft_cents, 5.25 * 435.6, places=1)

        sqft_grounds = ExtractionValidator.normalize_extent_to_sqft("2 Grounds")
        self.assertEqual(sqft_grounds, 4800.0)

    def test_patta_form10_extraction(self):
        """Verify 100% extraction for Patta Form 10(1) with joint ownership, extent, and revenue check."""
        patta_sample_text = """தமிழ்நாடு அரசு - வருவாய்த்துறை
நில உரிமை விபரங்கள் : 10(1) பிரிவு சான்று
PATTA EXTRACT - TAMIL NADU REVENUE DEPARTMENT

பட்டா எண்: 1092
உரிமையாளர்கள் பெயர்:
1. பக்கிரிசாமி மகன் கோவிந்தராசு
2. ஜெயலட்சுமி மனைவி பக்கிரிசாமி

மாவட்டம்: திருவாரூர்
வட்டம்: நன்னிலம்
வருவாய் கிராமம்: தூத்துக்குடி

புல எண் | உட்பிரிவு | நஞ்சை பரப்பு (ஹெக் - ஏர்)
30 | 3B | 0.28.50
30 | 5B | 0.11.50
மொத்தம் | 0.40.00
"""
        extracted = self.extractor.extract(patta_sample_text, doc_type="patta")
        fields = extracted["fields"]

        self.assertEqual(fields["patta_number"]["value"], "1092")
        self.assertIn("Pakkirisamy", fields["owner_name"]["value"])
        self.assertIn("30-3B", fields["survey_numbers"]["value"])
        self.assertIn("30-5B", fields["survey_numbers"]["value"])
        self.assertIn("Thiruvarur", fields["district"]["value"])
        self.assertIn("Nannilam", fields["taluk"]["value"])
        self.assertIn("Thoothukudi", fields["village"]["value"])
        self.assertIn("0.28.50", fields["extent_details"]["value"])
        self.assertIn("Nanjai (Wet", fields["nature_of_land"]["value"])
        self.assertIn("Used to confirm", fields["revenue_owner_confirmation"]["value"])

    def test_llm_status_endpoint(self):
        """Verify /api/llm/status reports model name, base url, and fallback status."""
        res = self.client.get("/api/llm/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("llm_available", data)
        self.assertIn("recommended_model", data)
        self.assertEqual(data["recommended_model"], "Qwen2.5-7B-Instruct-GGUF (Q4_K_M)")

    def test_party_names_transliteration_and_clean_initials(self):
        """Verify proper transliteration and clean initials for Mohan, Krishnammal, Swami, Krishnan, etc."""
        from app.deep_translate_verifier import bilingual_party_list

        raw = "1. G.. ராமானுஜம் (பிரின்சிபல்) 2. R.. கிருஷ்ணம்மாள் (பிரின்சிபல்) 3. R.. மோகன் (பிரின்சிபல்) 4. அலேக் குமார் குலிசா (Alok Kumar Gulechha) (ஏஜண்ட்)"
        parties = bilingual_party_list(raw)
        self.assertEqual(len(parties), 4)

        # 1. G. Ramanujam (clean initials, standard Ramanujam spelling)
        self.assertEqual(parties[0]["english"], "G. Ramanujam")
        self.assertEqual(parties[0]["tamil"], "G. ராமானுஜம்")
        self.assertEqual(parties[0]["role_english"], "Principal")
        self.assertTrue(parties[0]["verified"])

        # 2. R. Krishnammal (Krishnammal not Kirushnammaal)
        self.assertEqual(parties[1]["english"], "R. Krishnammal")
        self.assertEqual(parties[1]["tamil"], "R. கிருஷ்ணம்மாள்")
        self.assertTrue(parties[1]["verified"])

        # 3. R. Mohan (Mohan not Mokan)
        self.assertEqual(parties[2]["english"], "R. Mohan")
        self.assertEqual(parties[2]["tamil"], "R. மோகன்")
        self.assertTrue(parties[2]["verified"])

        # 4. Single-party lists with initials
        krishnan_parties = bilingual_party_list("1. N.. கிருஷ்ணன்")
        self.assertEqual(krishnan_parties[0]["english"], "N. Krishnan")
        self.assertEqual(krishnan_parties[0]["tamil"], "N. கிருஷ்ணன்")
        self.assertTrue(krishnan_parties[0]["verified"])

        swami_parties = bilingual_party_list("1. B.N.. சுவாமி")
        self.assertEqual(swami_parties[0]["english"], "B.N. Swami")
        self.assertEqual(swami_parties[0]["tamil"], "B.N. சுவாமி")
        self.assertTrue(swami_parties[0]["verified"])

        # 5. Doctor title and Visweswara Reddy with role
        doc_parties = bilingual_party_list("1. P. டாக்டர்.விஸ்வேஸ்வர ரெட்டி (பிரின்சிபல்)")
        self.assertEqual(doc_parties[0]["english"], "P. Dr. Visweswara Reddy")
        self.assertEqual(doc_parties[0]["role_english"], "Principal")
        self.assertEqual(doc_parties[0]["role_tamil"], "பிரின்சிபல்")
        self.assertTrue(doc_parties[0]["verified"])

        # Bilingual role tag in parens: (Principal / பிரின்சிபல்)
        doc_bi_role = bilingual_party_list("1. P. டாக்டர்.விஸ்வேஸ்வர ரெட்டி (Principal / பிரின்சிபல்)")
        self.assertEqual(doc_bi_role[0]["english"], "P. Dr. Visweswara Reddy")
        self.assertEqual(doc_bi_role[0]["role_english"], "Principal")
        self.assertEqual(doc_bi_role[0]["role_tamil"], "பிரின்சிபல்")

        # Doctor with Agent role
        agent_parties = bilingual_party_list("1. டாக்டர்.சங்கீதா விஸ்வேஸ்வர ரெட்டி (ஏஜெண்ட்)")
        self.assertEqual(agent_parties[0]["english"], "Dr. Sangeetha Visweswara Reddy")
        self.assertEqual(agent_parties[0]["role_english"], "Agent")

        # 6. Manga Devi / Mangadevi (-devi not -thevi)
        manga1 = bilingual_party_list("1. M. மங்கா தேவி")
        self.assertEqual(manga1[0]["english"], "M. Manga Devi")

        manga2 = bilingual_party_list("1. மங்காதேவி")
        self.assertEqual(manga2[0]["english"], "Mangadevi")

        # 7. Corporate / company name with OCR double kombu and combined Tamil marks
        corp_ta = "1. சென்னை அக்னி பிஸ்னஸ் & மேேனஜ்மெண்ட் சர்வீஸ் பிரைேவட் லிமிடெட்"
        corp_res = bilingual_party_list(corp_ta)
        self.assertEqual(corp_res[0]["english"], "Chennai Agni Business & Management Services Private Limited")
        self.assertEqual(corp_res[0]["tamil"], "சென்னை அக்னி பிஸ்னஸ் & மேனேஜ்மெண்ட் சர்வீஸ் பிரைவேட் லிமிடெட்")
        self.assertTrue(corp_res[0]["verified"])

        # Also verify phonetic / garbled English transliteration fixes
        corp_en = "1. Chennai Agni Pisnas & Meேnajmend Sarvees Piraiேvad Limided"
        corp_en_res = bilingual_party_list(corp_en)
        self.assertEqual(corp_en_res[0]["english"], "Chennai Agni Business & Management Services Private Limited")

    def test_legacy_font_detection_safeguards(self):
        """Verify modern Unicode Tamil fonts (NotoSansTamil) with empty parens are not falsely treated as legacy dropped fonts."""
        import re
        page_fonts = {"AAAAAA+NotoSansTamil-Regular", "AAAAAA+NotoSansTamil-Bold"}
        joined_text = "SRO Office ( ) Date: 29-Aug-2026 Village ( ) Survey ( )"

        _LEGACY_TAMIL_FONT_MARKERS = (
            "bamini", "tscu_", "tscii", "tam-tam", "tam_",
            "amudham", "elango", "tboomis", "shreetam", "vanavil",
            "kamban", "softview"
        )
        _MODERN_UNICODE_FONT_MARKERS = (
            "notosans", "noto sans", "lohit", "mukta", "tiro", "arial",
            "times", "helvetica", "calibri", "cambria", "georgia", "dejavu"
        )
        has_modern_font = any(
            marker in f.lower() for f in page_fonts for marker in _MODERN_UNICODE_FONT_MARKERS
        )
        has_legacy_tamil_font = (not has_modern_font) and any(
            marker in f.lower() for f in page_fonts for marker in _LEGACY_TAMIL_FONT_MARKERS
        )
        has_tamil_unicode = any('\u0b80' <= c <= '\u0bff' for c in joined_text)
        empty_paren_count = len(re.findall(r'\(\s*\)', joined_text))
        has_dropped_bilingual_text = has_legacy_tamil_font and (not has_tamil_unicode) and empty_paren_count >= 3

        self.assertTrue(has_modern_font)
        self.assertFalse(has_legacy_tamil_font)
        self.assertFalse(has_dropped_bilingual_text)

    def test_sneha_normalization_and_transliteration(self):
        """Verify 'ஸ்னேகா' does not get corrupted to 'ஸ்னகோ' and translates to 'Sneha'."""
        from app.translator import normalize_tamil_visual_order, transliterate_tamil_text
        from app.deep_translate_verifier import bilingual_party_list

        raw = "3. ஸ்னேகா ஸ்டீபன்"
        norm = normalize_tamil_visual_order(raw)
        self.assertEqual(norm, "3. ஸ்னேகா ஸ்டீபன்")

        res = bilingual_party_list(raw)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["tamil"], "ஸ்னேகா ஸ்டீபன்")
        self.assertTrue(res[0]["english"].startswith("Sneha"))

    def test_prakash_transliteration(self):
        """Verify 'உத்ரா பிரகாஷ்' translates to 'Uthra Prakash' (not Piragaash)."""
        from app.deep_translate_verifier import bilingual_party_list
        from app.translator import transliterate_tamil_text

        raw = "உத்ரா பிரகாஷ்"
        res = bilingual_party_list(raw)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["english"], "Uthra Prakash")
        self.assertNotIn("Piragaash", res[0]["english"])
        self.assertIn("Prakash", transliterate_tamil_text(raw))

    def test_elizabeth_and_za_names_transliteration(self):
        """Verify 'எலிசபத் மோகன்' translates to 'Elizabeth Mohan' and all 'za' names transliterate correctly."""
        from app.deep_translate_verifier import bilingual_party_list
        from app.translator import dynamic_english_to_tamil, dynamic_transliterate_tamil

        # 1. Elizabeth Mohan
        res = bilingual_party_list("1. எலிசபத் மோகன்")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["english"], "Elizabeth Mohan")
        self.assertEqual(res[0]["tamil"], "எலிசபத் மோகன்")
        self.assertTrue(res[0]["verified"])

        # Also test alternate Tamil spellings of Elizabeth
        self.assertEqual(dynamic_transliterate_tamil("எலிசபெத்"), "Elizabeth")
        self.assertEqual(dynamic_transliterate_tamil("எலிஸபத்"), "Elizabeth")
        self.assertEqual(dynamic_transliterate_tamil("எலிஸபெத்"), "Elizabeth")

        # 2. Key "za" names (Mirza, Hamza, Faizal, Raza, Farzana, Riyaz, Feroz, Zakir, Aziz, Nazeer Ahamed, Mumtaz, Shahnawaz, Imtiaz)
        za_test_cases = [
            ("1. மிர்சா", "Mirza"),
            ("1. ஹம்சா", "Hamza"),
            ("1. பைசல்", "Faizal"),
            ("1. ரசா", "Raza"),
            ("1. பர்சானா", "Farzana"),
            ("1. ரியாஸ்", "Riyaz"),
            ("1. பெரோஸ்", "Feroz"),
            ("1. ஜாகிர்", "Zakir"),
            ("1. அஜீஸ்", "Aziz"),
            ("1. நசீர் அகமது", "Nazeer Ahamed"),
            ("1. மும்தாஜ்", "Mumtaz"),
            ("1. ஷாநவாஸ்", "Shahnawaz"),
            ("1. இம்தியாஸ்", "Imtiaz"),
        ]
        for raw, expected_en in za_test_cases:
            party = bilingual_party_list(raw)
            self.assertEqual(party[0]["english"], expected_en)
            self.assertTrue(party[0]["verified"])

        # 3. English to Tamil reverse checks
        self.assertEqual(dynamic_english_to_tamil("Elizabeth Mohan"), "எலிசபத் மோகன்")
        self.assertEqual(dynamic_english_to_tamil("Mirza"), "மிர்சா")
        self.assertEqual(dynamic_english_to_tamil("Faizal"), "பைசல்")
        self.assertEqual(dynamic_english_to_tamil("Hamza"), "ஹம்சா")
        self.assertEqual(dynamic_english_to_tamil("Riyaz"), "ரியாஸ்")
        self.assertEqual(dynamic_english_to_tamil("Feroz"), "பெரோஸ்")

    def test_neetu_hinduja_icici_bank_lessor_lessee(self):
        """Verify Neetu M. Hinduja transliteration, ICICI Bank Limited, and Lessor/Lessee role detection."""
        from app.deep_translate_verifier import bilingual_party_list
        from app.translator import dynamic_english_to_tamil, dynamic_transliterate_tamil, format_bilingual_entity

        # 1. Neetu M. Hinduja transliteration
        neetu_parties = bilingual_party_list("2. Neetu.m. Hinduja")
        self.assertEqual(len(neetu_parties), 1)
        self.assertEqual(neetu_parties[0]["english"], "Neetu M. Hinduja")
        self.assertEqual(neetu_parties[0]["tamil"], "நீத்து எம். ஹிந்துஜா")
        self.assertTrue(neetu_parties[0]["verified"])

        # 2. ICICI Bank Limited (Lessee)
        icici_parties = bilingual_party_list("1. ICICI பேங்க் லிமிடெட் ( Lessee)")
        self.assertEqual(len(icici_parties), 1)
        self.assertEqual(icici_parties[0]["english"], "ICICI Bank Limited")
        self.assertEqual(icici_parties[0]["role_english"], "Lessee")
        self.assertEqual(icici_parties[0]["role_tamil"], "குத்தகைக்கு எடுத்தவர்")
        self.assertTrue(icici_parties[0]["verified"])

        # 3. Lessor parties
        lessor_parties = bilingual_party_list("1. John Baptist Lasrado (lessor) 2. Flavy Daisy Lasrado (lessor)")
        self.assertEqual(len(lessor_parties), 2)
        self.assertEqual(lessor_parties[0]["english"], "John Baptist Lasrado")
        self.assertEqual(lessor_parties[0]["role_english"], "Lessor")
        self.assertEqual(lessor_parties[0]["role_tamil"], "குத்தகைக்கு விட்டவர்")
        self.assertTrue(lessor_parties[0]["verified"])

        # 4. Agni Estates & Foundations OCR typo fixes
        agni_parties = bilingual_party_list("1. Agni Esteds & Foundation Private Limited (agni Estates & Foundatiosn PVT Ltd)")
        self.assertEqual(agni_parties[0]["english"], "Agni Estates & Foundation Private Limited (Agni Estates & Foundations PVT LTD)")
        self.assertTrue(agni_parties[0]["verified"])

        # 5. Direct vocabulary checks
        self.assertEqual(dynamic_transliterate_tamil("பேங்க்"), "Bank")
        self.assertEqual(dynamic_transliterate_tamil("வங்கி"), "Bank")
        self.assertIn(dynamic_english_to_tamil("Bank"), ["வங்கி", "பேங்க்"])
        self.assertEqual(dynamic_english_to_tamil("Neetu"), "நீத்து")
        self.assertEqual(dynamic_english_to_tamil("Hinduja"), "ஹிந்துஜா")


if __name__ == "__main__":
    unittest.main()



