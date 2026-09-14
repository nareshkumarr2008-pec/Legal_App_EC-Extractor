# -*- coding: utf-8 -*-
"""
Property Title & Encumbrance Verification Engine.

Filters and verifies specific property details (Survey Number, Taluk, City/Village,
District, Extent, Boundaries, Flat Name, Door Number, Owner Name) against all registered
transactions in Encumbrance Certificates (EC Form 15) and title documents.

Produces structured verification insights:
1. Matching entries count & ratio
2. Current / relevant legal title holder
3. Target user's related transaction
4. Loan & mortgage history
5. Loan closure status (Closed / Discharged vs Open / Active Lien)
6. Court cases, attachments, and decrees
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from app.cross_checker import CrossVerificationEngine
from app.translator import transliterate_tamil_text, normalize_tamil_visual_order


def _clean_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip()


def _normalize_tokens(text: str) -> List[str]:
    clean = re.sub(r'[^a-zA-Z0-9\u0B80-\u0BFF\s]', ' ', text.lower())
    return [t for t in clean.split() if len(t) > 1]


def _extract_flat_token(text: str) -> Optional[str]:
    """Extract flat identifier like 3B, F-2, Flat 12 from text."""
    m = re.search(r'(?:flat|apartment|unit|அடுக்குமாடி)[^\w\n]*([A-Za-z0-9\-]+)', text, re.I)
    if m:
        return m.group(1).upper()
    m2 = re.search(r'\b([A-Z]\d{1,3}|\d{1,3}[A-Z])\b', text)
    if m2:
        return m2.group(1).upper()
    return None


def _extract_survey_token(text: str) -> Optional[str]:
    """Normalize survey number e.g. 142/2A, 142/2, 249/3A."""
    m = re.search(r'\b(\d{1,5}(?:/[A-Za-z0-9\-]+)?)\b', text)
    if m:
        return m.group(1).upper()
    return None


class PropertyFilterEngine:
    """Verifies and filters property parameters against document transactions."""

    @staticmethod
    def filter_and_verify(criteria: Dict[str, Any], extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        fields = extraction_data.get("fields", {})
        
        # 1. Gather all transactions
        raw_tx_list = []
        if "transactions_table" in fields and isinstance(fields["transactions_table"], dict):
            raw_tx_list = fields["transactions_table"].get("value", [])
        elif "transactions" in extraction_data:
            raw_tx_list = extraction_data.get("transactions", [])
        
        if not isinstance(raw_tx_list, list):
            raw_tx_list = []

        # Target input parameters
        target_sy = _clean_str(criteria.get("survey_no")).upper()
        target_taluk = _clean_str(criteria.get("taluk")).lower()
        target_city = _clean_str(criteria.get("city_village")).lower()
        target_district = _clean_str(criteria.get("district")).lower()
        target_extent = _clean_str(criteria.get("extent")).lower()
        target_boundary = _clean_str(criteria.get("boundary")).lower()
        target_flat = _clean_str(criteria.get("flat_name")).upper()
        target_door = _clean_str(criteria.get("door_no")).lower()
        target_owner = _clean_str(criteria.get("owner_name")).lower()

        # Document-level context
        doc_sy = _clean_str(fields.get("survey_searched", {}).get("value", "")).upper()
        doc_village = _clean_str(fields.get("village", {}).get("value", "")).lower()
        doc_taluk = _clean_str(fields.get("taluk", {}).get("value", "")).lower()
        doc_district = _clean_str(fields.get("district", {}).get("value", "")).lower()

        matched_transactions: List[Dict[str, Any]] = []
        unmatched_transactions: List[Dict[str, Any]] = []

        norm_target_sy = CrossVerificationEngine.normalize_survey_no(target_sy)
        target_extent_sqft = CrossVerificationEngine.normalize_extent_to_sqft(target_extent) if target_extent else None

        for idx, tx in enumerate(raw_tx_list):
            tx_copy = dict(tx)
            tx_sr = tx_copy.get("sr") or (idx + 1)
            doc_no = tx_copy.get("doc_no") or tx_copy.get("doc_no_year") or "-"
            nature = tx_copy.get("nature") or ""
            executants = tx_copy.get("executants") or ""
            claimants = tx_copy.get("claimants") or ""
            remarks = tx_copy.get("remarks") or tx_copy.get("document_remarks") or ""
            pr_num = tx_copy.get("pr_number") or tx_copy.get("pr_numbers") or ""
            schedules = tx_copy.get("schedules") or []

            combined_search_text = f"{doc_no} {nature} {executants} {claimants} {remarks} {pr_num} {doc_sy} {doc_village} {doc_taluk}".lower()
            if schedules:
                for sch in schedules:
                    combined_search_text += f" {sch.get('survey_no', '')} {sch.get('extent', '')} {sch.get('plot_no', '')} {sch.get('boundaries', '')}"

            match_reasons: List[str] = []
            is_match = False

            # Check 1: Survey Number
            if target_sy:
                norm_tx_sy = CrossVerificationEngine.normalize_survey_no(combined_search_text)
                if (norm_target_sy and norm_target_sy in norm_tx_sy) or (target_sy.lower() in combined_search_text):
                    match_reasons.append(f"Survey No {target_sy} matched")
                    is_match = True
            else:
                # If no survey specified, doc-level survey counts as context
                is_match = True

            # Check 2: Flat Name / Number
            if target_flat:
                norm_flat = re.sub(r'^(?:FLAT|APARTMENT|UNIT|NO\.?)\s*', '', target_flat, flags=re.I).strip()
                flat_pattern = r'(?:\b|Flat\s*|Unit\s*|எண்\s*)' + re.escape(norm_flat) + r'\b'
                if re.search(flat_pattern, combined_search_text, re.I) or norm_flat.lower() in combined_search_text:
                    match_reasons.append(f"Flat/Unit '{target_flat}' matched")
                    is_match = True
                elif target_flat and any(term in combined_search_text for term in ["flat", "apartment", "unit"]):
                    # Context match if property type is apartment
                    match_reasons.append("Apartment/Flat transaction")

            # Check 3: Door / Plot Number
            if target_door:
                norm_door = re.sub(r'^(?:PLOT|DOOR|D\.?NO\.?|NO\.?)\s*', '', target_door, flags=re.I).strip()
                if norm_door and norm_door in combined_search_text:
                    match_reasons.append(f"Plot/Door '{target_door}' matched")
                    is_match = True

            # Check 4: Extent / Area
            if target_extent:
                if target_extent in combined_search_text:
                    match_reasons.append(f"Extent '{target_extent}' matched")
                    is_match = True
                elif target_extent_sqft:
                    tx_extent_sqft = CrossVerificationEngine.normalize_extent_to_sqft(remarks)
                    if tx_extent_sqft and abs(tx_extent_sqft - target_extent_sqft) / target_extent_sqft < 0.15:
                        match_reasons.append(f"Extent ~{int(tx_extent_sqft)} sq.ft matched")
                        is_match = True

            # Check 5: Boundary details
            if target_boundary:
                b_tokens = [t for t in _normalize_tokens(target_boundary) if t not in ["north", "south", "east", "west", "road", "street", "வடக்கில்", "தெற்கில்", "கிழக்கில்", "மேற்கில்"]]
                matched_b = [t for t in b_tokens if t in combined_search_text]
                if len(matched_b) >= 2:
                    match_reasons.append(f"Boundary features matched ({', '.join(matched_b[:3])})")
                    is_match = True

            # Check 6: Owner Name
            has_owner_match = False
            if target_owner:
                norm_target_owner = CrossVerificationEngine.normalize_name(target_owner)
                norm_exec = CrossVerificationEngine.normalize_name(executants)
                norm_claim = CrossVerificationEngine.normalize_name(claimants)

                owner_tokens = [t for t in norm_target_owner.split() if len(t) > 2]
                if norm_target_owner and (norm_target_owner in norm_exec or norm_target_owner in norm_claim):
                    has_owner_match = True
                elif owner_tokens and any(t in norm_exec or t in norm_claim for t in owner_tokens):
                    has_owner_match = True

                if has_owner_match:
                    match_reasons.append(f"Owner '{target_owner}' identified in parties")
                    is_match = True

            tx_copy["match_reasons"] = match_reasons
            tx_copy["is_property_match"] = is_match
            tx_copy["has_owner_match"] = has_owner_match

            # If user provided no specific filter parameters, all transactions are included
            if not target_sy and not target_flat and not target_door and not target_extent and not target_owner:
                tx_copy["is_property_match"] = True
                tx_copy["match_reasons"] = ["Full Search Window Entry"]
                matched_transactions.append(tx_copy)
            elif is_match:
                matched_transactions.append(tx_copy)
            else:
                unmatched_transactions.append(tx_copy)

        # ------------------------------------------------------------------
        # 2. Identify Current / Relevant Title Holder
        # ------------------------------------------------------------------
        # Trace conveyances in chronological order (or table sequence)
        conveyance_types = [
            "conveyance", "sale", "settlement", "gift", "partition", "release",
            "கிரைய", "செட்டில்மென்ட்", "பாகப்பிரிவினை", "தான"
        ]

        title_chain: List[Dict[str, Any]] = []
        current_holder: Optional[Dict[str, Any]] = None

        pool_for_title = matched_transactions if matched_transactions else raw_tx_list

        for tx in pool_for_title:
            nat = (tx.get("nature") or "").lower()
            if any(k in nat for k in conveyance_types):
                claimants_clean = tx.get("claimants") or "-"
                executants_clean = tx.get("executants") or "-"
                title_event = {
                    "doc_no": tx.get("doc_no") or tx.get("doc_no_year") or "-",
                    "date": tx.get("date") or tx.get("registration_date") or "-",
                    "nature": tx.get("nature") or "-",
                    "buyer_holder": claimants_clean,
                    "seller_prior": executants_clean,
                    "consideration": tx.get("consideration") or "-",
                    "sr": tx.get("sr") or 1
                }
                title_chain.append(title_event)
                current_holder = title_event

        # ------------------------------------------------------------------
        # 3. User's Related Transaction
        # ------------------------------------------------------------------
        user_related_tx: Optional[Dict[str, Any]] = None
        if target_owner:
            norm_target_owner = CrossVerificationEngine.normalize_name(target_owner)
            for tx in pool_for_title:
                norm_exec = CrossVerificationEngine.normalize_name(tx.get("executants") or "")
                norm_claim = CrossVerificationEngine.normalize_name(tx.get("claimants") or "")
                
                role = None
                if norm_target_owner and norm_target_owner in norm_claim:
                    role = "Claimant / Buyer / Beneficiary"
                elif norm_target_owner and norm_target_owner in norm_exec:
                    role = "Executant / Seller / Mortgagor"
                elif any(t in norm_claim for t in [t for t in norm_target_owner.split() if len(t) > 2]):
                    role = "Claimant / Buyer (Fuzzy match)"
                elif any(t in norm_exec for t in [t for t in norm_target_owner.split() if len(t) > 2]):
                    role = "Executant / Seller (Fuzzy match)"

                if role:
                    user_related_tx = {
                        "doc_no": tx.get("doc_no") or tx.get("doc_no_year") or "-",
                        "date": tx.get("date") or tx.get("registration_date") or "-",
                        "nature": tx.get("nature") or "-",
                        "role": role,
                        "matched_name": target_owner,
                        "executants": tx.get("executants") or "-",
                        "claimants": tx.get("claimants") or "-",
                        "consideration": tx.get("consideration") or "-",
                        "remarks": tx.get("remarks") or ""
                    }
                    break

        # ------------------------------------------------------------------
        # 4 & 5. Loan / Mortgage Details & Loan Closure Status
        # ------------------------------------------------------------------
        mortgage_types = [
            "mortgage", "modt", "deposit of title", "charge", "hypothecation", "அடமான"
        ]
        discharge_types = [
            "receipt", "discharge", "release", "ரசீது", "விடுதலை"
        ]

        mortgages: List[Dict[str, Any]] = []
        discharges: List[Dict[str, Any]] = []

        for tx in pool_for_title:
            nat = (tx.get("nature") or "").lower()
            if any(k in nat for k in mortgage_types) and not any(k in nat for k in discharge_types):
                mortgages.append(tx)
            elif any(k in nat for k in discharge_types):
                discharges.append(tx)

        loan_records: List[Dict[str, Any]] = []
        open_loans_count = 0
        closed_loans_count = 0

        for m_tx in mortgages:
            m_doc = m_tx.get("doc_no") or m_tx.get("doc_no_year") or "-"
            m_date = m_tx.get("date") or m_tx.get("registration_date") or "-"
            m_lender = m_tx.get("claimants") or "Bank / Financial Institution"
            m_borrower = m_tx.get("executants") or "-"
            m_amount = m_tx.get("consideration") or "-"

            # Correlate with discharge deeds
            matching_discharge: Optional[Dict[str, Any]] = None
            for d_tx in discharges:
                d_pr = d_tx.get("pr_number") or d_tx.get("pr_numbers") or ""
                d_remarks = d_tx.get("remarks") or ""
                
                # Check PR number correlation (exact or sub-token match)
                if m_doc != "-" and (m_doc in d_pr or m_doc in d_remarks):
                    matching_discharge = d_tx
                    break

                # Correlate via lender name match
                lender_tokens = [t for t in _normalize_tokens(m_lender) if t not in ["bank", "ltd", "limited", "of", "india"]]
                d_claimants = d_tx.get("claimants") or ""
                d_executants = d_tx.get("executants") or ""
                d_parties = f"{d_claimants} {d_executants}".lower()

                if lender_tokens and any(lt in d_parties for lt in lender_tokens):
                    matching_discharge = d_tx
                    break

            if matching_discharge:
                closed_loans_count += 1
                loan_records.append({
                    "status": "CLOSED",
                    "status_label": "Closed / Discharged (ரசீது மூலம் விடுதலை செய்யப்பட்டது)",
                    "is_closed": True,
                    "mortgage_doc_no": m_doc,
                    "mortgage_date": m_date,
                    "lender": m_lender,
                    "borrower": m_borrower,
                    "amount": m_amount,
                    "discharge_doc_no": matching_discharge.get("doc_no") or matching_discharge.get("doc_no_year") or "-",
                    "discharge_date": matching_discharge.get("date") or matching_discharge.get("registration_date") or "-",
                    "discharge_nature": matching_discharge.get("nature") or "Receipt / Discharge",
                    "remarks": f"Verified: Registered discharge receipt {matching_discharge.get('doc_no')} recorded on {matching_discharge.get('date')}."
                })
            else:
                open_loans_count += 1
                loan_records.append({
                    "status": "OPEN",
                    "status_label": "Active / Unreleased Lien (நிலுவையில் உள்ள அடமானம்)",
                    "is_closed": False,
                    "mortgage_doc_no": m_doc,
                    "mortgage_date": m_date,
                    "lender": m_lender,
                    "borrower": m_borrower,
                    "amount": m_amount,
                    "discharge_doc_no": "-",
                    "discharge_date": "-",
                    "discharge_nature": "-",
                    "remarks": f"Warning: Mortgage Doc {m_doc} registered with {m_lender} has NO corresponding discharge receipt in this search window."
                })

        # ------------------------------------------------------------------
        # 6. Court Case / Court Order Details
        # ------------------------------------------------------------------
        court_keywords = [
            "court", "attachment", "injunction", "decree", "lis pendens",
            "o.s.", "e.p.", "c.s.", "w.p.", "suit", "stay", "order",
            "நீதிமன்ற", "பற்று", "தடை", "வழக்கு"
        ]

        court_cases: List[Dict[str, Any]] = []
        for tx in pool_for_title:
            nat = (tx.get("nature") or "").lower()
            rem = (tx.get("remarks") or "").lower()
            combined = f"{nat} {rem}"

            matched_ck = [k for k in court_keywords if k in combined]
            if matched_ck:
                court_cases.append({
                    "doc_no": tx.get("doc_no") or tx.get("doc_no_year") or "-",
                    "date": tx.get("date") or tx.get("registration_date") or "-",
                    "nature": tx.get("nature") or "-",
                    "details": tx.get("remarks") or tx.get("nature") or "Court instrument recorded",
                    "keywords": matched_ck
                })

        # Final structured payload
        total_entries_count = len(raw_tx_list)
        matched_count = len(matched_transactions)

        return {
            "status": "success",
            "criteria_used": {
                "survey_no": target_sy,
                "taluk": target_taluk,
                "city_village": target_city,
                "district": target_district,
                "extent": target_extent,
                "boundary": target_boundary,
                "flat_name": target_flat,
                "door_no": target_door,
                "owner_name": target_owner
            },
            "summary": {
                "total_entries": total_entries_count,
                "matched_entries_count": matched_count,
                "unmatched_entries_count": len(unmatched_transactions),
                "match_percentage": round((matched_count / total_entries_count * 100), 1) if total_entries_count > 0 else 0,
                "current_holder_name": current_holder["buyer_holder"] if current_holder else "Not Determined / Clear Nil",
                "user_transaction_found": bool(user_related_tx),
                "total_loans_found": len(loan_records),
                "open_loans_count": open_loans_count,
                "closed_loans_count": closed_loans_count,
                "has_active_loans": (open_loans_count > 0),
                "court_cases_count": len(court_cases),
                "has_court_orders": (len(court_cases) > 0)
            },
            "current_holder": current_holder,
            "title_chain": title_chain,
            "user_related_transaction": user_related_tx,
            "loan_records": loan_records,
            "court_cases": court_cases,
            "matched_transactions": matched_transactions,
            "unmatched_transactions": unmatched_transactions
        }
