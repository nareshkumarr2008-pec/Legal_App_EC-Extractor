# -*- coding: utf-8 -*-
"""Unit tests for Property Title & Encumbrance Verification Filter."""

import unittest
from fastapi.testclient import TestClient
from app.server import app
from app.property_filter import PropertyFilterEngine
from app.samples import SAMPLE_DOCUMENTS


class TestPropertyFilterEngine(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
        # Realistic sample EC extraction with 4 transactions:
        # 1. Sale deed to K. Rajendran
        # 2. MODT / Mortgage to State Bank of India
        # 3. Mortgage Discharge / Receipt by SBI
        # 4. Subsequent Sale to S. Lakshmi Priya
        self.sample_ec_extraction = {
            "document_type_id": "ec",
            "document_type_name": "Encumbrance Certificate (Form 15)",
            "fields": {
                "survey_searched": {"value": "142/2A"},
                "village": {"value": "Velachery"},
                "taluk": {"value": "Velachery"},
                "district": {"value": "Chennai"},
                "transactions_table": {
                    "value": [
                        {
                            "sr": 1,
                            "doc_no": "1820/2008",
                            "doc_no_year": "1820/2008",
                            "date": "24-Mar-2008",
                            "registration_date": "24-Mar-2008",
                            "nature": "Conveyance Metro/UA",
                            "executants": "1. Classic Foundations Pvt Ltd",
                            "claimants": "1. K. Rajendran",
                            "consideration": "Rs. 32,00,000/-",
                            "market_value": "Rs. 32,00,000/-",
                            "pr_number": "450/1995",
                            "remarks": "Schedule A Details: Property Type: Flat / Apartment, Property Extent: 1250 Sq.Ft (UDS: 480 Sq.Ft), Village & Street: Velachery, Main Road Survey No.: 142/2A, Flat No.: 3B, Boundary Details: North: 30 ft road, South: Plot 29, East: Plot 27, West: 40 ft road",
                            "schedules": [
                                {
                                    "survey_no": "142/2A",
                                    "extent": "1250 Sq.Ft (UDS: 480 Sq.Ft)",
                                    "plot_no": "Flat 3B",
                                    "boundaries": "North: 30 ft road, South: Plot 29"
                                }
                            ]
                        },
                        {
                            "sr": 2,
                            "doc_no": "2910/2012",
                            "doc_no_year": "2910/2012",
                            "date": "15-Jun-2012",
                            "registration_date": "15-Jun-2012",
                            "nature": "MODT / Deposit of Title Deeds",
                            "executants": "1. K. Rajendran",
                            "claimants": "1. State Bank of India",
                            "consideration": "Rs. 25,00,000/-",
                            "market_value": "Rs. 25,00,000/-",
                            "pr_number": "1820/2008",
                            "remarks": "Schedule A Details: Property Type: Flat / Apartment, Property Extent: 1250 Sq.Ft, Survey No.: 142/2A, Flat No.: 3B",
                            "schedules": [
                                {
                                    "survey_no": "142/2A",
                                    "extent": "1250 Sq.Ft",
                                    "plot_no": "Flat 3B"
                                }
                            ]
                        },
                        {
                            "sr": 3,
                            "doc_no": "640/2018",
                            "doc_no_year": "640/2018",
                            "date": "10-Feb-2018",
                            "registration_date": "10-Feb-2018",
                            "nature": "Receipt / Mortgage Discharge",
                            "executants": "1. State Bank of India",
                            "claimants": "1. K. Rajendran",
                            "consideration": "Rs. 25,00,000/-",
                            "market_value": "-",
                            "pr_number": "2910/2012",
                            "remarks": "Schedule A Details: Survey No.: 142/2A, Flat No.: 3B. Mortgage loan under 2910/2012 satisfied and released.",
                            "schedules": [
                                {
                                    "survey_no": "142/2A",
                                    "plot_no": "Flat 3B"
                                }
                            ]
                        },
                        {
                            "sr": 4,
                            "doc_no": "4521/2023",
                            "doc_no_year": "4521/2023",
                            "date": "14-Sep-2023",
                            "registration_date": "14-Sep-2023",
                            "nature": "Conveyance Metro/UA",
                            "executants": "1. K. Rajendran",
                            "claimants": "1. S. Lakshmi Priya",
                            "consideration": "Rs. 75,00,000/-",
                            "market_value": "Rs. 75,00,000/-",
                            "pr_number": "1820/2008",
                            "remarks": "Schedule A Details: Property Type: Flat / Apartment, Property Extent: 1250 Sq.Ft (UDS: 480 Sq.Ft), Survey No.: 142/2A, Flat No.: 3B",
                            "schedules": [
                                {
                                    "survey_no": "142/2A",
                                    "extent": "1250 Sq.Ft (UDS: 480 Sq.Ft)",
                                    "plot_no": "Flat 3B"
                                }
                            ]
                        }
                    ]
                }
            }
        }

    def test_filter_by_flat_and_survey(self):
        criteria = {
            "survey_no": "142/2A",
            "flat_name": "3B",
            "taluk": "Velachery",
            "city_village": "Velachery",
            "district": "Chennai",
            "owner_name": "K. Rajendran"
        }
        res = PropertyFilterEngine.filter_and_verify(criteria, self.sample_ec_extraction)
        
        self.assertEqual(res["status"], "success")
        summary = res["summary"]
        self.assertEqual(summary["total_entries"], 4)
        self.assertEqual(summary["matched_entries_count"], 4)
        self.assertEqual(summary["match_percentage"], 100.0)

    def test_current_title_holder(self):
        criteria = {"survey_no": "142/2A"}
        res = PropertyFilterEngine.filter_and_verify(criteria, self.sample_ec_extraction)
        
        holder = res["current_holder"]
        self.assertIsNotNone(holder)
        self.assertIn("Lakshmi Priya", holder["buyer_holder"])
        self.assertEqual(holder["doc_no"], "4521/2023")
        self.assertEqual(holder["date"], "14-Sep-2023")

    def test_user_related_transaction(self):
        criteria = {"owner_name": "K. Rajendran"}
        res = PropertyFilterEngine.filter_and_verify(criteria, self.sample_ec_extraction)
        
        user_tx = res["user_related_transaction"]
        self.assertIsNotNone(user_tx)
        self.assertIn("Rajendran", user_tx["claimants"])
        self.assertEqual(user_tx["doc_no"], "1820/2008")
        self.assertIn("Claimant", user_tx["role"])

    def test_loan_mortgage_and_closure_status(self):
        criteria = {"survey_no": "142/2A", "flat_name": "3B"}
        res = PropertyFilterEngine.filter_and_verify(criteria, self.sample_ec_extraction)
        
        summary = res["summary"]
        self.assertEqual(summary["total_loans_found"], 1)
        self.assertEqual(summary["closed_loans_count"], 1)
        self.assertEqual(summary["open_loans_count"], 0)
        self.assertFalse(summary["has_active_loans"])

        loan = res["loan_records"][0]
        self.assertEqual(loan["status"], "CLOSED")
        self.assertEqual(loan["mortgage_doc_no"], "2910/2012")
        self.assertEqual(loan["discharge_doc_no"], "640/2018")
        self.assertEqual(loan["discharge_date"], "10-Feb-2018")
        self.assertIn("State Bank of India", loan["lender"])

    def test_open_loan_detection(self):
        # Create an extraction where loan has no discharge deed
        unclosed_extraction = dict(self.sample_ec_extraction)
        unclosed_extraction["fields"] = dict(self.sample_ec_extraction["fields"])
        txs = list(self.sample_ec_extraction["fields"]["transactions_table"]["value"])
        # Remove the discharge deed (idx 2)
        txs_without_discharge = [txs[0], txs[1], txs[3]]
        unclosed_extraction["fields"]["transactions_table"] = {"value": txs_without_discharge}

        res = PropertyFilterEngine.filter_and_verify({"survey_no": "142/2A"}, unclosed_extraction)
        summary = res["summary"]
        self.assertEqual(summary["open_loans_count"], 1)
        self.assertEqual(summary["closed_loans_count"], 0)
        self.assertTrue(summary["has_active_loans"])
        self.assertEqual(res["loan_records"][0]["status"], "OPEN")

    def test_court_case_detection(self):
        # Add a court attachment entry
        ec_with_court = dict(self.sample_ec_extraction)
        ec_with_court["fields"] = dict(self.sample_ec_extraction["fields"])
        txs = list(self.sample_ec_extraction["fields"]["transactions_table"]["value"])
        court_tx = {
            "sr": 5,
            "doc_no": "Court Order 12/2021",
            "date": "05-May-2021",
            "nature": "Court Attachment Order",
            "executants": "City Civil Court, Chennai",
            "claimants": "M/s ABC Finance Ltd",
            "remarks": "In O.S. No. 450/2020 on the file of IV Asst City Civil Court Chennai, interim attachment of schedule property ordered."
        }
        ec_with_court["fields"]["transactions_table"] = {"value": txs + [court_tx]}

        res = PropertyFilterEngine.filter_and_verify({"survey_no": "142/2A"}, ec_with_court)
        self.assertTrue(res["summary"]["has_court_orders"])
        self.assertEqual(res["summary"]["court_cases_count"], 1)
        self.assertEqual(res["court_cases"][0]["doc_no"], "Court Order 12/2021")

    def test_api_endpoint(self):
        payload = {
            "criteria": {
                "survey_no": "142/2A",
                "flat_name": "3B",
                "owner_name": "K. Rajendran"
            },
            "extraction": self.sample_ec_extraction
        }
        response = self.client.post("/api/property/filter", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["summary"]["matched_entries_count"], 4)
        self.assertEqual(data["loan_records"][0]["status"], "CLOSED")


if __name__ == "__main__":
    unittest.main()
