# -*- coding: utf-8 -*-
DOCUMENT_CATEGORIES = [
    {
        "id": "sale_deed",
        "name": "Sale deed / title deed",
        "tamil_name": "கிரையப் பத்திரம் / தாய் பத்திரம்",
        "icon": "file-text",
        "color": "emerald",
        "description": "Vendor & Purchaser details, History/Previous owner, Schedule of property (Land, Land+Building, Apartment UDS), Boundary, and SRO details.",
        "key_fields": [
            "Vendor Details", "Purchaser Details", "History / Previous Owner Details", "Schedule of Property", "Survey Number / S No", "Land Extent", "Building Built-Up Area", "Apartment UDS & Floor", "Boundary", "SRO Details"
        ]
    },
    {
        "id": "patta",
        "name": "Patta document",
        "tamil_name": "பட்டா ஆவணம் (Patta Document)",
        "icon": "award",
        "color": "blue",
        "description": "Tamil Nadu Revenue Record: Patta Number, Owner Name(s), Survey Number & Sub-division, Village, Taluk, District, Extent of Land, Nature of Land.",
        "key_fields": [
            "Patta Number", "Owner Name(s)", "Survey Number(s) and Sub-division", "Village", "Taluk", "District", "Extent of Land under each Survey Number", "Nature of Land"
        ]
    },
    {
        "id": "parent_docs",
        "name": "Parent docs / mother copy",
        "tamil_name": "முந்தைய மூல ஆவணங்கள் (Mother Copy)",
        "icon": "layers",
        "color": "slate",
        "description": "Historical chain of title documents with mandatory 5-year continuity validation, prior vendor/purchaser, and survey extent trace.",
        "key_fields": [
            "Previous Owner / Vendor", "Purchaser / Claimant", "Parent Document No & Year", "Survey Number / S No", "Extent Transferred", "Last 5 Years Validation"
        ]
    },
    {
        "id": "ec",
        "name": "EC",
        "tamil_name": "வில்லங்கச் சான்றிதழ் (Encumbrance Certificate)",
        "icon": "shield-check",
        "color": "purple",
        "description": "30-year search period, Form 15 vs Form 16 Nil status, survey number, SRO details, and registered entries table.",
        "key_fields": [
            "Search Period (30-Year Min)", "Form Type (Form 15 vs 16)", "Survey Number & Village", "SRO Details", "Registered Entries Table", "Encumbrance Status"
        ]
    },
    {
        "id": "building_plan",
        "name": "Approved building plan",
        "tamil_name": "அங்கீகரிக்கப்பட்ட கட்டிட வரைபடம்",
        "icon": "home",
        "color": "amber",
        "description": "Sanctioned building permit order & drawing approved by Local Planning Authority, CMDA, or DTCP.",
        "key_fields": [
            "Permit Number & Date", "Sanctioning Authority", "Survey No / Plot No & Village", "Approved Built-Up Area", "Height & Number of Floors", "FSI & Setbacks Compliance"
        ]
    },
    {
        "id": "rera",
        "name": "Rera certificate approval certificate (if applicable)",
        "tamil_name": "RERA பதிவு சான்றிதழ்",
        "icon": "check-circle",
        "color": "teal",
        "description": "Real Estate Regulatory Authority registration certificate for layout or apartment development projects.",
        "key_fields": [
            "TNRERA Registration Number", "Project Name & Type", "Promoter / Developer Name", "Project Survey Numbers & Location", "Validity & Completion Expiry"
        ]
    },
    {
        "id": "tax_eb",
        "name": "Property water tax and eb receipts",
        "tamil_name": "சொத்து வரி, குடிநீர் வரி & EB ரசீது",
        "icon": "receipt",
        "color": "sky",
        "description": "Municipal property tax assessment, water tax connection receipts, and TANGEDCO Electricity Board consumer billing.",
        "key_fields": [
            "Property Tax Assessment No", "Property Owner Name", "Door Number & Locality", "Water Tax Connection & Status", "EB Consumer No & Tariff", "Payment Receipt Date & Amount"
        ]
    },
    {
        "id": "layout_approval",
        "name": "Approved layout (if applicable) CMDA / DTCP",
        "tamil_name": "அங்கீகரிக்கப்பட்ட மனைப்பிரிவு (CMDA / DTCP)",
        "icon": "map",
        "color": "rose",
        "description": "Subdivision layout approval sanctioned by CMDA or DTCP with plots breakdown and OSR park reservation.",
        "key_fields": [
            "Layout Approval Number (PPD/Lo)", "Sanctioning Authority (CMDA / DTCP)", "Survey Numbers & Village", "Total Extent & Number of Plots", "OSR Park & Road Gift Details"
        ]
    },
    {
        "id": "death_legal_heir",
        "name": "Death certificate and legal hier certificate",
        "tamil_name": "இறப்பு & வாரிசுச் சான்றிதழ் (Varisu)",
        "icon": "users",
        "color": "orange",
        "description": "Death certificate and Tahsildar Legal Heir Certificate (Varisu) with complete heir signatory check and Patta Mutation Hard Gate.",
        "key_fields": [
            "Deceased Name", "Date of Death & Reg No", "Varisu Certificate Order No & Date", "Surviving Legal Heirs List", "Heir Completeness Check (100%)", "Patta Mutation Status (TN Act 1983)"
        ]
    },
    {
        "id": "loan_docs",
        "name": "Loan documents (if applicable)",
        "tamil_name": "வங்கி கடன் ஆவணங்கள் / MODT",
        "icon": "landmark",
        "color": "violet",
        "description": "Housing loan sanction, registered Memorandum of Deposit of Title Deeds (MODT), and Bank NOC / Discharge receipt.",
        "key_fields": [
            "Lending Bank / Institution", "Borrower & Co-Borrower Names", "Loan Account & Sanctioned Amount", "Security / MODT Details", "MODT Doc No, Year & SRO", "NOC / Discharge Status"
        ]
    },
    {
        "id": "tslr",
        "name": "TSLR document (Town Survey Land Record)",
        "tamil_name": "நகர நில அளவை ஆவணம் (TSLR)",
        "icon": "map-pinned",
        "color": "cyan",
        "description": "Tamil Nadu Urban Land Records: Town Survey Land Register extract with Town Survey No, Old Survey No, Ward & Block, Extent, Land classification, Current land use, Tenure type, Assessment, and Mutation remarks.",
        "key_fields": [
            "District", "Taluk", "Town", "Ward", "Name", "Survey Number / S.No", "Extent", "Ward + Block", "Land classification", "Current land use", "Tenure type", "Assessment (Rs.)", "Remarks"
        ]
    }
]

SAMPLE_DOCUMENTS = {
    "sale_deed": {
        "title": "Sale deed / title deed",
        "raw_text": """GOVERNMENT OF TAMIL NADU - REGISTRATION DEPARTMENT
DOCUMENT NO: 4521 / 2023 | BOOK 1 | SRO VELACHERY
DATE OF REGISTRATION: 14th September 2023 (14.09.2023)

1. VENDOR DETAILS:
Name: Mr. K. RAJENDRAN, Son of Late Kumarasamy
Represented by Power of Attorney Agent: M/s. Premier Realty Advisors (POA Doc No. 842 of 2021, SRO Velachery)

2. PURCHASER DETAILS:
Name: Mrs. S. LAKSHMI PRIYA, Wife of Mr. M. Senthil Kumar

3. HISTORY / PREVIOUS OWNER DETAILS:
Previous Owner: Classic Foundations Pvt Ltd (Represented by POA: Mr. V. Ramanathan)
Previous Document No: Doc No. 1820 / 2008 registered at SRO Velachery on 24.03.2008

4. SCHEDULE OF PROPERTY:
Schedule Type: Apartment or flat with Undivided Share (UDS)
Survey Number / S No: T.S. No. 142/2A (Old Sy No. 458/1B)
Village: Velachery Village | Taluk: Velachery | District: Chennai South
Land Extent: Total Land 4800 Sq.Ft (2 Grounds)
Apartment Details: Flat No. 3B, Third Floor, Built-up Area: 1250 Sq.Ft | UDS: 480 Sq.Ft

5. BOUNDARY OF PROPERTY:
North by: 30 Feet Scheme Road
South by: Plot No. 29 & Property of Mr. Raghavan
East by: Plot No. 27 & Compound Wall
West by: 40 Feet Main Road

6. SRO REGISTRATION DETAILS:
Sub-Registrar Office: SRO Velachery
Document Number: 4521 / 2023 | Book 1
Stamp Duty Paid: Rs. 5,25,000/- | Registration Fee: Rs. 1,50,000/-""",
        "structured": {
            "document_type": "Sale deed / title deed",
            "document_number": {
                "value": "Doc No. 4521 of 2023 (Book 1)",
                "confidence": 0.98,
                "label": "Document Number",
                "box": {"x_pct": 5.0, "y_pct": 8.0, "w_pct": 88.0, "h_pct": 3.5}
            },
            "registration_date": {
                "value": "14.09.2023",
                "confidence": 0.96,
                "label": "Registration Date",
                "box": {"x_pct": 5.0, "y_pct": 10.0, "w_pct": 40.0, "h_pct": 3.0}
            },
            "vendor_details": {
                "value": "Mr. K. RAJENDRAN (Represented by POA: M/s. Premier Realty Advisors)",
                "confidence": 0.95,
                "label": "Vendor Details",
                "box": {"x_pct": 5.0, "y_pct": 15.0, "w_pct": 88.0, "h_pct": 4.5}
            },
            "purchaser_details": {
                "value": "Mrs. S. LAKSHMI PRIYA",
                "confidence": 0.95,
                "label": "Purchaser Details",
                "box": {"x_pct": 5.0, "y_pct": 20.0, "w_pct": 88.0, "h_pct": 4.5}
            },
            "poa_agent_details": {
                "value": "M/s. Premier Realty Advisors (POA Doc No. Doc No. 842 of 2021, SRO Velachery)",
                "confidence": 0.95,
                "label": "பவர் ஏஜென்ட் விவரம் (Power of Attorney Agent)",
                "poa_name": "M/s. Premier Realty Advisors",
                "poa_document_number": "Doc No. 842 of 2021, SRO Velachery",
                "box": {"x_pct": 5.0, "y_pct": 24.0, "w_pct": 88.0, "h_pct": 3.5}
            },
            "history_previous_owner": {
                "value": "Classic Foundations Pvt Ltd (Represented by POA: Mr. V. Ramanathan)",
                "confidence": 0.92,
                "label": "History / Previous Owner Details",
                "box": {"x_pct": 5.0, "y_pct": 28.5, "w_pct": 88.0, "h_pct": 4.0}
            },
            "previous_doc_reference": {
                "value": "Doc No. 1820 / 2008, registered at SRO Velachery on 24.03.2008",
                "confidence": 0.94,
                "label": "Previous Document Reference",
                "box": {"x_pct": 5.0, "y_pct": 33.0, "w_pct": 88.0, "h_pct": 3.5}
            },
            "schedule_property_type": {
                "value": "Apartment or flat with Undivided Share of Land (UDS)",
                "confidence": 0.95,
                "label": "Schedule of Property",
                "box": {"x_pct": 5.0, "y_pct": 37.0, "w_pct": 88.0, "h_pct": 3.8}
            },
            "survey_number": {
                "value": "T.S. No. 142/2A (Old S.No 458/1B), Velachery Village, Velachery Taluk, Chennai South",
                "confidence": 0.94,
                "label": "Survey Number / S No",
                "box": {"x_pct": 5.0, "y_pct": 41.0, "w_pct": 88.0, "h_pct": 3.8}
            },
            "village_taluk_district": {
                "value": "Velachery Village / Velachery Taluk / Chennai South District",
                "confidence": 0.94,
                "label": "Village / Taluk / District",
                "box": {"x_pct": 5.0, "y_pct": 45.0, "w_pct": 88.0, "h_pct": 3.5}
            },
            "flat_details": {
                "value": "Flat No. 3B, Third Floor, Sunshine Apartments",
                "confidence": 0.94,
                "label": "Flat Details",
                "box": {"x_pct": 5.0, "y_pct": 49.0, "w_pct": 88.0, "h_pct": 3.5}
            },
            "land_extent": {
                "value": "Total Land Extent: 4800 Sq.Ft (2 Grounds)",
                "confidence": 0.92,
                "label": "Land Extent",
                "box": {"x_pct": 5.0, "y_pct": 53.0, "w_pct": 88.0, "h_pct": 3.5}
            },
            "apartment_uds_floor": {
                "value": "UDS: 480 Sq.Ft | Built-Up Area: 1250 Sq.Ft | Flat No. 3B, 3rd Floor",
                "confidence": 0.95,
                "label": "Apartment UDS & Floor",
                "box": {"x_pct": 5.0, "y_pct": 57.0, "w_pct": 88.0, "h_pct": 4.0}
            },
            "boundaries": {
                "value": "North: 30 Feet Scheme Road | South: Plot No. 29 & Property of Mr. Raghavan | East: Plot No. 27 & Compound Wall | West: 40 Feet Main Road",
                "north": "30 Feet Scheme Road",
                "south": "Plot No. 29 & Property of Mr. Raghavan",
                "east": "Plot No. 27 & Compound Wall",
                "west": "40 Feet Main Road",
                "confidence": 0.93,
                "label": "Four Boundaries",
                "box": {"x_pct": 5.0, "y_pct": 62.0, "w_pct": 88.0, "h_pct": 4.0}
            },
            "sro_details": {
                "value": "SRO Velachery",
                "confidence": 0.95,
                "label": "SRO Details",
                "box": {"x_pct": 5.0, "y_pct": 67.0, "w_pct": 88.0, "h_pct": 3.8}
            },
            "stamp_duty_fee": {
                "value": "Stamp Duty: Rs. 5,25,000/- | Registration Fee: Rs. 1,50,000/-",
                "confidence": 0.95,
                "label": "Stamp Duty & Fees",
                "box": {"x_pct": 5.0, "y_pct": 71.0, "w_pct": 88.0, "h_pct": 3.5}
            }
        }
    },
    "patta": {
        "title": "Patta document",
        "raw_text": """தமிழ்நாடு அரசு
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
https://eservices.tn.gov.in""",
        "structured": {
            "document_type": "Patta document",
            "patta_number": {
                "value": "242",
                "confidence": 0.98,
                "label": "Patta Number"
            },
            "owner_name": {
                "value": "Ranganathan, S/o Chinnakannu (சின்னக்கண்ணு மகன் ரங்கநாதன்)",
                "confidence": 0.98,
                "label": "Owner Name(s)"
            },
            "village": {
                "value": "Sembakkam (செம்பாக்கம்)",
                "confidence": 0.98,
                "label": "Village"
            },
            "district": {
                "value": "Chengalpattu (செங்கல்பட்டு)",
                "confidence": 0.98,
                "label": "District"
            },
            "taluk": {
                "value": "Tambaram (தாம்பரம்)",
                "confidence": 0.98,
                "label": "Taluk"
            },
            "survey_numbers": {
                "value": "128/7",
                "confidence": 0.98,
                "label": "Survey Number(s)"
            },
            "extent_details": {
                "value": "128/7: 0.00.06 Hectares (நன்செய் / Wet) — Tax: Rs. 2.00\nTotal: 0.00.06 Hectares (0 Sq.M / 0 Sq.Ft / 0.00 Grounds / 0.000 Acres) — Total Tax: Rs. 2.00",
                "confidence": 0.98,
                "label": "Extent of Land under each Survey Number"
            },
            "nature_of_land": {
                "value": "Rayathuvari Manai (Residential Plot) — ரயத்துவாரி மனை",
                "confidence": 0.98,
                "label": "Nature of Land"
            },
            "digital_signature_timestamp": {
                "value": "22/01/2024 at 05:47:27 PM",
                "confidence": 0.99,
                "label": "Digital Signature Timestamp (மின்கையொப்பம்)"
            },
            "authorized_signatory": {
                "value": "Kavitha S (Tahsildar)",
                "confidence": 0.99,
                "label": "Authorized Signatory (மண்டல துணை வட்டாட்சியர்)"
            },
            "portal_reference": {
                "value": "S/NA/35/05/128/00242/20878",
                "confidence": 0.99,
                "label": "e-Services Reference / Application Number"
            },
            "certificate_printed_date": {
                "value": "15-09-2026 at 08:42:26 AM",
                "confidence": 0.99,
                "label": "Certificate Print Timestamp (அச்சிடப்பட்ட நேரம்)"
            },
            "verification_portal": {
                "value": "https://eservices.tn.gov.in",
                "confidence": 0.99,
                "label": "Government Verification Portal"
            },
            "total_tax": {
                "value": "Rs. 2.00",
                "confidence": 0.98,
                "label": "Total Land Revenue Tax / Assessment (தீர்வை)"
            },
            "cadastral_schedule": [
                {
                    "sl": "1",
                    "survey_no": "128/7",
                    "land_type": "ரயத்துவாரி மனை (Residential Site / Manai)",
                    "extent_ha": "0.00.06 Hectares",
                    "sq_meters": "6 Sq.M",
                    "sq_feet": "65 Sq.Ft",
                    "tax": "Rs. 2.00"
                }
            ],
            "checklist": [
                {
                    "item": "Patta Number Validation",
                    "title": "Patta Number Validation (பட்டா எண்: 242)",
                    "status": "PASSED",
                    "detail": "Valid Patta number 242 extracted and verified in Form 10(1) revenue heading."
                },
                {
                    "item": "Owner & Kinship Authentication",
                    "title": "Owner & Kinship Authentication (பட்டாதாரர் & உறவுமுறை)",
                    "status": "PASSED",
                    "detail": "Registered Pattadhar authenticated: Ranganathan, S/o Chinnakannu (சின்னக்கண்ணு மகன் ரங்கநாதன்)"
                },
                {
                    "item": "Survey Numbers Schedule",
                    "title": "Survey Numbers Schedule (புல எண்கள்: 128/7)",
                    "status": "PASSED",
                    "detail": "All 1 cadastral survey number(s) identified (128/7) in revenue table."
                },
                {
                    "item": "Extent & Revenue Balance",
                    "title": "Extent & Revenue Balance (பரப்பளவு & தீர்வை சரிபார்ப்பு)",
                    "status": "PASSED",
                    "detail": "Land area (0.40.00 Hectares = 4,000 Sq.M) and cumulative totals verified mathematically across revenue table."
                },
                {
                    "item": "Digital Signature & Authenticity",
                    "title": "Digital Signature & Authenticity (மின்கையொப்பம்)",
                    "status": "PASSED",
                    "detail": "Authorized Government Digital Signature confirmed: Kavitha S (Tahsildar) [22/01/2024 at 05:47:27 PM]."
                },
                {
                    "item": "TN e-Services Portal Verification",
                    "title": "TN e-Services Portal Verification (Ref: S/NA/35/05/128/00242/20878)",
                    "status": "PASSED",
                    "detail": "Online verification reference S/NA/35/05/128/00242/20878 active on official portal https://eservices.tn.gov.in."
                }
            ]
        }
    },
    "parent_docs": {
        "title": "Parent docs / mother copy",
        "raw_text": """PARENT DEED / MOTHER DOCUMENT VERIFICATION
TITLE CHAIN TRACE - SRO VELACHERY

1. PARENT DOCUMENT DETAILS:
Parent Document No: Doc No. 1820 / 2008 registered at SRO Velachery on 24.03.2008
Nature of Document: Absolute Sale Deed

2. PARTIES TO PARENT DEED:
Previous Owner / Vendor: M/s. Classic Foundations Pvt Ltd, rep by its Managing Director
Purchaser / Claimant: Mr. K. RAJENDRAN, Son of Late Kumarasamy

3. PROPERTY IDENTIFICATION:
Survey Number / S No: T.S. No. 142/2A, Velachery Village, Chennai
Extent Transferred: 4800 Sq.Ft (2 Grounds)

4. LAST 5 YEARS TITLE VALIDATION:
Search & Trace Period: 2018 to 2023 (5+ Years Validated)
Continuity Status: 100% Continuous & Unbroken Title Chain
Prior Encumbrance Check: Mortgage discharged via NOC Doc 640/2018 in year 2018.""",
        "structured": {
            "document_type": "Parent docs / mother copy",
            "previous_owner_vendor": {
                "value": "M/s. Classic Foundations Pvt Ltd (Managing Director)",
                "confidence": 0.92,
                "label": "Previous Owner / Vendor",
                "box": {"x_pct": 5.0, "y_pct": 14.0, "w_pct": 80.0, "h_pct": 3.8}
            },
            "purchaser_claimant": {
                "value": "Mr. K. RAJENDRAN (Son of Late Kumarasamy)",
                "confidence": 0.94,
                "label": "Purchaser / Claimant",
                "box": {"x_pct": 5.0, "y_pct": 20.0, "w_pct": 80.0, "h_pct": 3.8}
            },
            "parent_doc_no_year": {
                "value": "Doc No. 1820 / 2008 (Registered on 24.03.2008, SRO Velachery)",
                "confidence": 0.95,
                "label": "Parent Document No & Year",
                "box": {"x_pct": 5.0, "y_pct": 26.0, "w_pct": 85.0, "h_pct": 3.8}
            },
            "survey_number": {
                "value": "T.S. No. 142/2A, Velachery Village, Chennai",
                "confidence": 0.92,
                "label": "Survey Number / S No",
                "box": {"x_pct": 5.0, "y_pct": 32.0, "w_pct": 75.0, "h_pct": 3.8}
            },
            "extent_transferred": {
                "value": "4800 Sq.Ft (2 Grounds)",
                "confidence": 0.91,
                "label": "Extent Transferred",
                "box": {"x_pct": 5.0, "y_pct": 38.0, "w_pct": 55.0, "h_pct": 3.8}
            },
            "last_5_years_validation": {
                "value": "PASS: Unbroken Title Chain 2018-2023 (No Adverse Claims / Discharged)",
                "confidence": 0.96,
                "label": "Last 5 Years Validation",
                "box": {"x_pct": 5.0, "y_pct": 44.0, "w_pct": 90.0, "h_pct": 4.0}
            }
        }
    },
    "ec": {
        "title": "EC",
        "raw_text": """GOVERNMENT OF TAMILNADU
REGISTRATION DEPARTMENT
தமிழ்நாடு அரசு
பதிவுத்துறை
Certificate of Encumbrance on Property
சொத்து தொடர்பான வில்லங்கச் சான்று
S.R.O /சா.ப.அ: Velachery Date / நாள்: 29-Aug-2026
Village /கிராமம்: Velachery Survey Details /சர்வே விவரம்: 142/2A
Data Availability Period for Village: Velachery
Velachery Sub Registrar Office: From 01-Jan-1990 To 17-Oct-2023
Search Period /தேடுதல் காலம்: 01-Jan-1990 - 17-Oct-2023

1820/2008
24-Mar-2008
24-Mar-2008
24-Mar-2008
Conveyance Metro/UA
1. Classic Foundations Pvt Ltd
1. K. Rajendran
Consideration Value/கைமாற்றுத் தொகை: Rs. 32,00,000/-
Market Value/சந்தை மதிப்பு: Rs. 32,00,000/-
PR Number/முந்தைய ஆவண எண்: 450/1995
Schedule A Details:
Property Type/சொத்தின் வகைப்பாடு: Flat / Apartment
Property Extent/சொத்தின் விஸ்தீர்ணம்: 1250 Sq.Ft (UDS: 480 Sq.Ft)
Village & Street/கிராமம் மற்றும் தெரு: Velachery, Main Road Survey No./புல எண் : 142/2A
Flat No./அடுக்குமாடிக் குடியிருப்பு எண்: 3B
Boundary Details: வடக்கில் 30 அடி சாலை, தெற்கில் மனை எண் 29, கிழக்கில் மனை எண் 27, மேற்கில் 40 அடி மெயின் ரோடு

2910/2012
15-Jun-2012
15-Jun-2012
15-Jun-2012
MODT / Deposit of Title Deeds
1. K. Rajendran
1. State Bank of India
Consideration Value/கைமாற்றுத் தொகை: Rs. 25,00,000/-
Market Value/சந்தை மதிப்பு: Rs. 25,00,000/-
PR Number/முந்தைய ஆவண எண்: 1820/2008
Schedule A Details:
Property Type/சொத்தின் வகைப்பாடு: Flat / Apartment
Property Extent/சொத்தின் விஸ்தீர்ணம்: 1250 Sq.Ft (UDS: 480 Sq.Ft)
Village & Street/கிராமம் மற்றும் தெரு: Velachery, Main Road Survey No./புல எண் : 142/2A
Flat No./அடுக்குமாடிக் குடியிருப்பு எண்: 3B
Boundary Details: வடக்கில் 30 அடி சாலை, தெற்கில் மனை எண் 29, கிழக்கில் மனை எண் 27, மேற்கில் 40 அடி மெயின் ரோடு

640/2018
10-Feb-2018
10-Feb-2018
10-Feb-2018
Receipt / Mortgage Discharge
1. State Bank of India
1. K. Rajendran
Consideration Value/கைமாற்றுத் தொகை: Rs. 25,00,000/-
Market Value/சந்தை மதிப்பு: -
PR Number/முந்தைய ஆவண எண்: 2910/2012
Schedule A Details:
Property Type/சொத்தின் வகைப்பாடு: Flat / Apartment
Property Extent/சொத்தின் விஸ்தீர்ணம்: 1250 Sq.Ft (UDS: 480 Sq.Ft)
Village & Street/கிராமம் மற்றும் தெரு: Velachery, Main Road Survey No./புல எண் : 142/2A
Flat No./அடுக்குமாடிக் குடியிருப்பு எண்: 3B
Boundary Details: வடக்கில் 30 அடி சாலை, தெற்கில் மனை எண் 29, கிழக்கில் மனை எண் 27, மேற்கில் 40 அடி மெயின் ரோடு

4521/2023
14-Sep-2023
14-Sep-2023
14-Sep-2023
Conveyance Metro/UA
1. K. Rajendran
1. S. Lakshmi Priya
Consideration Value/கைமாற்றுத் தொகை: Rs. 75,00,000/-
Market Value/சந்தை மதிப்பு: Rs. 75,00,000/-
PR Number/முந்தைய ஆவண எண்: 1820/2008
Schedule A Details:
Property Type/சொத்தின் வகைப்பாடு: Flat / Apartment
Property Extent/சொத்தின் விஸ்தீர்ணம்: 1250 Sq.Ft (UDS: 480 Sq.Ft)
Village & Street/கிராமம் மற்றும் தெரு: Velachery, Main Road Survey No./புல எண் : 142/2A
Flat No./அடுக்குமாடிக் குடியிருப்பு எண்: 3B
Boundary Details: வடக்கில் 30 அடி சாலை, தெற்கில் மனை எண் 29, கிழக்கில் மனை எண் 27, மேற்கில் 40 அடி மெயின் ரோடு""",
        "structured": {
            "document_type": "EC",
            "search_period": {
                "value": "01-01-1990 to 17-10-2023 (33 Years - Min 30 Years Compliant)",
                "confidence": 0.96,
                "label": "Search Period (30-Year Min)",
                "box": {"x_pct": 5.0, "y_pct": 14.0, "w_pct": 85.0, "h_pct": 3.8}
            },
            "form_type": {
                "value": "Form 15 (Registered Transactions Recorded)",
                "confidence": 0.95,
                "label": "Form Type (Form 15 vs 16)",
                "box": {"x_pct": 5.0, "y_pct": 20.0, "w_pct": 75.0, "h_pct": 3.8}
            },
            "survey_number_village": {
                "value": "T.S. No. 142/2A, Velachery Village, Chennai South",
                "confidence": 0.92,
                "label": "Survey Number & Village",
                "box": {"x_pct": 5.0, "y_pct": 26.0, "w_pct": 80.0, "h_pct": 3.8}
            },
            "sro_details": {
                "value": "SRO Velachery, Chennai South Registration District",
                "confidence": 0.93,
                "label": "SRO Details",
                "box": {"x_pct": 5.0, "y_pct": 32.0, "w_pct": 75.0, "h_pct": 3.8}
            },
            "registered_entries_table": {
                "value": "4 Entries: Sale Deed (2008), MODT (2012), Discharge Receipt (2018), Sale Deed (2023)",
                "confidence": 0.92,
                "label": "Registered Entries Table",
                "box": {"x_pct": 5.0, "y_pct": 38.0, "w_pct": 90.0, "h_pct": 4.5}
            },
            "encumbrance_status": {
                "value": "CLEAR: Prior Mortgage Discharged via Doc 640/2018 (Nil Active Encumbrance)",
                "confidence": 0.95,
                "label": "Encumbrance Status",
                "box": {"x_pct": 5.0, "y_pct": 44.5, "w_pct": 90.0, "h_pct": 4.0}
            }
        }
    },
    "building_plan": {
        "title": "Approved building plan",
        "raw_text": """PLANNING PERMIT & BUILDING SANCTION ORDER
GREATER CHENNAI CORPORATION / CMDA
Permit No: PP/WD14/0481/2021 | Date: 18-08-2021
Sanctioning Authority: Greater Chennai Corporation (GCC) & CMDA
Property Location: Plot No. 28, T.S. No. 142/2A, Velachery, Chennai
Building Type: Stilt + 3 Floors Residential Apartment Building
Approved Built-Up Area: 4,850 Sq.Ft | Plinth Area: 1,600 Sq.Ft
Floor Space Index (FSI): 1.50 (Permissible: 1.75 - Compliant)
Setbacks: Front: 3.5m, Rear: 3.0m, Side 1: 2.0m, Side 2: 2.0m (Compliant).""",
        "structured": {
            "document_type": "Approved building plan",
            "permit_number_date": {
                "value": "PP/WD14/0481/2021 dated 18-08-2021",
                "confidence": 0.94,
                "label": "Permit Number & Date",
                "box": {"x_pct": 5.0, "y_pct": 14.0, "w_pct": 75.0, "h_pct": 3.8}
            },
            "sanctioning_authority": {
                "value": "Greater Chennai Corporation (GCC) & CMDA",
                "confidence": 0.92,
                "label": "Sanctioning Authority",
                "box": {"x_pct": 5.0, "y_pct": 20.0, "w_pct": 75.0, "h_pct": 3.8}
            },
            "survey_plot_village": {
                "value": "Plot No. 28, T.S. No. 142/2A, Velachery, Chennai",
                "confidence": 0.91,
                "label": "Survey No / Plot No & Village",
                "box": {"x_pct": 5.0, "y_pct": 26.0, "w_pct": 80.0, "h_pct": 3.8}
            },
            "approved_builtup_area": {
                "value": "4,850 Sq.Ft (Stilt + 3 Floors)",
                "confidence": 0.90,
                "label": "Approved Built-Up Area",
                "box": {"x_pct": 5.0, "y_pct": 32.0, "w_pct": 65.0, "h_pct": 3.8}
            },
            "height_floors": {
                "value": "Stilt + 3 Floors (Height: 12.0 Meters)",
                "confidence": 0.90,
                "label": "Height & Number of Floors",
                "box": {"x_pct": 5.0, "y_pct": 38.0, "w_pct": 65.0, "h_pct": 3.8}
            },
            "fsi_setbacks_compliance": {
                "value": "PASS: FSI 1.50 (Limit 1.75) | Setbacks: Front 3.5m, Rear 3.0m, Sides 2.0m",
                "confidence": 0.93,
                "label": "FSI & Setbacks Compliance",
                "box": {"x_pct": 5.0, "y_pct": 44.0, "w_pct": 90.0, "h_pct": 4.0}
            }
        }
    },
    "rera": {
        "title": "Rera certificate approval certificate (if applicable)",
        "raw_text": """TAMIL NADU REAL ESTATE REGULATORY AUTHORITY (TNRERA)
REGISTRATION CERTIFICATE OF PROJECT
Registration No: TN/29/Building/0192/2022 | Date: 12-05-2022

Project Name: Sunshine Haven Apartments
Project Type: Residential Apartment Development
Promoter Name: M/s. Chennai Prime Infra Pvt Ltd
Registered Address: No. 45, Mount Road, Guindy, Chennai - 600032
Survey Numbers: T.S. No. 142/2A, Block 14, Velachery Village, Chennai
Certificate Validity: Valid up to 31-12-2025 for Project Completion.""",
        "structured": {
            "document_type": "Rera certificate approval certificate (if applicable)",
            "tnrera_reg_number": {
                "value": "TN/29/Building/0192/2022",
                "confidence": 0.96,
                "label": "TNRERA Registration Number",
                "box": {"x_pct": 5.0, "y_pct": 14.0, "w_pct": 70.0, "h_pct": 3.8}
            },
            "project_name_type": {
                "value": "Sunshine Haven Apartments (Residential Development)",
                "confidence": 0.92,
                "label": "Project Name & Type",
                "box": {"x_pct": 5.0, "y_pct": 20.0, "w_pct": 80.0, "h_pct": 3.8}
            },
            "promoter_name": {
                "value": "M/s. Chennai Prime Infra Pvt Ltd (Guindy, Chennai)",
                "confidence": 0.91,
                "label": "Promoter / Developer Name",
                "box": {"x_pct": 5.0, "y_pct": 26.0, "w_pct": 80.0, "h_pct": 3.8}
            },
            "project_survey_location": {
                "value": "T.S. No. 142/2A, Block 14, Velachery Village, Chennai",
                "confidence": 0.92,
                "label": "Project Survey Numbers & Location",
                "box": {"x_pct": 5.0, "y_pct": 32.0, "w_pct": 85.0, "h_pct": 3.8}
            },
            "validity_expiry": {
                "value": "Valid up to 31-12-2025 (Active & Compliant)",
                "confidence": 0.94,
                "label": "Validity & Completion Expiry",
                "box": {"x_pct": 5.0, "y_pct": 38.0, "w_pct": 75.0, "h_pct": 3.8}
            }
        }
    },
    "tax_eb": {
        "title": "Property water tax and eb receipts",
        "raw_text": """PROPERTY TAX, CMWSSB WATER TAX & TANGEDCO EB BILL
Property Tax Assessment No: 14-192-04812-000
Owner Name: Mr. K. RAJENDRAN
Door No & Locality: Door No. 25, 1st Cross Street, Velachery, Chennai - 600042
CMWSSB Water Tax Consumer No: WT/VEL/091244 | Payment Status: Paid
TANGEDCO Electricity Board Consumer No: 01-192-004-9812
Tariff Category: 1A Domestic | Meter Status: Active
Receipt Date: 28-09-2023 | Total Amount Paid: Rs. 4,850/- (Nil Arrears).""",
        "structured": {
            "document_type": "Property water tax and eb receipts",
            "property_tax_assessment_no": {
                "value": "14-192-04812-000 (Greater Chennai Corporation)",
                "confidence": 0.94,
                "label": "Property Tax Assessment No",
                "box": {"x_pct": 5.0, "y_pct": 14.0, "w_pct": 80.0, "h_pct": 3.8}
            },
            "property_owner_name": {
                "value": "Mr. K. RAJENDRAN",
                "confidence": 0.92,
                "label": "Property Owner Name",
                "box": {"x_pct": 5.0, "y_pct": 20.0, "w_pct": 60.0, "h_pct": 3.8}
            },
            "door_number_locality": {
                "value": "Door No. 25, 1st Cross Street, Velachery, Chennai - 600042",
                "confidence": 0.90,
                "label": "Door Number & Locality",
                "box": {"x_pct": 5.0, "y_pct": 26.0, "w_pct": 85.0, "h_pct": 3.8}
            },
            "water_tax_status": {
                "value": "Connection No. WT/VEL/091244 | Status: Fully Paid (Nil Due)",
                "confidence": 0.91,
                "label": "Water Tax Connection & Status",
                "box": {"x_pct": 5.0, "y_pct": 32.0, "w_pct": 85.0, "h_pct": 3.8}
            },
            "eb_consumer_tariff": {
                "value": "Consumer No: 01-192-004-9812 | Tariff: 1A Domestic",
                "confidence": 0.93,
                "label": "EB Consumer No & Tariff",
                "box": {"x_pct": 5.0, "y_pct": 38.0, "w_pct": 80.0, "h_pct": 3.8}
            },
            "payment_receipt_amount": {
                "value": "Receipt Date: 28-09-2023 | Amount: Rs. 4,850/- (Nil Arrears)",
                "confidence": 0.94,
                "label": "Payment Receipt Date & Amount",
                "box": {"x_pct": 5.0, "y_pct": 44.0, "w_pct": 85.0, "h_pct": 3.8}
            }
        }
    },
    "layout_approval": {
        "title": "Approved layout (if applicable) CMDA / DTCP",
        "raw_text": """CHENNAI METROPOLITAN DEVELOPMENT AUTHORITY (CMDA)
PLANNING PERMIT - LAYOUT SUBDIVISION APPROVAL
Layout Approval No: PPD / Lo No. 48 / 2020 | Date: 15-11-2020
Sanctioning Authority: CMDA & Velachery Local Body
Survey Numbers: Survey Nos. 142/1, 142/2A, 142/2B, Velachery Village
Total Layout Extent: 5.50 Acres | Total Approved Plots: 42 Plots
Open Space Reservation (OSR): 10% OSR Park Land (24,000 Sq.Ft) Gifted via Registered Gift Deed Doc 1920/2020 to GCC.""",
        "structured": {
            "document_type": "Approved layout (if applicable) CMDA / DTCP",
            "layout_approval_no": {
                "value": "PPD / Lo No. 48 / 2020 dated 15-11-2020",
                "confidence": 0.95,
                "label": "Layout Approval Number (PPD/Lo)",
                "box": {"x_pct": 5.0, "y_pct": 14.0, "w_pct": 80.0, "h_pct": 3.8}
            },
            "sanctioning_authority": {
                "value": "CMDA (Chennai Metropolitan Development Authority)",
                "confidence": 0.92,
                "label": "Sanctioning Authority (CMDA / DTCP)",
                "box": {"x_pct": 5.0, "y_pct": 20.0, "w_pct": 80.0, "h_pct": 3.8}
            },
            "survey_numbers_village": {
                "value": "Survey Nos. 142/1, 142/2A, 142/2B, Velachery Village",
                "confidence": 0.91,
                "label": "Survey Numbers & Village",
                "box": {"x_pct": 5.0, "y_pct": 26.0, "w_pct": 85.0, "h_pct": 3.8}
            },
            "total_extent_plots": {
                "value": "Total Extent: 5.50 Acres | Total Plots: 42 Approved House Plots",
                "confidence": 0.90,
                "label": "Total Extent & Number of Plots",
                "box": {"x_pct": 5.0, "y_pct": 32.0, "w_pct": 85.0, "h_pct": 3.8}
            },
            "osr_park_gift": {
                "value": "PASS: 10% OSR Park (24,000 Sq.Ft) Gifted via Registered Gift Deed Doc 1920/2020",
                "confidence": 0.94,
                "label": "OSR Park & Road Gift Details",
                "box": {"x_pct": 5.0, "y_pct": 38.0, "w_pct": 90.0, "h_pct": 4.0}
            }
        }
    },
    "death_legal_heir": {
        "title": "Death certificate and legal hier certificate",
        "raw_text": """GOVERNMENT OF TAMIL NADU - REVENUE DEPARTMENT
DEATH CERTIFICATE & LEGAL HEIRSHIP CERTIFICATE (வாரிசுச் சான்றிதழ்)

1. DEATH CERTIFICATE:
Deceased Name: Late Mr. V. RAMAMOORTHY
Date of Death: 14th April 2023 (14-04-2023)
Death Registration No: GCC/DC/2023/04812 | Place: Chennai

2. LEGAL HEIR CERTIFICATE (VARISU):
Tahsildar Varisu Order No: TN-720230514102941 | Date: 14-05-2023
Surviving Legal Heirs:
- Smt. R. SARADHA (Age 58, Wife) [Status: Signatory / Party 1]
- Thiru. R. VIJAYAKUMAR (Age 34, Son) [Status: Signatory / Party 2]
- Selvi. R. DEEPA (Age 29, Daughter) [Status: Registered Release Deed Doc 1420/2023]
- Smt. V. MEENAKSHI (Age 82, Mother) [Status: Registered POA Doc 891/2023]

3. INHERITED TITLE AUDIT:
Heir Completeness: 100% Accounted (4 of 4 Heirs Signed / Released)
Patta Mutation Check: PASSED - Revenue Patta mutated to heirs under Tahsildar Order MUT/MYL/2023/4812 (TN Patta Passbook Act 1983).""",
        "structured": {
            "document_type": "Death certificate and legal hier certificate",
            "deceased_name": {
                "value": "Late Mr. V. RAMAMOORTHY",
                "confidence": 0.96,
                "label": "Deceased Name",
                "box": {"x_pct": 5.0, "y_pct": 14.0, "w_pct": 60.0, "h_pct": 3.8}
            },
            "death_date_reg_no": {
                "value": "Date: 14-04-2023 | Registration No: GCC/DC/2023/04812",
                "confidence": 0.94,
                "label": "Date of Death & Reg No",
                "box": {"x_pct": 5.0, "y_pct": 20.0, "w_pct": 80.0, "h_pct": 3.8}
            },
            "varisu_certificate_order": {
                "value": "Order No: TN-720230514102941 dated 14-05-2023 (Tahsildar)",
                "confidence": 0.95,
                "label": "Varisu Certificate Order No & Date",
                "box": {"x_pct": 5.0, "y_pct": 26.0, "w_pct": 85.0, "h_pct": 3.8}
            },
            "surviving_legal_heirs_list": {
                "value": "1. R. Saradha (Wife), 2. R. Vijayakumar (Son), 3. R. Deepa (Daughter), 4. V. Meenakshi (Mother)",
                "confidence": 0.93,
                "label": "Surviving Legal Heirs List",
                "box": {"x_pct": 5.0, "y_pct": 32.0, "w_pct": 90.0, "h_pct": 4.5}
            },
            "heir_completeness_check": {
                "value": "PASS: 100% Accounted (4 of 4 Heirs Signed / Release Deed / Registered POA)",
                "confidence": 0.96,
                "label": "Heir Completeness Check (100%)",
                "box": {"x_pct": 5.0, "y_pct": 38.5, "w_pct": 90.0, "h_pct": 4.0}
            },
            "patta_mutation_status": {
                "value": "PASS: Mutated to Heirs under Tahsildar Order MUT/MYL/2023/4812 (TN Act 1983)",
                "confidence": 0.95,
                "label": "Patta Mutation Status (TN Act 1983)",
                "box": {"x_pct": 5.0, "y_pct": 44.5, "w_pct": 90.0, "h_pct": 4.0}
            }
        }
    },
    "loan_docs": {
        "title": "Loan documents (if applicable)",
        "raw_text": """MEMORANDUM OF DEPOSIT OF TITLE DEEDS (MODT) / HOUSING LOAN
Lending Bank: State Bank of India, RACPC South Chennai
Borrower Name: Mr. K. RAJENDRAN | Co-Borrower: Mrs. R. KAVITHA
Loan Account No: SBI/HL/2012/894102 | Sanctioned Amount: Rs. 25,00,000/-
Security: Simple Mortgage via Deposit of Title Deed Doc 1820/2008 for Property at T.S. No. 142/2A, Velachery
MODT Document Number: Registered Doc No. 2910 / 2012 at SRO Velachery
Discharge Status: FULLY PAID & DISCHARGED via Bank NOC & Receipt Doc No. 640/2018 (Title Cleared).""",
        "structured": {
            "document_type": "Loan documents (if applicable)",
            "lending_bank": {
                "value": "State Bank of India (RACPC South Chennai)",
                "confidence": 0.94,
                "label": "Lending Bank / Institution",
                "box": {"x_pct": 5.0, "y_pct": 14.0, "w_pct": 75.0, "h_pct": 3.8}
            },
            "borrower_names": {
                "value": "Mr. K. RAJENDRAN & Mrs. R. KAVITHA (Co-Borrower)",
                "confidence": 0.92,
                "label": "Borrower & Co-Borrower Names",
                "box": {"x_pct": 5.0, "y_pct": 20.0, "w_pct": 80.0, "h_pct": 3.8}
            },
            "loan_account_amount": {
                "value": "A/C: SBI/HL/2012/894102 | Sanctioned Loan: Rs. 25,00,000/-",
                "confidence": 0.93,
                "label": "Loan Account & Sanctioned Amount",
                "box": {"x_pct": 5.0, "y_pct": 26.0, "w_pct": 85.0, "h_pct": 3.8}
            },
            "security_modt_details": {
                "value": "Deposit of Original Mother Deed Doc 1820/2008 for T.S. No. 142/2A, Velachery",
                "confidence": 0.90,
                "label": "Security / MODT Details",
                "box": {"x_pct": 5.0, "y_pct": 32.0, "w_pct": 90.0, "h_pct": 3.8}
            },
            "modt_doc_no_sro": {
                "value": "Registered MODT Doc No. 2910 / 2012 at SRO Velachery",
                "confidence": 0.94,
                "label": "MODT Doc No, Year & SRO",
                "box": {"x_pct": 5.0, "y_pct": 38.0, "w_pct": 85.0, "h_pct": 3.8}
            },
            "noc_discharge_status": {
                "value": "CLEARED: Discharge Receipt Doc No. 640/2018 registered (Full NOC Issued)",
                "confidence": 0.96,
                "label": "NOC / Discharge Status",
                "box": {"x_pct": 5.0, "y_pct": 44.0, "w_pct": 90.0, "h_pct": 4.0}
            }
        }
    },
    "tslr": {
        "title": "TSLR document (Town Survey Land Record)",
        "raw_text": """District : Chengalpattu Taluk : Tambaram Town : Tambaram Ward : Ward-CTambaram
URB/35/05/003/003/0027/2/0
Sl.No 1
2/0
357/A,B-/358/A,B-359A,361/364/366/368/1,2-3691-2,370/1-357/1A-1B/358/1A1B,393/394/395/396/397
Ward-CTambaram, Block 0027
Door No : -
Name : -
Government (சர்க்கார் / அரசு)
Government Poramboke (புறம்போக்கு)
30 Hectare, 14 Are(s), 5.0 Sq.Meter(s) [~ 301,405.0 Sq.M / 3,244,293.3 Sq.Ft (1,351.79 Grounds)]
Municipal=-, Govt=0.00
TR DT: 21-01-2020
SARAVANNAN V — Tahsildar — தாம்பரம் வட்டம் / Tambaram, செங்கல்பட்டு மாவட்டம் / Chengalpattu
21-01-2020
16-09-2026 at 08:05:24 AM
https://eservices.tn.gov.in""",
        "structured": {
            "document_type": "TSLR document",
            "district": {
                "value": "Chengalpattu (செங்கல்பட்டு)",
                "confidence": 0.98,
                "label": "District (மாவட்டம்)"
            },
            "taluk": {
                "value": "Tambaram (தாம்பரம்)",
                "confidence": 0.98,
                "label": "Taluk (வட்டம்)"
            },
            "town_village": {
                "value": "Tambaram (தாம்பரம்)",
                "confidence": 0.98,
                "label": "Town / Revenue Village (நகரம் / வருவாய் கிராமம்)"
            },
            "ward": {
                "value": "Ward-CTambaram",
                "confidence": 0.98,
                "label": "Ward (வார்டு)"
            },
            "digital_signature_authority": {
                "value": "SARAVANNAN V — Tahsildar — தாம்பரம் வட்டம் / Tambaram, செங்கல்பட்டு மாவட்டம் / Chengalpattu",
                "confidence": 0.98,
                "label": "Digital Signature Authority (வட்டாட்சியர் / மின் கையொப்பம்)"
            },
            "signature_date": {
                "value": "21-01-2020",
                "confidence": 0.98,
                "label": "Signature Date (கையொப்ப நாள்)"
            },
            "portal_reference": {
                "value": "URB/35/05/003/003/0027/2/0",
                "confidence": 0.99,
                "label": "eServices Verification Ref No (சரிபார்ப்பு குறிப்பு எண்)"
            },
            "certificate_printed_date": {
                "value": "16-09-2026 at 08:05:24 AM",
                "confidence": 0.95,
                "label": "Certificate Print Date & Time (அச்சிடப்பட்ட நாள்)"
            },
            "verification_portal": {
                "value": "https://eservices.tn.gov.in",
                "confidence": 0.99,
                "label": "Verification Portal (சரிபார்ப்பு இணையதளம்)"
            },
            "serial_no": {
                "value": "1",
                "confidence": 0.95,
                "label": "Sl.No (வரிசை எண்)"
            },
            "survey_number": {
                "value": "2/0",
                "confidence": 0.98,
                "label": "Town Survey Number / S.No (நகர புல எண் / T.S. No)"
            },
            "old_survey_number": {
                "value": "357/A,B-/358/A,B-359A,361/364/366/368/1,2-3691-2,370/1-357/1A-1B/358/1A1B,393/394/395/396/397",
                "confidence": 0.96,
                "label": "Old Survey Number (பழைய சர்வே எண் / O.Sur No & Letter)"
            },
            "ward_block": {
                "value": "Ward-CTambaram, Block 0027",
                "confidence": 0.96,
                "label": "Ward + Block (வார்டு & பிளாக்)"
            },
            "municipal_door_no": {
                "value": "Not Recorded (-)",
                "confidence": 0.90,
                "label": "Municipal Door No. (நகராட்சி கதவு எண்)"
            },
            "owner_name": {
                "value": "Not Recorded (-) (பதிவு செய்யப்படவில்லை)",
                "confidence": 0.97,
                "label": "Name (உரிமையாளர் பெயர் / Adangal Holder)"
            },
            "tenure_type": {
                "value": "Government (சர்க்கார் / அரசு)",
                "confidence": 0.98,
                "label": "Tenure Type (நில உரிமை முறை: Govt/Mitta/Zamindari/Inam)"
            },
            "land_classification": {
                "value": "Government Poramboke (புறம்போக்கு)",
                "confidence": 0.98,
                "label": "Land Classification (நில வகைப்பாடு: Dry/Wet/Promboke/House-site)"
            },
            "current_land_use": {
                "value": "Not Recorded (-) (பதிவு செய்யப்படவில்லை)",
                "confidence": 0.90,
                "label": "Current Land Use (தற்போதைய பயன்பாடு: How holding is utilised)"
            },
            "extent": {
                "value": "30 Hectare, 14 Are(s), 5.0 Sq.Meter(s) [~ 301,405.0 Sq.M / 3,244,293.3 Sq.Ft (1,351.79 Grounds)]",
                "confidence": 0.98,
                "label": "Extent By Town Survey (நில விஸ்தீரணம்: Hectare, Ares, Sq.Meter)"
            },
            "assessment": {
                "value": "Municipal=-, Govt=0.00",
                "confidence": 0.95,
                "label": "Assessment (தீர்வை / நில வரி: Municipal, Govt.)"
            },
            "municipal_register": {
                "value": "Not Recorded (-)",
                "confidence": 0.90,
                "label": "Municipal Register (நகராட்சி பதிவேடு)"
            },
            "remarks": {
                "value": "TR DT: 21-01-2020",
                "confidence": 0.98,
                "label": "Remarks (குறிப்புகள் / மாறுதல் உத்தரவு)"
            },
            "multi_page_audit": {
                "value": "2 Pages Total — Page 2 Verified — eServices Official 2D Barcode & Portal Attestation (Reference: URB/35/05/003/003/0027/2/0)",
                "confidence": 0.99,
                "label": "Multi-Page & Survey Map Audit (பக்க & வரைபட சரிபார்ப்பு)"
            },
            "checklist": [
                {
                    "item": "Adangal Holding & Owner Verification",
                    "title": "Adangal Holding & Owner Verification (உரிமையாளர் சரிபார்ப்பு)",
                    "status": "PASSED",
                    "detail": "Government Poramboke Land (சர்க்கார் புறம்போக்கு). Vested with Government of Tamil Nadu; private Adangal holding not applicable."
                },
                {
                    "item": "Town Survey & Old Revenue Survey Correlation",
                    "title": "Town Survey & Old Revenue Survey Correlation (புல எண் இணைப்பு)",
                    "status": "PASSED",
                    "detail": "Town Survey No: 2/0, Old Revenue Survey No: 357/A,B-/358/A,B-359A,361/364/366/368/1,2-3691-2,370/1-357/1A-1B/358/1A1B,393/394/395/396/397."
                },
                {
                    "item": "Tenure Type Verification",
                    "title": "Tenure Type Verification (நில உரிமை உறுதி)",
                    "status": "PASSED",
                    "detail": "Tenure: Government (சர்க்கார் / அரசு)."
                },
                {
                    "item": "Land Classification & Use",
                    "title": "Land Classification & Use (மனை வகைப்பாடு)",
                    "status": "PASSED",
                    "detail": "Classification: 'Government Poramboke (புறம்போக்கு)', Use: 'Not Recorded (-)'."
                },
                {
                    "item": "Digital Signature & eServices Validity",
                    "title": "Digital Signature & eServices Validity (மின் கையொப்பம்)",
                    "status": "PASSED",
                    "detail": "Signed by SARAVANNAN V on 21-01-2020. Ref: URB/35/05/003/003/0027/2/0."
                },
                {
                    "item": "Multi-Page & Survey Map Audit",
                    "title": "Multi-Page & Survey Map Audit (பக்க & வரைபட சரிபார்ப்பு)",
                    "status": "PASSED",
                    "detail": "2 Pages Total — Page 2 Verified — eServices Official 2D Barcode & Portal Attestation (Reference: URB/35/05/003/003/0027/2/0)."
                }
            ]
        }
    }
}

MULTI_DOC_BUNDLES = {
    "standard_sale_bundle": {
        "bundle_id": "standard_sale_bundle",
        "title": "Standard Chennai Property Sale Verification Bundle",
        "description": "Cross-verifies Sale deed / title deed (Apartment UDS) ↔ Patta document (TSLR) ↔ EC ↔ Parent docs.",
        "documents": {
            "sale_deed": SAMPLE_DOCUMENTS["sale_deed"]["structured"],
            "patta": {
                "pattadhar_name": "Mr. K. RAJENDRAN",
                "survey_number": "T.S. No. 142/2A",
                "tslr_town_survey_no": "T.S. No. 142/2A",
                "extent": "445.93 Sq.Meters (4800 Sq.Ft)",
                "village_taluk_district": "Velachery Town / Chennai Corporation",
                "tslr_ward_block": "Ward E, Block 14",
                "tslr_town": "Velachery Town"
            },
            "ec": SAMPLE_DOCUMENTS["ec"]["structured"],
            "parent_docs": SAMPLE_DOCUMENTS["parent_docs"]["structured"]
        }
    },
    "rural_patta_bundle": {
        "bundle_id": "rural_patta_bundle",
        "title": "Rural Agricultural Patta 1092 Verification Bundle",
        "description": "Cross-verifies Rural Patta 1092 ↔ Thiruvarur Taluk ↔ EC ↔ Parent docs.",
        "documents": {
            "sale_deed": {
                "executant_seller": "Pakkirisamy (S/o Govindarasu)",
                "survey_number": "30-3B, 30-5B",
                "extent_area": "0.40.00 Hectares (43,056 Sq.Ft)",
                "previous_document_reference": "Doc No. 1092 / 2024"
            },
            "patta": SAMPLE_DOCUMENTS["patta"]["structured"],
            "ec": SAMPLE_DOCUMENTS["ec"]["structured"],
            "parent_docs": SAMPLE_DOCUMENTS["parent_docs"]["structured"]
        }
    },
    "inherited_property_bundle": {
        "bundle_id": "inherited_property_bundle",
        "title": "Death certificate and legal hier certificate (Varisu) Track",
        "description": "Inheritance verification: Death Certificate ↔ Varisu (4 Heirs) ↔ Patta Mutation Gate ↔ Sale Deed Signatories.",
        "inheritance_data": {
            "death_certificate": {"deceased_name": "Late Mr. V. Ramamoorthy", "date_of_death": "14-04-2023", "death_reg_no": "GCC/DC/2023/04812"},
            "legal_heir_certificate": {
                "deceased_name": "Late Mr. V. Ramamoorthy",
                "legal_heirs_list": [
                    {"name": "Smt. R. SARADHA", "relationship": "Wife", "age": "58", "status": "Signatory / Party 1"},
                    {"name": "Thiru. R. VIJAYAKUMAR", "relationship": "Son", "age": "34", "status": "Signatory / Party 2"},
                    {"name": "Selvi. R. DEEPA", "relationship": "Daughter", "age": "29", "status": "Registered Release Deed Doc 1420/2023"},
                    {"name": "Smt. V. MEENAKSHI", "relationship": "Mother", "age": "82", "status": "Registered POA Holder Doc 891/2023"}
                ]
            },
            "original_patta_owner": "Mr. V. Ramamoorthy",
            "partition_deed": {"allotted_share_extent": "1200 Sq.Ft (50% share)", "doc_no": "890/2023"},
            "selling_extent": "1200 Sq.Ft",
            "patta_mutation": {"mutation_status": "MUTATED TO HEIRS (Order No. MUT/MYL/2023/4812)", "hard_gate_passed": True},
            "sale_deed_signatories": ["Smt. R. Saradha", "Thiru. R. Vijayakumar"]
        }
    },
    "fraud_alert_bundle": {
        "bundle_id": "fraud_alert_bundle",
        "title": "High Risk Demo: Government Poramboke Fraud Alert",
        "description": "Catches fraudulent conveyance attempt with active litigation and mismatched extents.",
        "documents": {
            "sale_deed": {
                "executant_seller": "Mr. Fake Seller Kumar",
                "survey_number": "89/1 (Waterbody Poramboke)",
                "extent_area": "5000 Sq.Ft",
                "previous_document_reference": "Forged Deed 999/2010"
            },
            "patta": {
                "pattadhar_names": ["Government of Tamil Nadu - Revenue Dept"],
                "survey_and_subdivision": "89/1",
                "land_classification": "Government Poramboke (ஏரி புறம்போக்கு)",
                "extent_area": "2400 Sq.Ft"
            },
            "ec": {
                "form_type": "Form 15 (Active Court Attachment Found)",
                "encumbrance_status": "Active Court Attachment in O.S. 412/2021",
                "total_entries": 3
            },
            "parent_docs": {
                "last_5_years_validation": "FAILED: Fake / Broken lineage"
            }
        }
    }
}
